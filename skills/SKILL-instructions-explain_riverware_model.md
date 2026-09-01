### name: explain-riverware-model
description: Write a plain-language narrative explanation of a RiverWare model (.mdl) and/or ruleset (.rls) — what objects, slots, rule curves, DMIs, and policy rules the file contains and how they operate together. Use when asked to explain, summarize, document, walk through, or describe a RiverWare .mdl or .rls file.

## Explain a RiverWare model / ruleset

This skill produces a **narrative explanation** — flowing prose a modeler can read — by first extracting a structural digest with a parser, then narrating it with RiverWare domain knowledge.

**Hard rule:** Never read a `.mdl` raw; use the skill’s digest and read only narrow line ranges when verifying a specific block.

### Step 1 — extract the skeleton (driver)
Run the skill directly on user-supplied files:

- `SKILL-code-explain_riverware_model.py model.mdl`  
- `SKILL-code-explain_riverware_model.py ruleset.rls`  
- `SKILL-code-explain_riverware_model.py model.mdl ruleset.rls`  
Options:
- `--json` for machine-readable output
- `--annotations` for the description inventory

From the digest, you will have:
- RiverWare version, run horizon + timestep, object count; each object’s type, description, selected methods, slots by type; rule-curve / lookup tables (labels, rows, samples); DMIs, embedded RPL sets, model scripts.
- (If separate `.rls` exists) ruleset name, agenda order, precision, description; each policy/utility group and every rule/function with active flags, notes, and bodies.

### When the operating policy is not in the model
If the digest’s **Embedded RPL sets** list has no Rule Based Simulation set, the operating policy is in an external `.rls`. Report the path (as recorded in the model) and ask the user to supply the file. Stay inside the working directory.

### Step 2 — narrate the digest
Write prose organized as:
- **Overview** — basin objects, run horizon, timestep.
- **Physical network** — top to bottom; focus on important elevations in tables (e.g., Dead Pool, Max Elevation), not row counts.
- **Data / rule-curve objects** — highlight RC/Data objects and DMI-written slots.
- **Ruleset** — respect agenda order (ASCENDING = bottom rule fires first); document active groups/rules in execution order; inactive are history.
- **External connections** — optimizers or DMI workflows: name objective/constraint/metric slots and involved DMIs matter-of-factly.

**House style**
- Capitalize named objects/slots; lowercase generic types.
- No contractions; “timestep”, “streamflow”.
- Cross-check names/counts; do not invent slots.
- Use authoritative RiverWare help for semantics.

**Delivery**
Save as `<model>_explained.md` next to the model unless instructed otherwise.

**If example files are not present:** Run the skill against user-supplied `.mdl`/`.rls`. If none are provided, answer using the skill output and REF_ documentation.