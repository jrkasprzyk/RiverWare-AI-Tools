# Deck-spec reference

The authoritative description of the JSON that `build_pptx.py` renders, the
slide types it understands, and what it guarantees about the file it writes.
`SKILL.md` is the workflow; this file is the contract.

## 1. The spec

A deck spec is a JSON object. `slides` is the only required key.

```json
{
  "deck_title": "Arbor Basin operations review",
  "date": "2026-08-28",
  "template": null,
  "slides": [ { "type": "title", "id": "cover" } ]
}
```

| Key | Required | Meaning |
|-----|----------|---------|
| `deck_title` | no | Title on the cover slide and in the file's document properties. Defaults to the model file name. |
| `date` | no | The date shown in the footer, `YYYY-MM-DD`. Defaults to `--date`, then to today. |
| `template` | no | Path to a `.pptx` whose theme and layouts the deck inherits. `--template` overrides it. |
| `slides` | yes | Ordered, non-empty list of slide objects. |

A bare JSON list is accepted as shorthand for `{"slides": [...]}`.

### Slide objects

| Key | Required | Meaning |
|-----|----------|---------|
| `type` | yes | One of the nine types in section 2. |
| `id` | no | Stable identifier, unique in the deck. Used to talk about a slide across edits. |
| `title` | no | Overrides the heading the renderer would choose. |
| `bullets` | some types | Narrative lines. On figure slides they sit under the figure; on `bullets` slides they are the slide. |
| `refs` | some types | What the slide draws. Every reference is checked against the model before anything is rendered. |
| `annotations` | `policy` only | Map of `"Group"` or `"Group/Rule"` to a one-line description. |
| `notes` | no | Speaker notes, appended after the provenance line the renderer writes. |

## 2. Slide types

| Type | `refs` | Draws |
|------|--------|-------|
| `title` | none | Model file, RiverWare version, run horizon, timestep, object counts, date, plus any `bullets`. |
| `network` | `objects` (optional filter) | Layered object schematic: nodes coloured by object type, flow links as solid arrows, data and head links dashed, plus a type legend. Nodes and connectors are native shapes, so a presenter can nudge them and the links follow. |
| `summary` | `objects`, `types` (optional filters), `ruleset_note` | Object inventory table: name, type, slot count, description, under a type-count line. |
| `policy` | `set` (optional), `groups` (optional filter and order) | Table of policy groups and their rules, with the agenda-order caption. The `#` column is each rule's agenda position, counted over the whole set. Wording comes from `annotations`, falling back to the rule's own description. |
| `series` | `series` (required) | Native line chart of stored result series on a shared date axis. |
| `table` | `table` (required) | Native table of a lookup table's rows. |
| `chart-xy` | `table` (required), `x`, `y` (optional) | Native scatter-line chart of one lookup table's columns, e.g. an elevation-volume curve. `x` defaults to the first column, `y` to all the others. |
| `bullets` | none | Free narrative slide. `bullets` is required; nothing is drawn from the model. |
| `caveats` | none | The standing "check it against RiverWare" closing slide, plus any `bullets`. |

### Reference formats

- An object reference is a bare object name: `"Aspen"`.
- A series reference is `"Object.Slot"` and must name a slot that has stored
  values: `"Aspen.Pool Elevation"`. Object names never contain a `.`, so the
  first `.` splits the two.
- A table reference is `"Object.Slot"` for a lookup table the digest extracted:
  `"Aspen.Elevation Volume Table"`. The extracted set is the whitelist in
  `digest_to_json.py` (`TABLE_WHITELIST`).
- A policy reference names a rule set by its own name, then groups inside it.
  `refs.groups` both selects and orders: the groups appear in the order the
  spec lists them, which matters because an `ASCENDING` set is stored in the
  reverse of its firing order. The `#` column is unaffected — it is always the
  rule's agenda position in the full set.

### Worked example

```json
{
  "deck_title": "Arbor Basin: how the system is operated",
  "date": "2026-08-28",
  "slides": [
    {"type": "title", "id": "cover"},
    {"type": "network", "id": "system",
     "bullets": ["Eight reservoirs on two forks, joining above the state line."],
     "notes": "Link direction is inferred from inflow slots."},
    {"type": "policy", "id": "policy-aspen",
     "refs": {"set": "Arbor Basin Rules", "groups": ["Aspen Rules"]},
     "annotations": {
       "Aspen Rules": "Holds Aspen between its physical limits, then tracks the guide curve.",
       "Aspen Rules/Aspen Elevation Max": "Releases whatever is needed to stay under the maximum."
     }},
    {"type": "series", "id": "results-elevation",
     "refs": {"series": ["Aspen.Pool Elevation", "Birch.Pool Elevation"]},
     "bullets": ["Both reservoirs refill by June and draft through the autumn."]},
    {"type": "caveats", "id": "caveats"}
  ]
}
```

## 3. Validation

Validation runs to completion before any slide is drawn. If anything fails,
every problem is listed on stderr, the exit code is 3, and no file is written
— there is no such thing as a partially rendered deck.

Checked:

- `type` is one of the nine listed types.
- `id` is a non-empty string and unique within the deck.
- Every object, type, series, table, column, rule set and group reference
  exists in the model. The message names the valid targets, capped at twelve
  with a total count.
- `series` slides name at least one series; `table` and `chart-xy` slides name
  a table; `bullets` slides carry bullets.
- A `policy` slide on a model with no rule set is rejected with a pointer to
  `--rls`.

Exit codes: `0` written, `1` usage, `2` a file or dependency problem,
`3` the spec was rejected.

## 4. Command line

```
python build_pptx.py <model.mdl> (--spec deck.json | --auto)
                     [--template client.pptx] [--rls policy.rls]
                     [--date YYYY-MM-DD] [-o out.pptx]
```

| Option | Effect |
|--------|--------|
| `--spec` | Render this spec. Mutually exclusive with `--auto`. |
| `--auto` | Generate a generic baseline spec, render it, and write the spec next to the deck so it can be edited and re-rendered. |
| `--template` | Inherit theme and layouts from a `.pptx`. Best effort; see section 6. |
| `--rls` | Read an external ruleset for the `policy` slides. Used when the model carries no embedded rule set. |
| `--date` | The date in the footer. Pin it to make a rebuild byte-identical. |
| `-o` | Output path. Defaults to `<model>_deck.pptx` next to the model. |

The `--auto` baseline is title, network, summary, one policy slide per four
rule groups, a chart of reservoir pool elevations, a chart of reservoir
outflows, and caveats. Slides whose data is absent are simply not emitted: a
model with no stored results gets no series slides. The baseline makes no claim
about which part of the model matters, which is what a written spec is for.

## 5. Determinism

The same spec and the same model produce a byte-identical `.pptx` on every
run, provided the date is pinned (`--date`, or `date` in the spec). Three
things had to be neutralised to get there:

- Document core properties are stamped with a fixed timestamp, and author and
  last-modified-by are left empty.
- Every zip entry is written with a fixed date rather than the current clock.
- A chart's data lives in an embedded Excel workbook, which is a zip with its
  own timestamps and its own creation date. Those are normalised recursively.

Without a pinned date the footer changes daily, so two runs match within a day
and differ across midnight. `tests/test_pptx.py` asserts byte equality for a
deck with charts and one without.

## 6. Templates, best effort

`--template` keeps the template's slide masters, layouts, theme colours and
fonts, and discards any example slides it contained. Layouts are found by
name — `Title Slide`, `Title and Content`, `Title Only`, `Blank` — then by
position, then by falling back to the first layout in the file. Every fallback
is printed as a warning.

This works with most templates and is guaranteed with none. A template with
renamed layouts, an unusual master, or no title placeholders still renders,
but the result may not look like the rest of the client's deck. The review
step in `SKILL.md` exists to catch that: open the deck, compare it with the
template, and fix by hand what the renderer could not infer.

Text colours are set as theme colours rather than literal RGB, so body text
follows the template. Object-type fills in the schematic and the chart series
colours stay literal — they are a data legend, not decoration.

## 7. Tuning constants

All in `build_pptx.py`, each with its range and effect in a comment next to it.

| Constant | Default | Effect |
|----------|---------|--------|
| `MAX_SERIES_POINTS` | 400 | Points per chart. A longer series is thinned by a fixed stride and the notes say so. |
| `SUMMARY_MAX_ROWS` | 14 | Objects on one summary slide; the rest are counted in a footnote. |
| `TABLE_MAX_ROWS` | 12 | Data rows on one table slide. |
| `POLICY_MAX_ROWS` | 18 | Group and rule lines on one policy slide. |
| `NETWORK_CROWDED` | 45 | Object count past which the schematic is reported as crowded. |
| `NODE_FONT_WARN` | 8.0 | Label size, in points, under which readability is reported. |
| `MAX_NODE_W_IN` / `MAX_NODE_H_IN` | 2.2 / 0.6 | Caps on node box size, so a three-object model does not get three enormous boxes. |
| `LEGEND_ROWS` | 2 | Rows the type legend may wrap onto before entries are dropped. |

## 8. Compatibility

Requires `python-pptx>=0.6.21`; developed and tested against 1.0.2. The APIs
this script depends on beyond the basics are `add_connector` with
`begin_connect`/`end_connect`, `CategoryChartData` with date categories, and
`XyChartData`.

`build_pptx.py` writes a standard Open XML package: no macros, no external
references, no linked media. Every emitted part is well-formed XML and every
part declared in `[Content_Types].xml` is present in the archive, which
`tests/test_pptx.py` asserts on each build.

| Target | Status | Checked by |
|--------|--------|------------|
| Package structure (well-formed XML, complete inventory) | verified | `tests/test_pptx.py`, every run |
| Geometry (nothing drawn off the slide) | verified | `tests/test_pptx.py`, every run |
| PowerPoint desktop 2016+ | pending owner check | open `examples/ArborBasin/ArborBasin_deck.pptx`, confirm no repair prompt |
| PowerPoint for the web | pending owner check | upload and open the same file |
| LibreOffice Impress | pending owner check | open the same file |

Only PowerPoint validates a `.pptx`. A clean run here is not proof the deck
opens; record what you find in this table.

## 9. Shared extraction

Nothing here reads a `.mdl`. Extraction goes through
`skills/visualize-riverware-model/digest_to_json.py`:

- `build_digest(path, include_policy=True)` — objects, links, lookup tables,
  result series, and the RPL policy tree. `include_policy` is off by default,
  because the dashboard embeds this digest verbatim and must keep regenerating
  unchanged.
- `layout_nodes(objects, links)` — the layered layout the dashboard draws with,
  in pixel units, scaled here to slide coordinates. One layout algorithm, two
  views of the same model.
- `policy_from_rls(text)` — the same policy shape from a standalone `.rls`.

A `.mdl` records the path of the ruleset it last loaded. `build_digest` reports
those paths under `policy.referenced_files` and the CLI prints them when the
model carries no embedded set. They are reported, never opened.
