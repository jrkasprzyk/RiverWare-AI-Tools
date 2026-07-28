#!/usr/bin/env python3
"""digest_to_json.py — extract a visualization digest from a RiverWare .mdl.

Reuses the structural parser from the explain-riverware-model skill and adds
what a dashboard needs: object-to-object link topology, full numeric data for
key lookup tables, and the curated result time series.

Usage:
    python digest_to_json.py model.mdl                 # JSON to stdout
    python digest_to_json.py model.mdl --html          # write <model>_dashboard.html
    python digest_to_json.py model.mdl --html -o out.html

The --html mode injects the JSON into template.html (next to this script) and
writes a fully self-contained dashboard (inline CSS/JS, no network access).
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "explain-riverware-model"))
from explain import parse_mdl  # noqa: E402

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
                values = [_num(v) for v in m.group(6).split()]
                if any(v is not None for v in values):
                    series.append({"object": obj, "slot": want,
                                   "unit": m.group(1), "start": m.group(2),
                                   "end": m.group(3),
                                   "timestep": f"{m.group(4)} {m.group(5)}",
                                   "values": values})
            want = None
    return series


def build_digest(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    mdl = parse_mdl(text)
    counts: dict[str, int] = {}
    for o in mdl["objects"]:
        counts[o["type"]] = counts.get(o["type"], 0) + 1
    return {
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
    digest = build_digest(p)
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
    raise SystemExit(main(sys.argv[1:]))
