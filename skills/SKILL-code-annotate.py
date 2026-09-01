#!/usr/bin/env python3
"""annotate.py -- apply an approved annotation proposal to a RiverWare .mdl.

This is the *applier* half of the annotate-riverware-model skill. It does no
judging: it takes a JSON list of approved annotations and writes them into the
model file, refusing to touch anything that already has text.

Usage:
    python annotate.py model.mdl proposals.json              # -> model_annotated.mdl
    python annotate.py model.mdl proposals.json --in-place   # overwrite model.mdl
    python annotate.py model.mdl proposals.json --output X   # explicit destination
    python annotate.py model.mdl proposals.json --dry-run    # report only, write nothing

Proposal file: a JSON list, or an object with an "annotations" list. Each entry:

    {"target_type": "model_description",  "target": "",                "text": "..."}
    {"target_type": "object_description", "target": "Cora",            "text": "..."}
    {"target_type": "slot_description",   "target": "Cora.Max Release","text": "..."}
    {"target_type": "rpl_description",    "target": "RPL Set/Cora Rules/Irrigation",
                                          "text": "..."}
    {"target_type": "rpl_comment",        "target": "RPL Set/Cora Rules/Irrigation",
                                          "literal": "0.00000000 \"cms\"",
                                          "occurrence": 1, "text": "..."}

An rpl_description target is a path: "<Set>", "<Set>/<Group>", or
"<Set>/<Group>/<Rule or Function>". Rule names repeat across groups, so the
full path is what disambiguates them.

Design notes worth knowing before editing this file:

- The file is read and written as **bytes**. Line endings vary per model (the
  two bundled examples are CRLF and LF respectively) and normalizing them would
  rewrite every line. Applying an empty proposal list must leave the bytes
  untouched -- tests/test_annotate.py asserts exactly that.
- Occupancy is re-checked here, at apply time. The propose step's inventory
  (explain.py --annotations) is advisory; this script is what guarantees an
  existing description is never overwritten.
- Only RiverWare validates a .mdl. A clean run here is not a clean load.

See reference.md in this directory for the serialization grammar.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

TARGET_TYPES = ("model_description", "object_description", "slot_description",
                "rpl_description", "rpl_comment")

# CON-004: the text restrictions that make escaping unnecessary. See reference.md
# section 7 -- no observed RiverWare file escapes any of these, so rather than
# guess at an escaping scheme we refuse the input.
MAX_TEXT = 400
FORBIDDEN_ALL = {"{": "an opening brace", "}": "a closing brace",
                 "\\": "a backslash", "\n": "a newline", "\r": "a carriage return"}
FORBIDDEN_RPL = {'"': "a double quote (it would terminate the RPL string)"}
RPL_SURFACES = ("rpl_description", "rpl_comment")


class Applied:
    """Tally of what happened, rendered as the run summary."""

    def __init__(self) -> None:
        self.applied: list[str] = []
        self.skipped: list[str] = []
        self.missing: list[str] = []


# ----------------------------------------------------------------- validation
def validate_entry(e: dict, idx: int) -> list[str]:
    """Structural + CON-004 text checks for one proposal entry."""
    errs = []
    where = f"entry {idx}"
    tt = e.get("target_type")
    if tt not in TARGET_TYPES:
        errs.append(f"{where}: target_type {tt!r} is not one of {TARGET_TYPES}")
        return errs
    where = f"entry {idx} ({tt} {e.get('target', '')!r})"
    text = e.get("text")
    if not isinstance(text, str) or not text.strip():
        errs.append(f"{where}: 'text' must be a non-empty string")
        return errs
    if len(text) > MAX_TEXT:
        errs.append(f"{where}: text is {len(text)} characters, over the "
                    f"{MAX_TEXT}-character limit")
    bad = dict(FORBIDDEN_ALL)
    if tt in RPL_SURFACES:
        bad.update(FORBIDDEN_RPL)
    for ch, name in bad.items():
        if ch in text:
            errs.append(f"{where}: text contains {name}; not supported -- "
                        f"rewrite the sentence without it")
    if tt == "rpl_comment" and not e.get("literal"):
        errs.append(f"{where}: rpl_comment needs a 'literal' naming the numeric "
                    f"literal to attach to, e.g. '0.00000000 \"cms\"'")
    if tt != "model_description" and not e.get("target"):
        errs.append(f"{where}: 'target' is required")
    return errs


# -------------------------------------------------------------------- locating
def _find_objects(lines: list[str]) -> dict:
    """name -> {anchor, existing, slots} for every simulation object.

    'anchor' is the last line of the objAttributes block, which a new
    userDescript goes after; 'existing' is the index of a userDescript already
    there, or None.

    objAttributes has two serialized forms. Most objects get a one-liner:

        "$o" objAttributes {<SimObjAttributes simObjName="Cora"/>}

    but an object carrying custom attributes gets a multi-line brace argument,
    with the name on the *following* line:

        "$o" objAttributes { \\
        <SimObjAttributes simObjName="Aspen"> \\
         <SimObjAttribute name="Fed or NonFed" value="Nonfederal"/> \\
        </SimObjAttributes>}

    Inserting after the opening line of that second form would land inside the
    XML, so the block is walked to its closing brace.
    """
    starts = [i for i, ln in enumerate(lines)
              if ln.startswith("$ws SimObj $obj")]
    starts.append(len(lines))
    objs: dict = {}
    for k in range(len(starts) - 1):
        i, j = starts[k], starts[k + 1]
        name, anchor, existing = None, None, None
        for n in range(i, j):
            s = lines[n]
            if s.startswith('"$o" objAttributes {') and anchor is None:
                anchor = _end_of_brace_arg(lines, n, j)
                for m in range(n, anchor + 1):
                    mm = re.search(r'simObjName="([^"]+)"', lines[m])
                    if mm:
                        name = mm.group(1)
                        break
            elif re.match(r'"\$o" userDescript \{', s) and existing is None:
                existing = n
        if name is not None:
            objs[name] = {"anchor": anchor, "existing": existing,
                          "slots": _find_slots(lines, i, j)}
    return objs


def _end_of_brace_arg(lines: list[str], start: int, limit: int) -> int:
    """Index of the line closing the brace argument that opens on `start`."""
    depth = 0
    for n in range(start, limit):
        depth += lines[n].count("{") - lines[n].count("}")
        if depth <= 0:
            return n
    return start


def _find_slots(lines: list[str], i: int, j: int) -> dict:
    """Slot name -> {anchor, existing} within one object's line range."""
    heads = [n for n in range(i, j) if re.match(r'"\$o" \{\w+Slot\} \{', lines[n])]
    heads.append(j)
    slots: dict = {}
    for k in range(len(heads) - 1):
        a, b = heads[k], heads[k + 1]
        m = re.match(r'"\$o" \{\w+Slot\} \{([^}]*)\}', lines[a])
        if not m:
            continue
        # Baseline anchor is the `set s "$o.<Slot>"` line: everything after it
        # binds to this slot, so an insert there is always attributed correctly
        # even for a slot that carries no UUID.
        anchor, found_uuid, existing = a, False, None
        for n in range(a, b):
            if lines[n].startswith("set s ") and anchor == a:
                anchor = n
            elif re.match(r'"\$s" UUID \{', lines[n]) and not found_uuid:
                anchor, found_uuid = n, True
                # RiverWare emits computedByExpr between UUID and userDescript
                while (anchor + 1 < b
                       and re.match(r'"\$s" computedByExpr ', lines[anchor + 1])):
                    anchor += 1
            elif re.match(r'"\$s" userDescript \{', lines[n]) and existing is None:
                existing = n
        slots[m.group(1)] = {"anchor": anchor, "existing": existing}
    return slots


def _find_rpl(lines: list[str]) -> dict:
    """Path -> {desc_line, body} for every RPL set, group, rule and function.

    'desc_line' is the index of that item's DESCRIPTION field. 'body' is the
    (begin, end) line range of a rule/function body, used by rpl_comment.
    """
    out: dict = {}
    i = 0
    while i < len(lines):
        if not lines[i].rstrip("\r\n").rstrip("\\").rstrip().endswith("{RULESET"):
            i += 1
            continue
        end = i + 1
        while end < len(lines) and lines[end].strip() != "}":
            end += 1
        _scan_set(lines, i, end, out)
        i = end + 1
    return out


def _scan_set(lines: list[str], start: int, end: int, out: dict) -> None:
    set_name = None
    for n in range(start, min(start + 8, end)):
        m = re.match(r'NAME\s+"(.*)";', _rpl_strip(lines[n]))
        if m:
            set_name = m.group(1)
            break
    if set_name is None:
        return
    out[set_name] = {"desc_line": _desc_line(lines, start, end), "body": None}
    group = None
    for n in range(start, end):
        s = _rpl_strip(lines[n])
        m = re.match(r'(?:POLICY_GROUP|UTILITY_GROUP)\s+"(.*)";', s)
        if m:
            group = f"{set_name}/{m.group(1)}"
            out[group] = {"desc_line": _desc_line(lines, n, end), "body": None}
            continue
        m = re.match(r'(?:RULE|FUNCTION)\s+"([^"]*)"', s)
        if m and group is not None:
            out[f"{group}/{m.group(1)}"] = {
                "desc_line": _desc_line(lines, n, end),
                "body": _body_range(lines, n, end)}


def _rpl_strip(line: str) -> str:
    """Strip an embedded-RPL line down to its bare statement.

    Embedded RPL lines look like `    DESCRIPTION    "";\\` plus a line ending.
    """
    return line.rstrip("\r\n").rstrip("\\").strip()


def _desc_line(lines: list[str], hdr: int, limit: int) -> int | None:
    """Index of the DESCRIPTION belonging to the header at `hdr`.

    Stops at BEGIN: a group's fields are followed a few lines later by its first
    rule's fields, and only the first block belongs to the group.
    """
    for n in range(hdr + 1, min(hdr + 14, limit)):
        s = _rpl_strip(lines[n])
        if s == "BEGIN":
            return None
        if re.match(r'DESCRIPTION\s+"', s):
            return n
    return None


def _body_range(lines: list[str], hdr: int, limit: int) -> tuple[int, int] | None:
    """(first, last) line indices of a rule/function body, exclusive of BEGIN/END."""
    depth, begin = 0, None
    for n in range(hdr, limit):
        s = _rpl_strip(lines[n])
        if s == "BEGIN":
            depth += 1
            if depth == 1:
                begin = n + 1
        elif s == "END":
            depth -= 1
            if depth == 0:
                return (begin, n) if begin is not None else None
    return None


# --------------------------------------------------------------------- editing
def _newline(lines: list[str]) -> str:
    for ln in lines:
        if ln.endswith("\r\n"):
            return "\r\n"
        if ln.endswith("\n"):
            return "\n"
    return os.linesep


def _brace_line(prefix: str, text: str, nl: str) -> str:
    return f'"{prefix}" userDescript {{{text}}}{nl}'


def apply_entries(lines: list[str], entries: list[dict], tally: Applied) -> list[str]:
    """Compute and apply every edit. Returns the new line list.

    Edits are collected first and applied last-to-first, so that an insertion
    never shifts the index of an edit that has not happened yet.
    """
    nl = _newline(lines)
    objs = _find_objects(lines)
    rpl = _find_rpl(lines)
    edits: list[tuple[int, str, str]] = []  # (line_index, "replace"|"insert", text)

    for e in entries:
        tt, target, text = e["target_type"], e.get("target", ""), e["text"]
        label = f"{tt} {target}" if target else tt

        if tt == "model_description":
            hit = [n for n, ln in enumerate(lines)
                   if ln.startswith("$ws.Model.FileInfo comment {")]
            if not hit:
                tally.missing.append(f"{label}: no $ws.Model.FileInfo comment line")
                continue
            n = hit[0]
            cur = re.match(r'\$ws\.Model\.FileInfo comment \{(.*)\}\s*$',
                           lines[n].rstrip("\r\n"))
            if cur and cur.group(1).strip():
                tally.skipped.append(f"{label}: SKIPPED (existing text)")
                continue
            edits.append((n, "replace",
                          f"$ws.Model.FileInfo comment {{{text}}}{nl}"))
            tally.applied.append(label)

        elif tt == "object_description":
            o = objs.get(target)
            if o is None:
                tally.missing.append(f"{label}: no such object")
                continue
            if o["existing"] is not None:
                tally.skipped.append(f"{label}: SKIPPED (existing text)")
                continue
            edits.append((o["anchor"], "insert", _brace_line("$o", text, nl)))
            tally.applied.append(label)

        elif tt == "slot_description":
            obj_name, _, slot_name = target.partition(".")
            o = objs.get(obj_name)
            s = o["slots"].get(slot_name) if o else None
            if s is None:
                tally.missing.append(
                    f"{label}: no such slot" if o else f"{label}: no such object")
                continue
            if s["existing"] is not None:
                tally.skipped.append(f"{label}: SKIPPED (existing text)")
                continue
            edits.append((s["anchor"], "insert", _brace_line("$s", text, nl)))
            tally.applied.append(label)

        elif tt == "rpl_description":
            node = rpl.get(target)
            if node is None or node["desc_line"] is None:
                tally.missing.append(f"{label}: no such RPL set/group/item path")
                continue
            n = node["desc_line"]
            raw = lines[n]
            m = re.match(r'^(\s*DESCRIPTION\s+)"(.*)"(.*)$', raw.rstrip("\r\n"))
            if m is None:
                tally.missing.append(f"{label}: DESCRIPTION line not parseable")
                continue
            if m.group(2).strip():
                tally.skipped.append(f"{label}: SKIPPED (existing text)")
                continue
            edits.append((n, "replace",
                          f'{m.group(1)}"{text}"{m.group(3)}{nl}'))
            tally.applied.append(label)

        elif tt == "rpl_comment":
            node = rpl.get(target)
            if node is None or node["body"] is None:
                tally.missing.append(f"{label}: no such rule/function path")
                continue
            hit = _locate_literal(lines, node["body"], e["literal"],
                                  int(e.get("occurrence", 1)))
            if hit is None:
                tally.missing.append(
                    f"{label}: literal {e['literal']!r} occurrence "
                    f"{e.get('occurrence', 1)} not found in the body")
                continue
            n, col = hit
            raw = lines[n].rstrip("\r\n")
            if raw[col:].lstrip().startswith("COMMENTED_BY"):
                tally.skipped.append(f"{label}: SKIPPED (existing comment)")
                continue
            edits.append((n, "replace",
                          f'{raw[:col]} COMMENTED_BY "{text}"{raw[col:]}{nl}'))
            tally.applied.append(f"{label} @ {e['literal']}")

    for n, kind, new in sorted(edits, key=lambda t: t[0], reverse=True):
        if kind == "replace":
            lines[n] = new
        else:
            lines.insert(n + 1, new)
    return lines


def _locate_literal(lines: list[str], body: tuple[int, int], literal: str,
                    occurrence: int) -> tuple[int, int] | None:
    """Find the Nth occurrence of a numeric literal in a rule body.

    v1 targets numeric literals only (reference.md section 6). The literal
    includes its unit string, e.g. `0.00000000 "cms"`, because RiverWare treats
    the value and its unit as one token pair -- the comment goes after both.
    A trailing word character or period would mean we matched a prefix of a
    longer number, so those are rejected.
    """
    pat = re.compile(re.escape(literal))
    seen = 0
    for n in range(body[0], body[1]):
        raw = lines[n].rstrip("\r\n")
        for m in pat.finditer(raw):
            tail = raw[m.end():m.end() + 1]
            if tail and (tail.isalnum() or tail == "."):
                continue
            seen += 1
            if seen == occurrence:
                return n, m.end()
    return None


# ------------------------------------------------------------------------ main
def load_entries(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("annotations", [])
    if not isinstance(data, list):
        raise ValueError("proposal file must be a JSON list, or an object with "
                         "an 'annotations' list")
    return data


def main(argv: list[str]) -> int:
    in_place = "--in-place" in argv
    dry_run = "--dry-run" in argv
    out_override = None
    args: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--output" and i + 1 < len(argv):
            out_override = Path(argv[i + 1])
            i += 2
            continue
        if not a.startswith("--"):
            args.append(a)
        i += 1
    if len(args) != 2:
        print(__doc__)
        return 1

    model, proposals = Path(args[0]), Path(args[1])
    for p in (model, proposals):
        if not p.exists():
            print(f"error: {p} not found", file=sys.stderr)
            return 2
    if model.suffix.lower() != ".mdl":
        print(f"error: {model} is not a .mdl", file=sys.stderr)
        return 2

    try:
        entries = load_entries(proposals)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {proposals}: {exc}", file=sys.stderr)
        return 2

    errs: list[str] = []
    for i, e in enumerate(entries, 1):
        if not isinstance(e, dict):
            errs.append(f"entry {i}: expected an object, got {type(e).__name__}")
            continue
        errs.extend(validate_entry(e, i))
    if errs:
        print("error: the proposal file was rejected; nothing was written:",
              file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 3

    raw = model.read_bytes().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    tally = Applied()
    lines = apply_entries(lines, entries, tally)

    dest = out_override or (model if in_place
                            else model.with_name(model.stem + "_annotated.mdl"))
    if not dry_run:
        dest.write_bytes("".join(lines).encode("utf-8"))

    print(f"annotate.py: {model.name} -> "
          f"{'(dry run, nothing written)' if dry_run else dest.name}")
    print(f"  applied:   {len(tally.applied)}")
    for s in tally.applied:
        print(f"    + {s}")
    print(f"  skipped:   {len(tally.skipped)}")
    for s in tally.skipped:
        print(f"    = {s}")
    print(f"  not found: {len(tally.missing)}")
    for s in tally.missing:
        print(f"    ? {s}")
    if tally.missing:
        print("\nnot-found targets were reported, not silently dropped; fix the "
              "paths in the proposal file and re-run.")
    print("\nOnly RiverWare validates a .mdl. Load the result in RiverWare and "
          "check the descriptions appear in the GUI before trusting it.")
    return 4 if tally.missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
