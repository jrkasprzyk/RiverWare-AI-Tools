# Arbor Basin example

`ArborBasin.mdl` is the **Arbor Basin training model** developed by
[CADSWES](https://cadswes.colorado.edu/) (Center for Advanced Decision Support
for Water and Environmental Systems, University of Colorado Boulder) for
RiverWare training. It is included here, with CADSWES attribution, as a
realistic mid-size example: a two-basin system with a five-reservoir power
cascade, a transbasin diversion, irrigation districts, and a
canal-and-groundwater conjunctive-use complex — 41 simulation objects with an
embedded RPL ruleset.

## Contents

| File | What it is |
|------|------------|
| `ArborBasin.mdl` | The RiverWare model (RiverWare 9.4 format, ~1.7 MB Tcl text) |
| `ArborBasin_explained.md` | Narrative explanation produced with the explain skill, human-polished |
| `ArborBasin_dashboard.html` | Self-contained interactive dashboard produced with the visualize skill ([live version](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/ArborBasin/ArborBasin_dashboard.html)) |
| `ArborBasin_rule_case_study.md` | Request → rule walkthrough produced with the draft-rules skill |

## Regenerating the outputs

The narrative was produced with the
[explain-riverware-model](../../skills/explain-riverware-model/SKILL.md) skill.
Its structural digest comes from (run at the repo root):

```bash
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl
```

Do not open the `.mdl` in a text editor expecting to read it — it is a
generated Tcl script of tens of thousands of lines. The parser digest is the
readable view.
