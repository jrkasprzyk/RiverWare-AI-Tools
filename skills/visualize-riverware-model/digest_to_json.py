#!/usr/bin/env python3
"""digest_to_json.py — extract a visualization digest from a RiverWare .mdl.

Reuses the structural parser from the explain-riverware-model skill and adds
what a dashboard needs: object-to-object link topology, full numeric data for
key lookup tables, and the curated result time series.

Usage:
    python digest_to_json.py model.mdl                 # JSON to stdout
    python digest_to_json.py model.mdl --policy        # ... with the RPL policy tree
    python digest_to_json.py model.mdl --html          # write <model>_dashboard.html
    python digest_to_json.py model.mdl --html -o out.html

The --html mode injects the JSON into template.html (next to this script) and
writes a fully self-contained dashboard (inline CSS/JS, no network access).

This module is also the shared extraction layer for the
present-riverware-model skill, which imports `build_digest`, `layout_nodes`
and `policy_from_rls` instead of touching a `.mdl` itself. The dashboard
payload is fixed: `build_digest` adds the policy tree only when asked, so the
committed dashboards stay byte-identical.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "explain-riverware-model"))
from explain import parse_mdl, parse_rls  # noqa: E402

# Curated result series shown as time-series plots (owner decision: structure + key series).
KEY_SERIES_SLOTS = ["Pool Elevation", "Outflow", "Storage"]

# Lookup tables whose full numeric data is worth plotting/browsing.
TABLE_WHITELIST = [
    "Elevation Volume Table",
    "Max Release",
    "Guide Curve",
    "Elevation Guide Curve",
]

# Slot-name hints marking a link as water conveyance (vs. a data/head link).
FLOW_HINTS = ("Inflow", "Outflow", "Flow", "Diversion", "Seepage", "Return",
              "Available", "Delivered", "Bypass", "Pumped")

# Layered-layout geometry, in the SVG pixel units template.html draws with.
# The slide renderer scales these to slide coordinates, so the dashboard and
# the deck place the same model the same way.
LAYOUT_COLW = 190     # column pitch, px (>= LAYOUT_NODEW; wider = longer edges)
LAYOUT_ROWH = 58      # row pitch, px (>= LAYOUT_NODEH; wider = more vertical space)
LAYOUT_PAD = 40       # margin around the drawing, px
LAYOUT_NODEW = 150    # node box width, px
LAYOUT_NODEH = 34     # node box height, px
LAYOUT_PASSES = 30    # relaxation passes, 1-100; caps the cost of a cyclic network


def _split_ref(ref: str) -> tuple[str, str]:
    """'Obj.Slot Name' -> ('Obj', 'Slot Name'). Object names never contain '.'."""
    obj, _, slot = ref.partition(".")
    return obj, slot


def extract_links(text: str) -> list[dict]:
    links = []
    for a, b in re.findall(r"^\$ws Link \{([^}]+)\} \{([^}]+)\}", text, re.M):
        fo, fs = _split_ref(a)
        to, ts = _split_ref(b)
        # RiverWare links are undirected; orient for drawing: the side whose
        # slot is an Inflow is the downstream end.
        if ("Inflow" in fs) and ("Inflow" not in ts):
            fo, fs, to, ts = to, ts, fo, fs
        kind = "flow" if any(h in fs or h in ts for h in FLOW_HINTS) else "data"
        links.append({"from": fo, "from_slot": fs, "to": to, "to_slot": ts,
                      "kind": kind})
    return links


def _num(tok: str) -> float | None:
    try:
        f = float(tok)
        return None if math.isnan(f) else float(f"{f:.6g}")
    except ValueError:
        return None


def extract_tables(text: str) -> list[dict]:
    """Full numeric rows for whitelisted Table/Periodic slots, per object."""
    tables: list[dict] = []
    obj = None
    current: dict | None = None
    for ln in text.splitlines():
        m = re.search(r'simObjName="([^"]+)"', ln)
        if m:
            obj = m.group(1)
            continue
        m = re.match(r'"\$o" \{(TableSlot|PeriodicSlot)\} \{([^}]*)\}', ln)
        if m:
            name = m.group(2)
            if name in TABLE_WHITELIST and obj:
                current = {"object": obj, "slot": name, "kind": m.group(1),
                           "cols": [], "rows": []}
                tables.append(current)
            else:
                current = None
            continue
        if current is None:
            continue
        m = re.match(r'"\$s" setColumnLabels (.+)', ln)
        if m:
            current["cols"] = re.findall(r"\{([^}]*)\}", m.group(1))
        m = re.match(r'"\$s" row \d+ (.+)', ln)
        if m:
            current["rows"].append([_num(v) for v in m.group(1).split()])
    return [t for t in tables if t["rows"]]


def _expand_rle(tokens: list[str]) -> list[float | None]:
    """Expand a setDSeries value stream, where 'v @ N' run-length-encodes a
    value that holds for N timesteps (the count includes the occurrence
    already emitted, so '@ N' appends N-1 repeats)."""
    values: list[float | None] = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "@" and i + 1 < len(tokens) and values:
            values.extend([values[-1]] * (int(tokens[i + 1]) - 1))
            i += 2
        else:
            values.append(_num(tokens[i]))
            i += 1
    return values


def extract_series(text: str) -> list[dict]:
    """Values for the curated series slots (from setDSeries data lines)."""
    series: list[dict] = []
    obj = None
    want: str | None = None
    for ln in text.splitlines():
        m = re.search(r'simObjName="([^"]+)"', ln)
        if m:
            obj = m.group(1)
            continue
        m = re.match(r'"\$o" \{\w+Slot\} \{([^}]*)\}', ln)
        if m:
            want = m.group(1) if m.group(1) in KEY_SERIES_SLOTS else None
            continue
        if want and obj and ln.startswith('"$s" setDSeries'):
            m = re.match(r'"\$s" setDSeries \{([^}]*)\} \{([^}]*)\} \{([^}]*)\}'
                         r" (\d+) (\w+) -?\d+ (.*)$", ln)
            if m:
                values = _expand_rle(m.group(6).split())
                if any(v is not None for v in values):
                    series.append({"object": obj, "slot": want,
                                   "unit": m.group(1), "start": m.group(2),
                                   "end": m.group(3),
                                   "timestep": f"{m.group(4)} {m.group(5)}",
                                   "values": values})
            want = None
    return series


def object_edges(objects: list[dict], links: list[dict]) -> list[dict]:
    """Object-level edges: self-links dropped, dangling ends dropped, deduplicated."""
    names = {o["name"] for o in objects}
    seen: set[tuple[str, str, str]] = set()
    edges: list[dict] = []
    for l in links:
        if l["from"] == l["to"] or l["from"] not in names or l["to"] not in names:
            continue
        key = (l["from"], l["to"], l["kind"])
        if key in seen:
            continue
        seen.add(key)
        edges.append({"from": l["from"], "to": l["to"], "kind": l["kind"]})
    return edges


def layout_nodes(objects: list[dict], links: list[dict]) -> dict:
    """Place objects on a left-to-right layered grid, upstream to downstream.

    Depth is the longest path over water-conveyance edges only, found by
    relaxation with a cycle cap -- a basin with a return-flow loop has no
    topological order, and a capped relaxation degrades to a usable layout
    instead of failing. Data/head edges do not move a node, so a tailwater
    coupling cannot drag a reservoir out of its column.

    Returns nodes with x/y in pixel units, the deduplicated edges, and the
    bounding box the caller scales to its own canvas.
    """
    edges = object_edges(objects, links)
    depth = {o["name"]: 0 for o in objects}
    flow = [e for e in edges if e["kind"] == "flow"]
    for _ in range(LAYOUT_PASSES):
        changed = False
        for e in flow:
            d = depth[e["from"]] + 1
            if d > depth[e["to"]] and d < len(depth):
                depth[e["to"]] = d
                changed = True
        if not changed:
            break
    cols: dict[int, list[str]] = {}
    for name in sorted(depth):
        cols.setdefault(depth[name], []).append(name)
    by_name = {o["name"]: o for o in objects}
    nodes: list[dict] = []
    max_rows = 0
    for ci, d in enumerate(sorted(cols)):
        max_rows = max(max_rows, len(cols[d]))
        for ri, name in enumerate(cols[d]):
            nodes.append({"name": name, "type": by_name[name]["type"],
                          "column": ci, "row": ri,
                          "x": LAYOUT_PAD + ci * LAYOUT_COLW,
                          "y": LAYOUT_PAD + ri * LAYOUT_ROWH})
    return {"nodes": nodes, "edges": edges,
            "width": LAYOUT_PAD * 2 + len(cols) * LAYOUT_COLW,
            "height": LAYOUT_PAD * 2 + max_rows * LAYOUT_ROWH,
            "node_width": LAYOUT_NODEW, "node_height": LAYOUT_NODEH}


def _policy_groups(groups: list[dict]) -> list[dict]:
    """Normalize the parser's RPL tree: absent ACTIVE fields mean active."""
    return [{"kind": g["kind"], "name": g["name"],
             "active": g.get("active") is not False,
             "description": g.get("description", ""),
             "items": [{"kind": it["kind"], "name": it["name"],
                        "active": it.get("active") is not False,
                        "description": it.get("description", ""),
                        "notes": it.get("notes", "")}
                       for it in g["items"]]}
            for g in groups]


def extract_policy(mdl: dict) -> dict:
    """The RPL sets serialized inside the .mdl, as agenda-ordered policy trees.

    Rule bodies are left out on purpose: a deck states what a rule does, and
    the wording for that comes from the spec, not from RPL source.
    """
    set_types = dict(mdl.get("rpl_sets", []))
    sets = []
    for rs in mdl.get("embedded_rpl", []):
        if not rs["groups"]:
            continue
        sets.append({"name": rs["name"], "type": set_types.get(rs["name"], "?"),
                     "agenda": rs["agenda"] or "?",
                     "description": rs["description"],
                     "groups": _policy_groups(rs["groups"])})
    return {"sets": sets}


def policy_from_rls(text: str) -> dict:
    """The same policy shape from a standalone .rls the user supplied.

    A model whose operating policy lives in an external ruleset has nothing to
    extract from the .mdl; the modeler has to hand over the .rls (AGENTS.md:
    the path recorded in the model is reported, never opened).
    """
    rls = parse_rls(text)
    if not rls["groups"]:
        return {"sets": []}
    return {"sets": [{"name": rls["name"] or "(unnamed ruleset)",
                      "type": "Rule Based Simulation",
                      "agenda": rls["agenda"] or "?",
                      "description": rls["description"],
                      "groups": _policy_groups(rls["groups"])}]}


def extract_ruleset_files(text: str) -> list[str]:
    """Ruleset paths the .mdl records. Reported to the user, never opened."""
    return sorted(set(re.findall(r'[^\s"{}<>\\]+\.rls', text)))


def build_digest(path: Path, include_policy: bool = False) -> dict:
    """Structure, topology, lookup tables and result series for one model.

    include_policy adds the RPL policy tree and the ruleset paths the model
    references. It is off by default because the dashboard embeds this digest
    verbatim, and the committed dashboards must regenerate unchanged.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    mdl = parse_mdl(text)
    counts: dict[str, int] = {}
    for o in mdl["objects"]:
        counts[o["type"]] = counts.get(o["type"], 0) + 1
    digest = {
        "model": {
            "file": path.name,
            "version": mdl["header"].get("version", "?"),
            "run": mdl.get("run", {}),
            "object_count": mdl["header"].get("sim_obj_count", len(mdl["objects"])),
            "type_counts": counts,
        },
        "objects": [{"name": o["name"], "type": o["type"],
                     "description": o["description"],
                     "slot_count": len(o["slots"])} for o in mdl["objects"]],
        "links": extract_links(text),
        "tables": extract_tables(text),
        "series": extract_series(text),
    }
    if include_policy:
        digest["policy"] = extract_policy(mdl)
        digest["policy"]["referenced_files"] = extract_ruleset_files(text)
    return digest


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("-")]
    as_html = "--html" in argv
    out_path = None
    if "-o" in argv:
        out_path = Path(argv[argv.index("-o") + 1])
        args = [a for a in args if a != str(out_path)]
    if not args:
        print(__doc__)
        return 1
    p = Path(args[0])
    if not p.exists() or p.suffix.lower() != ".mdl":
        print(f"error: {args[0]} is not an existing .mdl file", file=sys.stderr)
        return 2
    # The dashboard payload never carries the policy tree -- see build_digest.
    digest = build_digest(p, include_policy=("--policy" in argv and not as_html))
    payload = json.dumps(digest, separators=(",", ":"), allow_nan=False)
    if not as_html:
        print(payload)
        return 0
    template = (Path(__file__).resolve().parent / "template.html").read_text(encoding="utf-8")
    html = template.replace("/*__DATA__*/null", payload)
    out = out_path or p.with_name(p.stem + "_dashboard.html")
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(digest['objects'])} objects, "
          f"{len(digest['links'])} links, {len(digest['series'])} series)")
    return 0


if __name__ == "__main__":
    try:
        _code = main(sys.argv[1:])
        sys.stdout.flush()  # surface a closed pipe here, not at shutdown
    except BrokenPipeError:
        # Same guard as explain.py: the JSON digest is routinely piped into
        # `head` or `python -m json.tool`, and a reader that exits early must
        # not produce a traceback over the caller's output.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        _code = 0
    raise SystemExit(_code)
