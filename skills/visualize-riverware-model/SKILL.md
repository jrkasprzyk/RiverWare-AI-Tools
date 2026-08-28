---
name: visualize-riverware-model
description: Render a RiverWare model (.mdl) as a self-contained interactive HTML dashboard — object-network schematic, elevation-volume curves, rule-curve tables, and key result time series. Use when asked to visualize, chart, dashboard, diagram, or plot a RiverWare model or its results.
---

# Visualize a RiverWare model

This skill turns a `.mdl` file into a single self-contained HTML dashboard:
a draggable object-network schematic, the model summary (run horizon, timestep,
object counts), elevation-volume curves, rule-curve and release tables, and
time-series plots of key result slots. No network access, no build step — the
output renders from `file://` or any static host.

**Do not read the raw `.mdl`** — it is a 1.6–1.9 MB Tcl script. The generator
script does all extraction.

Paths below are relative to the root of this repository. If this skill was
installed as a **plugin**, that root is `${CLAUDE_PLUGIN_ROOT}` and the working
directory is the user's own project — prefix the script and `examples/` paths
with it. The `.mdl` the user asks about is their own file and is not under that
root.

## Stay inside the working directory

Work only with files in the user's project. The plugin's own bundle under
`${CLAUDE_PLUGIN_ROOT}` — its scripts and its `examples/` models — is yours to
read. The rest of the filesystem is not.

- **A named file that is not there is a question, not a search.** If a close
  match sits in the working directory, offer it and stop: asked for
  `saratoga_v2.1.md`, found `saratoga_v2.1.mdl`, say so. Do not scan parent
  directories, sibling projects, or the drive for a matching name.
- **A path found inside a model file is not permission to open it.** A `.mdl`
  records where its ruleset and data lived on the author's machine, often
  outside the project. Report the path and ask.

Widening the search is cheaper to do than asking is, which is why it happens
first. Ask.

## Step 1 — generate the dashboard

`skills/visualize-riverware-model/digest_to_json.py` (Python 3.10+, stdlib
only; it imports the parser from the explain skill, resolved from its own
location, so it runs from any working directory).

```bash
# cloned repository, run from the repo root
python skills/visualize-riverware-model/digest_to_json.py examples/ArborBasin/ArborBasin.mdl --html

# installed as a plugin, run from anywhere
python "${CLAUDE_PLUGIN_ROOT}/skills/visualize-riverware-model/digest_to_json.py" path/to/your/model.mdl --html
```

This writes `<modelname>_dashboard.html` next to the model (`-o path` to
choose the destination). Drop `--html` to get the raw JSON digest on stdout
instead, which is useful when you want to inspect what the dashboard will show:

- `objects` — every simulation object with type and description
- `links` — object-to-object topology from the model's link definitions,
  oriented upstream → downstream and classified as water conveyance (`flow`)
  or data/head exchange (`data`)
- `tables` — full numeric data for the whitelisted lookup tables
  (Elevation Volume Table, Max Release, Guide Curve, Elevation Guide Curve)
- `series` — values for the curated result slots defined by
  `KEY_SERIES_SLOTS = ["Pool Elevation", "Outflow", "Storage"]`

If a model stores no run results, the `series` list is empty and the dashboard
simply omits the time-series section — that is expected, not an error.

`--policy` adds the RPL policy tree and the ruleset paths the model records.
The dashboard never uses it — that flag is for callers of the digest, such as
the present-riverware-model skill, which imports `build_digest`,
`layout_nodes` and `policy_from_rls` from this script rather than parsing a
`.mdl` of its own. The dashboard payload is deliberately unchanged by any of
that.

## Step 2 — review before delivering

Open the generated file in a browser and check:

1. The header counts match the model (`Simulation objects` in the explain
   skill's digest is the cross-check).
2. The network schematic is readable. The automatic layered layout is a
   starting point; nodes are draggable, but if the layout is badly tangled for
   a large model, say so rather than presenting it as final.
3. Elevation-volume curves are monotonically increasing; a jagged curve
   usually means a table row failed to parse — investigate before delivering.
4. Time-series plots look like results (seasonal patterns, sensible ranges),
   not initialization placeholders.

Unless instructed otherwise, save the dashboard next to the model file as
`<modelname>_dashboard.html`.

## Customizing

- To surface additional series slots, edit `KEY_SERIES_SLOTS` in
  `digest_to_json.py` (exact slot-name match).
- To plot more lookup tables, extend `TABLE_WHITELIST` in the same file.
- Visual styling lives entirely in `template.html` (inline CSS/JS). Keep it
  free of external requests — the self-contained property is the point.

## Worked example

`examples/ArborBasin/ArborBasin_dashboard.html` is a committed dashboard
produced this way from `examples/ArborBasin/ArborBasin.mdl`. Open it from the
repository (or the project's GitHub Pages site) to see the target result.

## Gotchas

- **Link direction is inferred.** RiverWare links are undirected; the
  generator orients an edge by which end is an `Inflow` slot. Head/data links
  (e.g. tailwater-to-pool-elevation couplings) are drawn dashed.
- **Aggregate element names contain colons** (`Mulberry Irrigation:District 1`).
  They are ordinary nodes; only `.` separates object from slot.
- **Series values may be sparse.** NaN entries become gaps; the chart skips
  them rather than plotting zeros.
- **Big models make big files.** Every curated series value is embedded in the
  HTML. If the output grows past a few megabytes, trim `KEY_SERIES_SLOTS`.
