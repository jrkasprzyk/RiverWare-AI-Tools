# Examples

Two RiverWare models with committed outputs from every model skill, plus a
set of worked sessions for the skills that act on text rather than on a `.mdl`
— so you can see results without running anything. All outputs are **produced
with the repository's skills and then human-polished** into finished
documentation — they show what the workflow delivers after review, not raw
generation.

| Model | What it is | Committed outputs |
|-------|-----------|-------------------|
| [ArborBasin](ArborBasin/) | The CADSWES RiverWare training model: 41 objects, two basins joined by a transbasin diversion, a five-reservoir power cascade, irrigation districts, and a groundwater complex. Included with attribution to [CADSWES](https://cadswes.colorado.edu/), University of Colorado Boulder. | [Narrative](ArborBasin/ArborBasin_explained.md) · [Dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/ArborBasin/ArborBasin_dashboard.html) · [Slide deck](ArborBasin/ArborBasin_deck.pptx) · [Rule case study](ArborBasin/ArborBasin_rule_case_study.md) · [Annotation review](ArborBasin/ArborBasin_annotations.md) |
| [TwoResOps](TwoResOps/) | Saratoga, a synthetic two-reservoir operations testbed by the repository owner: irrigation, a fishery, a flood-prone city, and an ecological flow target scored by eight objective measures. | [Narrative](TwoResOps/saratoga_v2.4_explained.md) · [Dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/TwoResOps/saratoga_v2.4_dashboard.html) · [Rule case study](TwoResOps/saratoga_v2.4_rule_case_study.md) · [Annotation review](TwoResOps/saratoga_v2.4_annotations.md) |

The dashboard links above go to [GitHub Pages](https://jrkasprzyk.github.io/RiverWare-AI-Tools/),
which serves the rendered page. The same files are committed next to each
model (`*_dashboard.html`) — opening those on github.com shows HTML source,
so download them or use the Pages links to actually view them.

## Sessions

The other three skills do not produce a per-model artifact — they answer a
question, clean up code, or rewrite a report. [`sessions/`](sessions/) holds one
worked example of each, grounded in the models above.

| Session | Skill | What it shows |
|---------|-------|---------------|
| [Elevation lookup in a rule](sessions/riverware-help_elevation-lookup.md) | [riverware-help](../skills/riverware-help/SKILL.md) | A cited `ElevationToStorage` answer from the live CADSWES help, checked against what Saratoga's `Cora` actually has — including a sibling function that would abort the run on that object |
| [Why is my rule overwritten?](sessions/riverware-help_rule-overwrite.md) | [riverware-help](../skills/riverware-help/SKILL.md) | A "why is my model doing this" answer: rule priorities, the R flag, and the overwrite table from the live help, mapped onto Saratoga's actual `Roberto Rules` agenda |
| [DMI control-file syntax](sessions/riverware-help_dmi-control-file.md) | [riverware-help](../skills/riverware-help/SKILL.md) | Control-file line format and %-directives from the live help for Saratoga's `to_rw` input DMI — including a wildcard that would wrongly match a computed gage |
| [Minimum-flow rule, request to draft](sessions/draft-riverware-rules_roberto-min-flow.md) | [draft-riverware-rules](../skills/draft-riverware-rules/SKILL.md) | The conversation shape of a drafting session: digest first, an honest refusal to invent a missing threshold slot, a draft mirroring the model's own idiom, and placement stated as a policy tradeoff |
| [Comment cleanup, before and after](sessions/comment-cleanup_before-after.md) | [comment-cleanup](../skills/comment-cleanup/SKILL.md) | An AI-written post-processing script losing 11 history-and-restatement comments and gaining documented ranges, defaults, and units for three tuning constants |
| [Report cleanup, before and after](sessions/report-cleanup_before-after.md) | [report-cleanup](../skills/report-cleanup/SKILL.md) | A one-paragraph Saratoga bug report split into Summary / Repro / Hypothesis / four numbered Asks, with the writer's guess kept but relabeled |

The help sessions' cited content was fetched live and the report session's
hypothesis was checked against the Saratoga digest; the comment-cleanup input
is a constructed script, and the questions/requests in the help and drafting
sessions are constructed for the examples — each file labels what is
constructed and what is real.

## Which skill produced what

| Output | Skill | Regeneration command (from repo root) |
|--------|-------|----------------------------------------|
| `*_explained.md` | [explain-riverware-model](../skills/explain-riverware-model/SKILL.md) | `python skills/explain-riverware-model/explain.py <model.mdl>` then narrate per the SKILL.md |
| `*_dashboard.html` | [visualize-riverware-model](../skills/visualize-riverware-model/SKILL.md) | `python skills/visualize-riverware-model/digest_to_json.py <model.mdl> --html` |
| `*_rule_case_study.md` | [draft-riverware-rules](../skills/draft-riverware-rules/SKILL.md) | Digest the model, then draft per the SKILL.md |
| `*_annotations.md` / `.json` | [annotate-riverware-model](../skills/annotate-riverware-model/SKILL.md) | Propose per the SKILL.md, then `python skills/annotate-riverware-model/annotate.py <model.mdl> <annotations.json>` |
| `sessions/riverware-help_*.md` | [riverware-help](../skills/riverware-help/SKILL.md) | Ask the question; the skill fetches and cites the help |
| `sessions/draft-riverware-rules_*.md` | [draft-riverware-rules](../skills/draft-riverware-rules/SKILL.md) | State the policy request; the skill digests, drafts, and places |
| `sessions/comment-cleanup_*.md` | [comment-cleanup](../skills/comment-cleanup/SKILL.md) | Point the skill at the files or the working diff |
| `sessions/report-cleanup_*.md` | [report-cleanup](../skills/report-cleanup/SKILL.md) | Paste the report; the skill restructures it |

The `.mdl` files are 1.6–1.9 MB generated Tcl scripts — do not read them raw;
every skill goes through the parsers.
