### name: visualize-riverware-model
description: Render a RiverWare model (.mdl) as a self-contained interactive HTML dashboard — object-network schematic, elevation-volume curves, rule-curve tables, and key result time series.

## Visualize a RiverWare model

This skill turns a `.mdl` into a single self-contained HTML dashboard:
draggable object-network schematic, model summary, elevation-volume curves, rule-curve/release tables, and curated result time series.

**Hard rule:** Do not read the raw `.mdl`. Use the generator; verify only narrow line ranges if needed.

### Step 1 — generate the dashboard
Run directly:

- `SKILL-code-digest_to_json.py model.mdl --html`  
  - Writes `<modelname>_dashboard.html` next to the model (use `-o` to choose destination).
- Drop `--html` to emit the raw JSON digest (objects, links, whitelisted tables, curated series).

### Step 2 — review before delivering
Open the generated dashboard:
- Header counts match the digest.
- Network schematic readable (drag to refine).
- Elevation-volume curves monotonically increasing.
- Time series look like results (sensible ranges/patterns).

### Customizing
- Add series: edit `KEY_SERIES_SLOTS`.
- Plot more tables: extend `TABLE_WHITELIST`.
- Visual styling is in `template.html`; keep self-contained.

**If example files are not present:** Run the skill against user-supplied `.mdl`. If none are provided, answer using the skill output and REF_ documentation.