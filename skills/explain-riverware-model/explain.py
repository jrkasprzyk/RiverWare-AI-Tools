#!/usr/bin/env python3
"""explain.py — extract a narratable skeleton from a RiverWare .mdl and/or .rls.

RiverWare files are big and machine-oriented (a .mdl is a Tcl script; a .rls is
RPL text). This does NOT try to reproduce the file — it pulls out the structure a
human narrator needs: objects, their selected simulation methods, their slot
inventory, the rule-curve tables, and the ruleset's policy-group / rule tree with
the RPL bodies. Feed the output to an agent (see SKILL.md) that turns it into prose.

Usage:
    python explain.py model.mdl                 # model skeleton
    python explain.py ruleset.rls               # ruleset skeleton
    python explain.py model.mdl ruleset.rls     # both, in one digest
    python explain.py model.mdl --json          # machine-readable
    python explain.py model.mdl --annotations   # annotation inventory

Order of the two file args does not matter; extension decides which parser runs.

--annotations swaps the narrative digest for an inventory of every place a
description could go and whether one is already there. It feeds the
annotate-riverware-model skill's propose step, which must never overwrite an
existing description. The inventory is advisory: annotate.py re-checks
occupancy itself before writing a single byte.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


# ----------------------------------------------------------------------------- .mdl
def parse_mdl(text: str) -> dict:
    lines = text.splitlines()
    out: dict = {"header": {}, "run": {}, "objects": [], "dmi": {}, "scripts": [],
                 "rpl_sets": [], "description": "", "embedded_rpl": []}

    # --- header (first comment lines) + counts + run params ---------------------
    m = re.search(r"^# RiverWare_Model (\S+)", text, re.M)
    if m:
        out["header"]["version"] = m.group(1)
    m = re.search(r"^# Created (.+)$", text, re.M)
    if m:
        out["header"]["created"] = m.group(1).strip()
    m = re.search(r"^ModelSimObjCount\s+(\d+)", text, re.M)
    if m:
        out["header"]["sim_obj_count"] = int(m.group(1))
    # $ws.runInfo runParam {start} {end} n UNIT
    m = re.search(r"\$ws\.runInfo runParam \{([^}]*)\} \{([^}]*)\} (\d+) (\w+)", text)
    if m:
        out["run"] = {"start": m.group(1), "end": m.group(2),
                      "timestep": f"{m.group(3)} {m.group(4)}"}
    # model-level description: the line is always present, empty braces when unset
    m = re.search(r"^\$ws\.Model\.FileInfo comment \{(.*)\}\s*$", text, re.M)
    if m:
        out["description"] = _clean(m.group(1))

    # --- DMI (parsed out of the embedded Catalog XML blob) ---------------------
    out["dmi"]["exec"] = re.findall(r'<execDmi name="([^"]+)" type="([^"]+)"', text)
    out["dmi"]["db"] = re.findall(r'<dbDmi datasets="[^"]*" name="([^"]+)" type="([^"]+)"', text)
    out["dmi"]["datasets"] = re.findall(r'<dataset name="([^"]+)" type="([^"]+)"', text)
    out["scripts"] = re.findall(r'<Script Name="([^"]+)"', text)
    out["rpl_sets"] = re.findall(r'rplSetName="([^"]+)" rplSetType="([^"]+)"', text)

    # --- objects ---------------------------------------------------------------
    # An object starts at:  $ws SimObj $obj {Type} ...
    # name follows at:      "$o" objAttributes {<SimObjAttributes simObjName="NAME"/>}
    obj_starts = [i for i, ln in enumerate(lines)
                  if ln.startswith("$ws SimObj $obj")]
    obj_starts.append(len(lines))
    for k in range(len(obj_starts) - 1):
        i, j = obj_starts[k], obj_starts[k + 1]
        block = lines[i:j]
        mtype = re.match(r"\$ws SimObj \$obj \{([^}]+)\}", block[0])
        obj = {"type": mtype.group(1) if mtype else "?", "name": "?",
               "description": "", "methods": [], "slots": [], "tables": []}
        slot = None  # the slot whose block we are currently inside
        for ln in block:
            m = re.search(r'simObjName="([^"]+)"', ln)
            if m:
                obj["name"] = m.group(1)
            m = re.match(r'"\$o" userDescript \{(.*)\}', ln)
            if m and m.group(1):
                obj["description"] = _clean(m.group(1))
            # sDM {category} {method} {applicability}  -- keep only real methods
            m = re.match(r'"\$o" sDM \{([^}]*)\} \{([^}]*)\}', ln)
            if m and m.group(2) not in ("None", "No Method", ""):
                obj["methods"].append({"category": m.group(1), "method": m.group(2)})
            # slot:  "$o" {SlotType} {SlotName}  -- also closes the previous slot
            m = re.match(r'"\$o" \{(\w+Slot)\} \{([^}]*)\}', ln)
            if m:
                slot = {"type": m.group(1), "name": m.group(2), "description": ""}
                obj["slots"].append(slot)
                continue
            # a slot's own description, anywhere in its block
            m = re.match(r'"\$s" userDescript \{(.*)\}', ln)
            if m and m.group(1) and slot is not None:
                slot["description"] = _clean(m.group(1))
        # rule-curve / lookup tables: pull dims + labels for Table/Periodic slots
        obj["tables"] = _extract_tables(block)
        out["objects"].append(obj)

    out["embedded_rpl"] = _extract_embedded_rpl(lines)
    return out


def _extract_embedded_rpl(lines: list[str]) -> list[dict]:
    """Pull the RPL sets serialized inside the .mdl itself.

    Each is a Tcl command whose single brace argument opens with `{RULESET\\`
    and closes on a line that is exactly `}`:

        $rsm loadedSet {RULESET\\        <- Rule Based Simulation
        $ws.GlobalRplSetMgr globalFunctionSet {RULESET\\
        $ws initRules {RULESET\\
        $resm resmRplSet {RULESET\\
        ...
        }

    The set's own name comes from the NAME field inside, not the command --
    the command only marks where the set begins.
    """
    sets: list[dict] = []
    i = 0
    while i < len(lines):
        if not lines[i].rstrip("\\").rstrip().endswith("{RULESET"):
            i += 1
            continue
        start = i
        end = start + 1
        while end < len(lines) and lines[end].strip() != "}":
            end += 1
        block = lines[start:end]
        rs = {"name": "?", "description": "", "agenda": "", "groups": []}
        for ln in block[:8]:
            s = ln.strip().rstrip("\\").strip()
            m = re.match(r'NAME\s+"(.*)";?$', s)
            if m and rs["name"] == "?":
                rs["name"] = m.group(1)
            m = re.match(r'AGENDA_ORDER\s+(\w+)', s)
            if m and not rs["agenda"]:
                rs["agenda"] = m.group(1)
            m = re.match(r'DESCRIPTION\s+"(.*)";?$', s)
            if m and not rs["description"]:
                rs["description"] = _clean(m.group(1))
        rs["groups"] = _scan_rpl_groups(block)
        sets.append(rs)
        i = end + 1
    return sets


def _extract_tables(block: list[str]) -> list[dict]:
    tables = []
    i = 0
    while i < len(block):
        m = re.match(r'"\$o" \{(TableSlot|PeriodicSlot)\} \{([^}]*)\}', block[i])
        if not m:
            i += 1
            continue
        tbl = {"name": m.group(2), "kind": m.group(1), "cols": [], "rows": 0,
               "desc": "", "sample": []}
        i += 1
        while i < len(block) and not re.match(r'"\$o" \{', block[i]) \
                and not block[i].startswith("$ws SimObj"):
            ln = block[i]
            mm = re.match(r'"\$s" setColumnLabels (.+)', ln)
            if mm:
                tbl["cols"] = re.findall(r"\{([^}]*)\}", mm.group(1))
            mm = re.match(r'"\$s" userDescript \{(.*)\}', ln)
            if mm and mm.group(1):
                tbl["desc"] = _clean(mm.group(1))
            if re.match(r'"\$s" row \d+', ln):
                tbl["rows"] += 1
                if len(tbl["sample"]) < 3:
                    vals = ln.split()[3:]  # drop '"$s" row <idx>'
                    tbl["sample"].append([_fmt_num(v) for v in vals])
            i += 1
        tables.append(tbl)
    return tables


# ----------------------------------------------------------------------------- .rls
def parse_rls(text: str) -> dict:
    out: dict = {"name": "", "description": "", "precision": "", "agenda": "",
                 "groups": []}
    m = re.search(r'NAME\s+"([^"]*)"', text)
    if m:
        out["name"] = m.group(1)
    m = re.search(r'AGENDA_ORDER\s+(\w+)', text)
    if m:
        out["agenda"] = m.group(1)
    m = re.search(r'DESCRIPTION\s+"([^"]*)"', text)
    if m:
        out["description"] = _clean(m.group(1))
    m = re.search(r'PRECISION\s+(\d+)', text)
    if m:
        out["precision"] = m.group(1)

    out["groups"] = _scan_rpl_groups(text.splitlines())
    return out


def _scan_rpl_groups(lines: list[str]) -> list[dict]:
    """Walk RPL text and pull out its POLICY_GROUP/UTILITY_GROUP -> RULE/FUNCTION tree.

    Shared by the .rls parser and the .mdl embedded-set parser. Embedded RPL
    lines carry a trailing `\\` continuation and leading indentation; both are
    handled by matching against the stripped line.
    """
    groups: list[dict] = []
    group = None
    for idx, ln in enumerate(lines):
        s = ln.strip()
        m = re.match(r'(POLICY_GROUP|UTILITY_GROUP)\s+"([^"]*)"', s)
        if m:
            group = {"kind": m.group(1), "name": m.group(2), "active": None,
                     "description": "", "items": []}
            group.update(_rpl_header_fields(lines, idx))
            groups.append(group)
            continue
        if group is not None and group.get("active") is None:
            m = re.match(r'ACTIVE\s+(TRUE|FALSE)', s)
            if m:
                group["active"] = (m.group(1) == "TRUE")
        m = re.match(r'(RULE|FUNCTION)\s+"([^"]*)"', s)
        if m and group is not None:
            item = {"kind": m.group(1), "name": m.group(2), "active": None,
                    "description": "", "notes": "", "body": ""}
            item.update(_rpl_header_fields(lines, idx))
            item["body"] = _rpl_body(lines, idx)
            group["items"].append(item)
    return groups


def _rpl_header_fields(lines: list[str], hdr_idx: int) -> dict:
    """Read the ACTIVE / DESCRIPTION / NOTES fields belonging to one RPL header.

    These sit between the header line and its BEGIN. Stopping at BEGIN matters:
    a group's own fields are followed, a few lines later, by its first rule's
    fields, and only the first match of each is the group's own.
    """
    got: dict = {}
    for look in lines[hdr_idx + 1: hdr_idx + 14]:
        s = look.strip().rstrip("\\").strip()
        if s == "BEGIN":
            break
        m = re.match(r'ACTIVE\s+(TRUE|FALSE)', s)
        if m and "active" not in got:
            got["active"] = (m.group(1) == "TRUE")
        m = re.match(r'DESCRIPTION\s+"(.*)";?$', s)
        if m and "description" not in got:
            got["description"] = _clean(m.group(1))
        m = re.match(r'NOTES\s+"(.*)";?$', s)
        if m and "notes" not in got:
            got["notes"] = _clean(m.group(1))
    return got


def _rpl_body(lines: list[str], rule_idx: int) -> str:
    """Grab the text between the first BEGIN after a RULE/FUNCTION and its END."""
    depth = 0
    started = False
    body: list[str] = []
    for ln in lines[rule_idx:]:
        s = ln.strip()
        if not started:
            if s == "BEGIN":
                started = True
                depth = 1
            continue
        if s == "BEGIN":
            depth += 1
        if s == "END":
            depth -= 1
            if depth == 0:
                break
        body.append(ln.rstrip())
    return "\n".join(l for l in body if l.strip())


# ----------------------------------------------------------------------------- helpers
def _clean(txt: str) -> str:
    return txt.replace("<br>", " ").replace("  ", " ").strip()


def _fmt_num(v: str) -> str:
    try:
        f = float(v)
        return f"{f:.2f}".rstrip("0").rstrip(".") if abs(f) < 1e7 else f"{f:.3g}"
    except ValueError:
        return v


# ----------------------------------------------------------------------------- render
def render_mdl(d: dict) -> str:
    L = []
    h, r = d["header"], d["run"]
    L.append("# MODEL SKELETON")
    L.append(f"- RiverWare version: {h.get('version', '?')}  |  saved: {h.get('created', '?')}")
    if r:
        L.append(f"- Run: {r['start']} -> {r['end']}, timestep {r['timestep']}")
    L.append(f"- Simulation objects: {h.get('sim_obj_count', len(d['objects']))}")
    if d["dmi"]["exec"] or d["dmi"]["db"]:
        L.append("\n## DMIs (data exchange)")
        for n, t in d["dmi"]["exec"]:
            L.append(f"- exec DMI `{n}` ({t})")
        for n, t in d["dmi"]["db"]:
            L.append(f"- db DMI `{n}` ({t})")
    if d["rpl_sets"]:
        L.append("\n## Embedded RPL sets")
        for n, t in d["rpl_sets"]:
            L.append(f"- {n} ({t})")
    for rs in d.get("embedded_rpl", []):
        if not rs["groups"]:
            continue
        agenda = rs["agenda"] or "?"
        note = ""
        if agenda == "ASCENDING":
            note = "  (bottom rule fires first; a rule listed higher fires later and overrides)"
        L.append(f"\n## RPL set `{rs['name']}`  --  agenda {agenda}{note}")
        prio = 0
        for g in rs["groups"]:
            inactive = "" if g.get("active", True) else "  [INACTIVE]"
            if g["kind"] == "UTILITY_GROUP":
                fns = ", ".join(it["name"] for it in g["items"])
                L.append(f"  UTILITY_GROUP `{g['name']}`{inactive}: {fns}")
                continue
            L.append(f"  POLICY_GROUP `{g['name']}`{inactive}")
            for it in g["items"]:
                prio += 1
                flag = "" if it.get("active", True) else "  [INACTIVE]"
                L.append(f"    {prio}. {it['name']}{flag}")
    L.append("\n## Objects")
    for o in d["objects"]:
        L.append(f"\n### {o['name']}  --  {o['type']}")
        if o["description"]:
            L.append(f"  desc: {o['description']}")
        if o["methods"]:
            ms = "; ".join(f"{m['category']}={m['method']}" for m in o["methods"])
            L.append(f"  selected methods: {ms}")
        if o["slots"]:
            by = {}
            for s in o["slots"]:
                by.setdefault(s["type"], []).append(s["name"])
            for t, names in by.items():
                L.append(f"  {t} ({len(names)}): {', '.join(names)}")
        for t in o["tables"]:
            cols = ", ".join(t["cols"]) if t["cols"] else "?"
            L.append(f"  TABLE `{t['name']}` [{t['kind']}] {t['rows']} rows, cols: {cols}")
            if t["desc"]:
                L.append(f"     note: {t['desc']}")
            for row in t["sample"]:
                L.append(f"     e.g. {row}")
    return "\n".join(L)


def render_annotations(d: dict) -> str:
    """Inventory of every description slot in the model and whether it is taken.

    Written for the annotate-riverware-model propose step. Described targets are
    printed with their text so a proposal never duplicates what a modeler already
    wrote; empty targets are printed as bare names, because that is all the
    propose step needs to pick candidates -- and because a large model has
    thousands of them.
    """
    L = ["# ANNOTATION INVENTORY",
         "Legend: [x] = already described, leave alone (REQ-005).  "
         "[ ] = empty, available.",
         ""]
    tally = {"filled": 0, "empty": 0}

    def mark(filled: bool) -> str:
        tally["filled" if filled else "empty"] += 1
        return "[x]" if filled else "[ ]"

    L.append("## Model description")
    L.append(f"{mark(bool(d['description']))} {d['description'] or '(empty)'}")

    L.append("\n## Objects and slots")
    for o in d["objects"]:
        L.append(f"\n### {o['name']}  --  {o['type']}")
        L.append(f"  {mark(bool(o['description']))} object: "
                 f"{o['description'] or '(empty)'}")
        described = [s for s in o["slots"] if s.get("description")]
        empty = [s for s in o["slots"] if not s.get("description")]
        for s in described:
            L.append(f"  {mark(True)} {o['name']}.{s['name']}: {s['description']}")
        if empty:
            for s in empty:
                mark(False)
            L.append(f"  [ ] {len(empty)} slots with no description: "
                     + ", ".join(s["name"] for s in empty))

    for rs in d.get("embedded_rpl", []):
        L.append(f"\n## RPL set: {rs['name']}")
        L.append(f"  {mark(bool(rs['description']))} set: "
                 f"{rs['description'] or '(empty)'}")
        for g in rs["groups"]:
            L.append(f"\n  {g['kind']} \"{g['name']}\"")
            L.append(f"    {mark(bool(g.get('description')))} group: "
                     f"{g.get('description') or '(empty)'}")
            for it in g["items"]:
                L.append(f"    {mark(bool(it.get('description')))} "
                         f"{it['kind']} \"{it['name']}\": "
                         f"{it.get('description') or '(empty)'}")

    L.append(f"\n## Totals\n- described: {tally['filled']}\n"
             f"- empty (candidates): {tally['empty']}")
    L.append("\nTarget paths for the proposal JSON:")
    L.append("- object_description  -> \"<Object>\"")
    L.append("- slot_description    -> \"<Object>.<Slot>\"")
    L.append("- rpl_description     -> \"<Set>/<Group>/<Rule or Function>\""
             " (drop trailing parts for group- and set-level fields)")
    L.append("- model_description   -> \"\" (there is only one)")
    return "\n".join(L)


def render_rls(d: dict) -> str:
    L = ["# RULESET SKELETON"]
    L.append(f"- Name: {d['name']}")
    L.append(f"- Agenda order: {d['agenda']}  |  precision: {d['precision']}")
    if d["description"]:
        L.append(f"- Description: {d['description']}")
    L.append("\nNOTE: within a policy group RiverWare evaluates rules by agenda order"
             " (ASCENDING = bottom rule first). Inactive groups/rules are dead code kept for history.")
    for g in d["groups"]:
        flag = "ACTIVE" if g["active"] else "INACTIVE"
        L.append(f"\n## {g['kind']}: {g['name']}  [{flag}]  ({len(g['items'])} items)")
        for it in g["items"]:
            iflag = "on" if it["active"] else "OFF"
            L.append(f"\n### {it['kind']}: {it['name']}  [{iflag}]")
            if it["notes"]:
                L.append(f"  notes: {it['notes']}")
            if it["body"]:
                L.append("  ```rpl")
                for bl in it["body"].splitlines():
                    L.append("  " + bl)
                L.append("  ```")
    return "\n".join(L)


# ----------------------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    as_annotations = "--annotations" in argv
    if not args:
        print(__doc__)
        return 1
    result = {}
    render = []
    for a in args:
        p = Path(a)
        if not p.exists():
            print(f"error: {a} not found", file=sys.stderr)
            return 2
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix.lower() == ".mdl":
            result["model"] = parse_mdl(text)
            render.append(render_annotations(result["model"]) if as_annotations
                          else render_mdl(result["model"]))
        elif p.suffix.lower() == ".rls":
            if as_annotations:
                print("error: --annotations applies to .mdl files; a .rls is"
                      " annotated in RiverWare's RPL editor", file=sys.stderr)
                return 2
            result["ruleset"] = parse_rls(text)
            render.append(render_rls(result["ruleset"]))
        else:
            print(f"error: {a} is not .mdl or .rls", file=sys.stderr)
            return 2
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("\n\n".join(render))
    return 0


if __name__ == "__main__":
    try:
        _code = main(sys.argv[1:])
        sys.stdout.flush()  # surface a closed pipe here, not at shutdown
    except BrokenPipeError:
        # The digest is long and gets piped into `head`, `grep -m`, or a pager
        # that exits early. Redirect stdout to devnull so the interpreter's
        # own shutdown flush cannot raise a second time and print "Exception
        # ignored" over the caller's output. A reader closing the pipe asked
        # for a truncated read, so this is a success, not a failure.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        _code = 0
    raise SystemExit(_code)
