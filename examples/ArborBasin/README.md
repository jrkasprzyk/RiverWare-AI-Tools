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
| `ArborBasin_annotations.md` | Annotation proposals, numbered for review, produced with the annotate skill |
| `ArborBasin_annotations.json` | The same proposals in machine form — the input `annotate.py` consumed |

## Annotations

The 40 approved annotations in `ArborBasin_annotations.json` were applied to the
model in place, so `git log -p ArborBasin.mdl` is the before/after record. This
model is the volume test for the annotation rubric: **40 annotations against
1,116 available targets (3.6%)**, and 15 slot descriptions against 1,017 empty
slot fields. The 1,000-odd untouched slots are standard power-reservoir
plumbing that carries no model-specific policy meaning.

```bash
# what is described already, and what is still empty
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl --annotations

# re-apply (a no-op now -- every target reports SKIPPED, existing text)
python skills/annotate-riverware-model/annotate.py \
    examples/ArborBasin/ArborBasin.mdl \
    examples/ArborBasin/ArborBasin_annotations.json --dry-run
```

**Not yet verified in RiverWare.** The annotations are textually correct and the
applier is round-trip tested, but only RiverWare validates a `.mdl`. Load the
model and confirm the descriptions appear in the object, slot, and RPL editor
dialogs.

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
