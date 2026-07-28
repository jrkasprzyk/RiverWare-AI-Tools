# Examples

Two RiverWare models with committed outputs from every skill, so you can see
results without running anything. All outputs are **produced with the
repository's skills and then human-polished** into finished documentation —
they show what the workflow delivers after review, not raw generation.

| Model | What it is | Committed outputs |
|-------|-----------|-------------------|
| [ArborBasin](ArborBasin/) | The CADSWES RiverWare training model: 41 objects, two basins joined by a transbasin diversion, a five-reservoir power cascade, irrigation districts, and a groundwater complex. Included with attribution to [CADSWES](https://cadswes.colorado.edu/), University of Colorado Boulder. | [Narrative](ArborBasin/ArborBasin_explained.md) · [Dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/ArborBasin/ArborBasin_dashboard.html) · [Rule case study](ArborBasin/ArborBasin_rule_case_study.md) |
| [TwoResOps](TwoResOps/) | Saratoga, a synthetic two-reservoir operations testbed by the repository owner: irrigation, a fishery, a flood-prone city, and an ecological flow target scored by eight objective measures. | [Narrative](TwoResOps/saratoga_v2.4_explained.md) · [Dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/TwoResOps/saratoga_v2.4_dashboard.html) · [Rule case study](TwoResOps/saratoga_v2.4_rule_case_study.md) |

The dashboard links above go to [GitHub Pages](https://jrkasprzyk.github.io/RiverWare-AI-Tools/),
which serves the rendered page. The same files are committed next to each
model (`*_dashboard.html`) — opening those on github.com shows HTML source,
so download them or use the Pages links to actually view them.

## Which skill produced what

| Output | Skill | Regeneration command (from repo root) |
|--------|-------|----------------------------------------|
| `*_explained.md` | [explain-riverware-model](../skills/explain-riverware-model/SKILL.md) | `python skills/explain-riverware-model/explain.py <model.mdl>` then narrate per the SKILL.md |
| `*_dashboard.html` | [visualize-riverware-model](../skills/visualize-riverware-model/SKILL.md) | `python skills/visualize-riverware-model/digest_to_json.py <model.mdl> --html` |
| `*_rule_case_study.md` | [draft-riverware-rules](../skills/draft-riverware-rules/SKILL.md) | Digest the model, then draft per the SKILL.md |

The `.mdl` files are 1.6–1.9 MB generated Tcl scripts — do not read them raw;
every skill goes through the parsers.
