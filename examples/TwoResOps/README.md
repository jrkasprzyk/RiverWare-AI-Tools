# TwoResOps (Saratoga) example

`saratoga_v2.4.mdl` is a synthetic **two-reservoir operations model** built by
the repository owner as a compact policy-evaluation testbed. Twelve objects on
one river stem: two storage reservoirs (Cora upstream, Roberto downstream), an
irrigation district, a fishery reach, a flood-prone city control point, and an
ecological flow target — with an embedded ruleset that rations water among
them and an Objectives data object that scores the result on eight
performance measures.

It complements the larger [Arbor Basin](../ArborBasin/) example: Arbor Basin
shows breadth (41 objects, two basins, groundwater), Saratoga shows a clean,
readable policy loop.

## Contents

| File | What it is |
|------|------------|
| `saratoga_v2.4.mdl` | The RiverWare model (RiverWare 9.7 format, ~1.9 MB Tcl text) |
| `saratoga_v2.4_explained.md` | Narrative explanation produced with the explain skill, human-polished |
| `saratoga_v2.4_dashboard.html` | Self-contained interactive dashboard produced with the visualize skill ([live version](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/TwoResOps/saratoga_v2.4_dashboard.html)) |
| `saratoga_v2.4_rule_case_study.md` | Request → rule walkthrough produced with the draft-rules skill |
| `saratoga_v2.4_annotations.md` | Annotation proposals, numbered for review, produced with the annotate skill |
| `saratoga_v2.4_annotations.json` | The same proposals in machine form — the input `annotate.py` consumed |
| `saratoga_v2.4.mdl.bak` | Pre-description copy of the model, kept as the fixture that captured the `userDescript` serialization grammar |

## Annotations

The 28 approved annotations in `saratoga_v2.4_annotations.json` were applied to
the model in place, so `git log -p saratoga_v2.4.mdl` is the before/after
record. The modeler's own hand-written descriptions were all left untouched.

```bash
# what is described already, and what is still empty
python skills/explain-riverware-model/explain.py examples/TwoResOps/saratoga_v2.4.mdl --annotations

# re-apply (a no-op now -- every target reports SKIPPED, existing text)
python skills/annotate-riverware-model/annotate.py \
    examples/TwoResOps/saratoga_v2.4.mdl \
    examples/TwoResOps/saratoga_v2.4_annotations.json --dry-run
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
python skills/explain-riverware-model/explain.py examples/TwoResOps/saratoga_v2.4.mdl
```

Do not open the `.mdl` in a text editor expecting to read it — it is a
generated Tcl script of tens of thousands of lines. The parser digest is the
readable view.
