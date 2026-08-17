# RiverWare User Group demo script

A run-of-show for presenting four of this repository's skills:
[explain-riverware-model](../skills/explain-riverware-model/SKILL.md),
[riverware-help](../skills/riverware-help/SKILL.md),
[draft-riverware-rules](../skills/draft-riverware-rules/SKILL.md), and
[visualize-riverware-model](../skills/visualize-riverware-model/SKILL.md).
It doubles as a handout: every demo below can be reproduced from a clone of
this repository with Claude Code and Python installed.

The demos run against the two committed models in [`examples/`](../examples/):
**ArborBasin** (the CADSWES training model, included with attribution) and
**TwoResOps/Saratoga** (a synthetic two-reservoir testbed). Nothing leaves
the machine except fetches of public CADSWES help pages.

## Setup checklist (before the session)

- [ ] Clone the repo; verify `python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl` prints a digest.
- [ ] Open both GitHub Pages dashboard links in browser tabs and confirm they render on the presentation machine:
  [ArborBasin](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/ArborBasin/ArborBasin_dashboard.html) ·
  [TwoResOps](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/TwoResOps/saratoga_v2.4_dashboard.html).
  Keep the committed `*_dashboard.html` files as offline backup.
- [ ] Confirm the venue network reaches `https://www.riverware.org/HelpSystem/CurrentVersion/` (the live demo depends on it).
- [ ] Have the canned session files open in an editor as backup for every live segment (paths in each act below).

## The arc: read → ask → write → see

One sentence to frame the talk: *the model file is the ground truth, the
skills read it through parsers, and a human reviews everything before it
touches the model.*

### Act 1 — read: explain-riverware-model (canned, ~5 min)

Open [`examples/ArborBasin/ArborBasin_explained.md`](../examples/ArborBasin/ArborBasin_explained.md).

- Hook: everyone in the room has inherited an undocumented model. This is the
  training model they already know, narrated from the `.mdl` alone.
- Show the regeneration command so it is concrete, not magic:

  ```
  python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl
  ```

- Key point: the `.mdl` is a 1.6 MB generated script; the skill never reads it
  raw — a parser produces a digest, and the narrative is grounded in that.
- Do **not** generate a narrative live; it is minutes of quiet screen.

### Act 2 — ask: riverware-help (live, ~7 min)

Live prompt, typed on stage:

> In a rule I want to convert Cora's pool elevation to a storage volume.
> Which RPL function does that, and what happens between table rows?

- Watch for the two beats: the answer **cites the CADSWES help page URL**, and
  it checks the answer **against the actual model** — in the canned version it
  catches that `ElevationToArea`, the sibling function, would abort the run on
  Cora because the slot doesn't exist.
- Audience framing: this is not a chatbot's recollection of RiverWare; the
  quote comes from the live help page and the model facts come from the digest.
- Backup if the network fails, in order:
  [function lookup](../examples/sessions/riverware-help_elevation-lookup.md) ·
  [why-is-my-rule-overwritten](../examples/sessions/riverware-help_rule-overwrite.md) ·
  [DMI control file](../examples/sessions/riverware-help_dmi-control-file.md).
  The rule-overwrite session is the strongest fallback — it answers a
  "why is my model doing this" question every RBS user has hit.

### Act 3 — write: draft-riverware-rules (canned walkthrough, ~8 min)

Walk through
[`examples/sessions/draft-riverware-rules_roberto-min-flow.md`](../examples/sessions/draft-riverware-rules_roberto-min-flow.md)
top to bottom. This is the segment where the audience decides whether to
trust the tooling, so land these beats in order:

1. Plain-language request ("the river goes dry — add a minimum flow").
2. The skill digests the model first and quotes the real agenda order.
3. **The refusal**: the threshold slot does not exist, and the skill says so
   instead of inventing `Roberto.Min Flow`. This is the single most important
   moment of the talk for the "won't it hallucinate RPL?" question.
4. The draft mirrors an existing rule's idiom rather than importing style.
5. Placement is stated as a policy tradeoff (flood safety vs. the flow floor)
   that the modeler owns.
6. Every draft ends unvalidated: only RiverWare validates RPL.

Deeper follow-up material: the two case studies
([ArborBasin](../examples/ArborBasin/ArborBasin_rule_case_study.md),
[Saratoga drought cutoff](../examples/TwoResOps/saratoga_v2.4_rule_case_study.md)).

### Act 4 — see: visualize-riverware-model (canned, ~5 min)

Open the two GitHub Pages dashboards from the checklist tabs.

- Self-contained HTML, no server, no data leaving the file — shareable with
  anyone by sending one file.
- Regeneration command:

  ```
  python skills/visualize-riverware-model/digest_to_json.py examples/TwoResOps/saratoga_v2.4.mdl --html
  ```

- End here: it is the visual high note.

## Anticipated questions

- **"Will it hallucinate RPL / slot names?"** — Point back to Act 3's refusal
  beat and the guardrail in the skill: every `Object.Slot` reference must
  appear in the parser digest, and a missing slot is surfaced as a decision,
  not papered over.
- **"Where does my model data go?"** — The `.mdl` is read locally by Python
  parsers. Network traffic is limited to public CADSWES help pages (Act 2).
  Model data is not uploaded by the skills.
- **"Does the AI change my model?"** — The four demoed skills never write to
  a `.mdl`. The one skill in the repo that does (annotate-riverware-model)
  applies only a human-reviewed annotations file, via a script — keep the
  model under version control or copy it first, as with any model edit.
- **"Can I use this on my own model?"** — Yes: clone the repo (or install it
  as a plugin) and point any skill at your `.mdl`. The ArborBasin demos
  transfer directly since it is the standard training model.
- **"Which RiverWare versions?"** — The two example models were saved by
  RiverWare 9.4 (ArborBasin) and 9.7 (Saratoga) and both parse; the help skill tracks CurrentVersion and says so when the
  user's version differs.
