---
name: present-riverware-model
description: Create a PowerPoint presentation, slide deck, or briefing that explains a RiverWare model — use when asked for slides, a deck, a .pptx, or a presentation about a model.
---

# Present a RiverWare model

The deliverable is a `.pptx` a modeler can walk a room through, or drop into a
briefing someone else is already building. It is not a dashboard with slide
breaks: a stakeholder meeting rewards a story about how the system is operated,
and punishes an inventory of everything the model contains.

The work splits in two. **You write a deck-spec JSON** — which slides exist, in
what order, what each one shows, and what it says. **`build_pptx.py` renders
it** from the model's own digest and makes no editorial decisions at all. The
spec is the reviewable artifact: it is short, it is readable, and the modeler
can see what the deck will claim before it exists.

**Prerequisite:** `pip install "python-pptx>=0.6.21"`. The script exits with
that message if it is missing. Say so early rather than at the end of the work.

Paths below are relative to the root of this repository. If this skill was
installed as a **plugin**, that root is `${CLAUDE_PLUGIN_ROOT}` and the working
directory is the user's own project — prefix the script and `examples/` paths
with it. The `.mdl` the user asks about is their own file and is not under that
root.

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
comes from the parser.

---

## Step 1 — digest the model

Two views. The narrative digest tells you what the model *is*; the deck digest
tells you exactly which objects, series, tables and rule groups a slide is
allowed to reference.

```bash
# cloned repository, run from the repo root
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl
python skills/visualize-riverware-model/digest_to_json.py examples/ArborBasin/ArborBasin.mdl --policy

# installed as a plugin, run from anywhere
python "${CLAUDE_PLUGIN_ROOT}/skills/explain-riverware-model/explain.py" path/to/model.mdl
python "${CLAUDE_PLUGIN_ROOT}/skills/visualize-riverware-model/digest_to_json.py" path/to/model.mdl --policy
```

The `--policy` digest is what the spec must agree with. Its keys:

- `objects` — every simulation object, with type and description
- `links` — topology, oriented upstream to downstream
- `tables` — full numeric rows for the whitelisted lookup tables
- `series` — stored results for the curated result slots. **An empty list means
  the model was saved without results**, which is normal, and means the deck
  has no evidence section.
- `policy.sets` — rule sets, groups and rules in agenda order
- `policy.referenced_files` — `.rls` paths the model records. Report them; do
  not open them.

## Step 2 — ask before you aim

A deck aimed at the wrong audience is wasted work, and a deck is harder to
re-aim than a document. Ask once, as one structured set of questions, and then
get on with it:

1. **Audience** — stakeholders and decision makers, or fellow modelers? This
   sets how much RPL vocabulary the deck can use.
2. **Length** — roughly how many slides, or how long is the slot?
3. **Emphasis** — the operating policy, the results, or the physical system?
4. **Template** — is there a client or agency `.pptx` whose theme the deck must
   inherit?
5. **Ruleset** — ask only when `policy.sets` is empty: the model carries no
   embedded rule set, so is a `.rls` available? Name the paths the model
   records, and ask for the file rather than going to find it.

If a ruleset is not available, say plainly that the deck will describe the
model's structure and not its operating policy. The renderer puts a visible
"Ruleset not included" note on the summary slide. A deck that is quietly
thinner than it should be is worse than one that says why.

## Step 3 — write the spec

**This step is the skill.** The renderer is mechanical; deciding what the room
needs to see is not.

Build a story, in this shape, sized to the model and the answers from Step 2.
Ten to fifteen slides is typical:

1. **Orient** — title, then the network schematic, then a short summary. Three
   slides that let someone place the system before you make a claim about it.
2. **Explain the policy** — usually the highest-value section. One `policy`
   slide per few rule groups, each rule given a one-line `annotations` entry in
   plain language. This is where a stakeholder learns how the system is
   actually operated.
3. **Show the evidence** — `series` slides for the results that bear on the
   question being asked. Two to four series per chart; more is a wall.
4. **Close** — the `caveats` slide, always last.

Physical-data slides (`table`, `chart-xy` — elevation-volume curves, max
release tables) are available and are **not** part of the default story. Add
them when the physical data *is* the point: a re-survey changed a curve, a
storage limit is the constraint under discussion. Otherwise they are detail the
room did not ask for.

`reference.md` in this directory is the authoritative schema: every slide type,
its `refs`, and the exact reference formats. Read it before writing a spec.

### The grounding rule

**Every claim in the spec must be supported by the digest.** Bullets, policy
one-liners and notes describe what the model contains — objects, links, rule
names, agenda order, stored values. They must not assert operational outcomes
the model file does not show, attribute intent to whoever built it, or restate
something the user told you in conversation. Decks get forwarded far past the
room they were made for; anything in this file has to survive that.

If a claim needs a fact the digest does not carry, either drop the claim or ask
the modeler and attribute it to them.

### Speaker notes

Notes are **factual annotations, not a talk track**. The renderer already
writes a provenance line naming the source `Object.Slot`, the row or point
counts, and the relevant caveat. Add to it only what a reader needs to check
the slide: a unit, a definition, a known limitation. Do not write a spoken
script — the deck will be forwarded, and a script reads as someone else's words
in the recipient's mouth.

## Step 4 — render

```bash
python skills/present-riverware-model/build_pptx.py examples/ArborBasin/ArborBasin.mdl \
    --spec ArborBasin_deck.json -o examples/ArborBasin/ArborBasin_deck.pptx

# with a client template, and with an external ruleset
python skills/present-riverware-model/build_pptx.py path/to/model.mdl \
    --spec deck.json --template client.pptx --rls policy.rls
```

`--auto` renders a generic baseline deck with no spec at all, and writes the
spec it used next to the deck. Use it as a smoke test, or as a starting point
to edit — not as a deliverable, because it makes no claim about what matters.

If the spec references something the model does not have, the run prints every
problem with the valid targets, exits non-zero, and writes nothing. Fix the
spec; there is no partial deck to clean up.

Read the warnings. A crowded schematic, a dropped legend entry, a chart mixing
units, and a template whose layouts could not be found are all reported on
stdout, and all of them are things to tell the user about rather than bury.

## Step 5 — review before delivering

Open the deck and check:

1. **The schematic is readable when projected.** The layered layout is a
   starting point; nodes are movable in PowerPoint and the connectors follow.
   If it is tangled or the labels are tiny, say so and offer to split it across
   two `network` slides with `refs.objects` — do not present it as final.
2. **The charts look like results** — seasonal shape, sensible ranges — not
   initialization placeholders. Elevation-volume curves should rise
   monotonically; a jagged one usually means a row failed to parse.
3. **The policy slides match the agenda.** For an `ASCENDING` set the bottom
   rule fires first, and a rule listed higher fires later and overrides it. The
   numbers on the slide are agenda positions, not execution order.
4. **The notes read as annotations**, and contain nothing from the conversation
   that is not in the model.
5. **The template took.** Compare against the client deck: fonts, colours,
   title placement. Anything the renderer could not infer is a hand fix, and
   the warnings say where to look.

Deliver the spec alongside the deck. It is the artifact that shows what was
claimed and where it came from, and it is what the modeler edits when they want
the next version.

Unless told otherwise, save the deck next to the model as
`<modelname>_deck.pptx` and the spec as `<modelname>_deck.json`.

## Worked example

`examples/ArborBasin/ArborBasin_deck.pptx`, built from
`examples/ArborBasin/ArborBasin_deck.json` by the command in Step 4. Open both
together to see the target: a short spec, and the deck it produces.

## Gotchas

- **No results is not an error.** A model saved without a run has an empty
  `series` list. Build the structure-and-policy deck and say the evidence
  section is missing, rather than hunting for numbers.
- **Link direction is inferred.** RiverWare links are undirected; the digest
  orients an edge by which end is an `Inflow` slot. Head and data links are
  drawn dashed.
- **Aggregate element names contain colons** (`Mulberry Irrigation:District 1`).
  Only the first `.` separates object from slot.
- **Long series are thinned.** Past 400 points the chart is sampled at a fixed
  stride and the notes say so.
- **Templates are best effort.** Layouts are matched by name, then position,
  then whatever the file has. Section 6 of `reference.md` has the details.
- **Only PowerPoint validates a `.pptx`.** A clean run is not proof the deck
  opens. Section 8 of `reference.md` records what has actually been checked.
