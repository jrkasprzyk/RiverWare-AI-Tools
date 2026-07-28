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

Order of the two file args does not matter; extension decides which parser runs.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# ----------------------------------------------------------------------------- .mdl
def parse_mdl(text: str) -> dict:
    lines = text.splitlines()
    out: dict = {"header": {}, "run": {}, "objects": [], "dmi": {}, "scripts": [],
                 "rpl_sets": []}

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
            # slot:  "$o" {SlotType} {SlotName}
            m = re.match(r'"\$o" \{(\w+Slot)\} \{([^}]*)\}', ln)
            if m:
                obj["slots"].append({"type": m.group(1), "name": m.group(2)})
        # rule-curve / lookup tables: pull dims + labels for Table/Periodic slots
        obj["tables"] = _extract_tables(block)
        out["objects"].append(obj)
    return out


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

    lines = text.splitlines()
    group = None
    for idx, ln in enumerate(lines):
        s = ln.strip()
        m = re.match(r'(POLICY_GROUP|UTILITY_GROUP)\s+"([^"]*)"', s)
        if m:
            group = {"kind": m.group(1), "name": m.group(2), "active": None,
                     "items": []}
            out["groups"].append(group)
            continue
        if group is not None and group.get("active") is None:
            m = re.match(r'ACTIVE\s+(TRUE|FALSE)', s)
            if m:
                group["active"] = (m.group(1) == "TRUE")
        m = re.match(r'(RULE|FUNCTION)\s+"([^"]*)"', s)
        if m and group is not None:
            item = {"kind": m.group(1), "name": m.group(2), "active": None,
                    "notes": "", "body": ""}
            # scan a few lines ahead for this item's ACTIVE flag + NOTES
            for look in lines[idx + 1: idx + 12]:
                a = re.match(r'\s*ACTIVE\s+(TRUE|FALSE)', look)
                if a and item["active"] is None:
                    item["active"] = (a.group(1) == "TRUE")
                nn = re.match(r'\s*NOTES\s+"([^"]+)"', look)
                if nn:
                    item["notes"] = _clean(nn.group(1))
            item["body"] = _rpl_body(lines, idx)
            group["items"].append(item)
    return out


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
            render.append(render_mdl(result["model"]))
        elif p.suffix.lower() == ".rls":
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
    raise SystemExit(main(sys.argv[1:]))
