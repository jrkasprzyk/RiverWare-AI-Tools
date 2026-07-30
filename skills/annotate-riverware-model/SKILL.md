---
name: annotate-riverware-model
description: Propose and apply descriptions and RPL comments to a RiverWare model — objects, slots, rules, functions, and the model itself — reviewed by the modeler before anything is written. Use when asked to add comments, descriptions, or documentation to a RiverWare model, ruleset, or RPL code.
---

# Annotate a RiverWare model

Older RiverWare models are almost entirely undescribed: the Description fields
on objects, slots, rules and functions exist, and they are empty. This skill
fills the ones worth filling.

The deliverable is **a proposal the modeler approves, then a file the modeler
loads in RiverWare** — never an annotated model handed over as finished. Two
things make that non-negotiable: taste is exactly the judgment a human should
confirm, and only RiverWare validates a `.mdl`.

Paths below are relative to the root of this repository. If this skill was
installed as a **plugin**, that root is `${CLAUDE_PLUGIN_ROOT}` and the working
directory is the user's own project — prefix the script paths with it. The
`.mdl` the user asks about is their own file and is not under that root.

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

Never read a `.mdl` raw — they are 1.6–1.9 MB Tcl scripts. Everything you need
comes from the parser. Read narrow line ranges only to verify one specific
block.

---

## Step 1 — digest the model, then inventory what is already described

Two runs. The first tells you what the model *is*; the second tells you where a
description could go and whether one is already there.

```bash
# cloned repository, run from the repo root
python skills/explain-riverware-model/explain.py examples/TwoResOps/saratoga_v2.4.mdl
python skills/explain-riverware-model/explain.py examples/TwoResOps/saratoga_v2.4.mdl --annotations

# installed as a plugin, run from anywhere
python "${CLAUDE_PLUGIN_ROOT}/skills/explain-riverware-model/explain.py" path/to/model.mdl
python "${CLAUDE_PLUGIN_ROOT}/skills/explain-riverware-model/explain.py" path/to/model.mdl --annotations
```

The inventory marks `[x]` for taken and `[ ]` for available, and ends with the
target-path forms the proposal JSON uses. **Anything marked `[x]` is off the
table** — the modeler wrote it, and this skill does not touch it. (The applier
enforces that independently, but a proposal that tries is a proposal that
wasted the reviewer's time.)

For rule bodies — needed to describe a rule honestly, and required for any
expression comment — grep the specific rule out of the `.mdl`, or read the
narrow line range the digest points at.

## Step 2 — decide what deserves an annotation

**This step is the skill.** The applier is mechanical; choosing well is not.
A model with 1,116 empty description fields does not want 1,116 descriptions.

### The tastefulness rubric

**Objects** — one sentence on the object's role in the basin. Major objects
only: reservoirs, water users, control points, the data objects that carry
metrics. Not every gage and confluence.

**Slots** — the *policy-meaning test*. Any slot, standard or custom, earns a
description if and only if it carries model-specific policy meaning: it is read
by a rule, holds a threshold, is a decision variable, or is a reported metric.
Pure physics slots stay bare. `Cora.Inflow` is physics. `Cora.Shortage Table`
is policy. `Roberto.Flood Control Level` is a decision variable. The owner's
hand-written description on `Cora.Pool Elevation`'s shortage table (repo commit
`6bed09b`) is the worked example of a standard slot that earns one.

**Rules and functions** — at most one or two sentences, and **only where the
name alone is not self-explanatory.** This is the cap that matters most,
because rules are where verbosity accumulates fastest.

**Expression comments (`COMMENTED_BY`)** — magic numbers, unit-bearing
thresholds, and non-obvious constructs (an `IF` with no `ELSE` that deliberately
leaves a slot unset for a later rule to fill). **No more than one comment per
rule body** unless the rule is unusually dense. v1 attaches comments to numeric
literals only.

**The model description** — one short paragraph: what basin, what reservoirs,
what the policy is trying to do.

### Good versus bad

| Target | Bad | Why | Good |
|---|---|---|---|
| `Cedar.Elevation Guide Curve` | "This is the guide curve for Cedar." | Restates the name. Costs a reader time and returns nothing. | *(leave empty — the name says it)* |
| `Roberto.Delivery Threshold` | "The delivery threshold." | Same. | "Below this pool elevation Roberto cannot pass releases downstream to the irrigators." |
| RULE `Cedar Outflow Min` | "This rule sets the minimum outflow for Cedar." | Restates the name. | *(leave empty)* |
| RULE `Find Shortage Level` | "Finds the shortage level." | Restates the name. | "This sets the Shortage Fraction[] variable only; no release is set at this point." — the owner's own, and the reason it earns a description is that the *absence* of a release is surprising. |
| literal `0.00000000 "kcfs"` | "Zero kcfs." | Restates the token. | "Do not let flow be negative." |

The test to apply to every candidate: **would a modeler opening this dialog for
the first time learn something they could not get from the name?** If not, drop
it. An empty field is better than a field that costs a read and returns nothing.

### Say no to volume

If the model has 40 rules and you propose 40 descriptions, the rubric was not
applied. Expect to propose for a **minority** of available targets. In the
review doc, state the ratio out loud (`18 proposed of 1,116 available`) so the
reviewer can see the restraint — or see that it is missing.

## Step 3 — write the two proposal artifacts

Write both next to the model:

**`<model>_annotations.md`** — the human review document. Every proposal,
numbered, with its target and a one-line rationale, grouped by surface. Lead
with the counts. End with the caveat from Step 5. Numbering is what makes
conversational approval work — the reviewer says "drop 4 and 9, reword 12."

```markdown
# Proposed annotations — saratoga_v2.4.mdl

18 annotations proposed, of 162 available targets. Nothing already described
is touched.

## Model description
1. **(model)** — "Saratoga is a two-reservoir river basin…"
   *Rationale: no one-line orientation exists anywhere in the file.*

## Object descriptions
2. **Pescado Fishery** — "Reach below Cora carrying the minimum fish flow…"
   *Rationale: the fishery is a policy target, not just a routing node.*

## Slot descriptions
…
## Rule and function descriptions
…
## Expression comments
…

## Skipped — already described (left untouched)
- Cora (object), Cora.Shortage Table, RULE "Find Shortage Level", the model
  description
```

**`<model>_annotations.json`** — the machine proposal, the same list in the
schema below. This is the *only* interface to the applier.

```json
[
  {"target_type": "model_description",  "target": "",
   "text": "Saratoga is a two-reservoir river basin…"},
  {"target_type": "object_description", "target": "Pescado Fishery",
   "text": "Reach below Cora carrying the minimum fish flow requirement."},
  {"target_type": "slot_description",   "target": "Roberto.Delivery Threshold",
   "text": "Below this pool elevation Roberto cannot pass releases downstream."},
  {"target_type": "rpl_description",    "target": "RPL Set/Cora Rules/Irrigation",
   "text": "Releases Cora water to meet the shortage-adjusted irrigation request."},
  {"target_type": "rpl_comment",        "target": "RPL Set/Cora Rules/Irrigation",
   "literal": "0.00000000 \"cms\"", "occurrence": 1,
   "text": "Do not let the release go negative."}
]
```

- `rpl_description` targets are paths: `"<Set>"`, `"<Set>/<Group>"`, or
  `"<Set>/<Group>/<Rule or Function>"`. Rule names repeat across groups
  (saratoga has `Prevent Overtopping` in two), so the full path is what
  disambiguates.
- `rpl_comment` also needs `literal` — the literal's exact serialized text,
  units included (`0.00000000 "cms"`, not `0`) — and optionally `occurrence`
  (1-based, default 1).
- **Text restrictions:** no `{`, `}`, `\`, or newlines anywhere; no `"` in
  `rpl_description` or `rpl_comment` text; 400 characters maximum. The applier
  rejects violations outright rather than guessing at an escape. Write plain
  single-line sentences and none of this comes up.
- **No provenance markers.** Approved annotations are the modeler's, endorsed
  by them. Annotation text never mentions AI, and never carries a "generated"
  tag. The review doc, the JSON, and git history are the audit trail.

## Step 4 — get approval, then apply

**Present the review doc and stop.** Do not run the applier on your own
initiative. The reviewer reads the numbered list and responds conversationally
— "drop 4 and 9, shorten 12, the rest are fine." Edit the JSON to match, say
what you changed, and only then:

```bash
# default: writes model_annotated.mdl next to the source, original untouched
python skills/annotate-riverware-model/annotate.py model.mdl model_annotations.json

# see what would happen without writing anything
python skills/annotate-riverware-model/annotate.py model.mdl model_annotations.json --dry-run

# edit the model itself -- only when the user asked for it
python skills/annotate-riverware-model/annotate.py model.mdl model_annotations.json --in-place
```

Default to the `_annotated.mdl` copy. Use `--in-place` only when the user asks
for it, or when the model is under version control and git history is the
before/after record — which is the pattern for this repository's own bundled
examples.

Read the applier's summary back to the user. It reports three tallies:

- `applied` — written.
- `skipped` — the target already had text. Expected and fine.
- `not found` — the target path did not resolve. **This is a bug in the
  proposal, not a warning to shrug at.** Exit code 4. Fix the path against the
  inventory and re-run; do not tell the user the annotation was applied.

## Step 5 — always end with the review caveat

End every run with words to this effect:

> Only RiverWare validates a `.mdl`. Load the annotated model in RiverWare and
> confirm the descriptions appear where they should — the open-object dialog,
> the slot dialog, the RPL editor's description tab — before trusting it or
> committing it.

---

## Guardrails

- **Never write into the `.mdl` without a review artifact and an approval.**
  The review doc must exist and the user must have responded to it. This is the
  whole reason the skill is two-phase; a single-shot annotate-and-done is the
  rejected alternative, not a shortcut.
- **Never overwrite an existing description or comment.** The applier enforces
  it, but do not propose it either. If you believe an existing description is
  wrong, say so in prose to the user; do not encode a replacement.
- **Never invent model facts.** Every description must be defensible from the
  digest, the rule bodies, or the model's own tables. If a slot's purpose is
  not determinable from what you have read, do not describe it — "probably a
  threshold for something" is worse than silence. Say which targets you skipped
  for this reason.
- **Do not describe a rule you have not read.** The digest lists rule names;
  names are not behavior. Read the body first, or leave it empty.
- **Restraint is the deliverable.** A short proposal that a modeler accepts
  wholesale is a better outcome than a long one they have to prune.

## Reference

- `reference.md` in this directory — the `.mdl` serialization grammar for every
  annotation surface: token forms, insertion anchors, escaping, line-ending
  discipline, and why a RiverWare re-save diff can never validate the applier.
- `skills/explain-riverware-model/SKILL.md` — the digest workflow Step 1 builds on.
- `skills/draft-riverware-rules/SKILL.md` — the working-directory rules and
  review-caveat pattern this skill inherits.
- `examples/TwoResOps/saratoga_v2.4_annotations.md` and
  `examples/ArborBasin/ArborBasin_annotations.md` — committed worked examples.
  Use them as the target shape and, more importantly, the target *volume*.
