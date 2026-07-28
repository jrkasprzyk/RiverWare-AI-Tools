---
name: explain-riverware-model
description: Write a plain-language narrative explanation of a RiverWare model (.mdl) and/or ruleset (.rls) — what objects, slots, rule curves, DMIs, and policy rules the file contains and how they operate together. Use when asked to explain, summarize, document, walk through, or describe a RiverWare .mdl or .rls file.
---

# Explain a RiverWare model / ruleset

This skill produces a **narrative
explanation** — flowing prose a modeler can read — by first extracting a structural
digest with a parser, then narrating it with RiverWare domain knowledge.

RiverWare `.mdl` files are Tcl scripts (thousands of lines) and `.rls` rulesets are
RPL text. In some models, there is a separate `.rls` file, but in other models, the rules
are embedded in the model file. This is not an important detail and should **not** be overemphasized
in the explanation.

**Do not read the raw `.mdl` line by line.** The `.mdl` files in this repository are
1.6–1.9 MB (tens of thousands of lines) and blow the Read token limit. Run the driver
instead; it gives you everything narratable in a few hundred lines.

Paths below are relative to the root of this repository. If this skill was
installed as a **plugin**, that root is `${CLAUDE_PLUGIN_ROOT}` and the working
directory is the user's own project — prefix the script and `examples/` paths
with it. The `.mdl` the user asks about is their own file and is not under that
root.

## Step 1 — extract the skeleton (the driver)

`skills/explain-riverware-model/explain.py` (Python 3.10+, stdlib only). It
resolves its own imports from its own location, so it runs from any working
directory.

```bash
# cloned repository, run from the repo root
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl

# installed as a plugin, run from anywhere
python "${CLAUDE_PLUGIN_ROOT}/skills/explain-riverware-model/explain.py" path/to/your/model.mdl
```

Pass a `.mdl` alone, a `.rls` alone, or both together (order does not matter — the
extension picks the parser). Add `--json` for machine-readable output.

What it pulls out:

- **From `.mdl`:** RiverWare version, run horizon + timestep, object count; every
  simulation object with its type, description, *selected* simulation methods (the
  `None`/`No Method` ones are dropped), and its slots grouped by slot type; the
  rule-curve / lookup tables (`TableSlot`, `PeriodicSlot`) with column labels, row
  count, and a 3-row sample; DMIs, embedded RPL sets, and model scripts.
- **From `.rls`:** (if stored in a separate file) ruleset name, agenda order, precision,
  description; every policy group and utility group with its active flag; every rule
  and function with its active flag, notes, and full RPL body.

If the output is long, redirect it to a temporary file of your choice and grep it:

```bash
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl > digest.txt
```

## Step 1b — when the operating policy is not in the model

Read the digest's **Embedded RPL sets** list before narrating. If it has no
`Rule Based Simulation` set — only `Initialization Rules`, `MRM Rules`,
`Expression Slots`, `Global Functions` — then the model's operating policy
lives in a separate `.rls` you have not read. The digest cannot tell you
whether that model has no policy or a policy you are missing, and those are
very different models.

**Stay inside the working directory.** The `.mdl` records the path of the
ruleset it last loaded, and that path routinely points somewhere else on the
user's machine — a network share, a sync folder, a client's directory. Report
the recorded path and ask the user to supply the file. Do not go read it on
your own initiative, and do not treat a path you found inside the `.mdl` as
permission to leave the project.

If the user declines or the file is unavailable, narrate the model anyway and
state plainly, in the ruleset section, that the operating policy was not
available and what the model records about it. **Do not reconstruct the policy
from slot names, object descriptions, or rule-curve tables** — that produces
confident prose about rules that may not exist, which is the one failure this
skill must not have.

## Step 2 — narrate the digest

Turn the digest into prose. The digest is accurate structure; you supply the meaning.
Structure the narrative roughly as:

1. **Overview** — what the system is (count and kind of reservoirs/reaches/gages),
   the run horizon and timestep. Assume the reader understands the physics of a RiverWare
   simulation and the fact that most RiverWare models will have a ruleset either embedded in
   the model file (`.mdl`) or in a separate ruleset file (`.rls`). **Do not** explain the RiverWare
   simulation engine or RPL language itself, and avoid "salesman" language like "RiverWare is a
   powerful tool for water resources management." Focus on the specific model and ruleset being
   explained.
2. **Physical network** — walk the objects top of watershed to bottom. Keep in mind that all RiverWare
   reservoirs are going to have things like a elevation-volume table, max-release, etc. Focus on important
   elevations in these tables (e.g. Dead Pool, Max Elevation), not how many rows the table has.
3. **Data / rule-curve objects** — the `...RC` and `...Data` objects that the rules
   read and write; call out any slots an external tool writes via DMI.
4. **Ruleset** — respect agenda order: **`ASCENDING` means the bottom rule in a group
   fires first. This is the default behavior. It should not be mentioned in the narrative unless there
   is a very good reason to do so.** List each active group's rules in execution order and say what each
   does. Flag inactive groups/rules as retained history, not live policy.
5. **How it connects** — if the model is wired to an external optimizer or a
   DMI-driven workflow, name the objective, constraint, and metric slots involved and
   the DMIs that read or write them. Treat the external tool matter-of-factly; the
   interesting content is which slots carry the exchange.

House style — apply it even though the output is narrative, not a strict doc format:

- **Capitalize** named objects and slots (Pool Elevation, `Cedar.Diversion Min Elevation`);
  **lowercase** generic types (reservoir, reach, data object, rule, policy group).
- No contractions
- Latin abbreviations are allowed (e.g., "e.g.")
- One word: "timestep", "streamflow".
- Cross-check names and counts against the digest; do not invent slots.

Cross-reference the model folder's `README.md` (if present) for context the model file
itself does not state. For RiverWare object/method/RPL semantics, the online help
is authoritative: https://riverware.org/HelpSystem/CurrentVersion/index.html

Describe the model as it stands — a finished artifact. **Do not** narrate development
history, changes, or context that is not present in the files themselves.

Unless otherwise instructed, save the narrative next to the same folder as the model file as `<modelname>_explained.md`.

## Worked example

`examples/ArborBasin/ArborBasin_explained.md` is a finished narrative produced this
way from `examples/ArborBasin/ArborBasin.mdl`. Use it as the target shape and depth.

## Gotchas

- **The `.mdl` will not fit in Read.** Always go through the driver; only Read narrow
  line ranges (via `sed -n` in Bash) if you need to verify a specific block the driver
  summarized.
- **Agenda order is bottom-up.** `AGENDA_ORDER ASCENDING` fires the *last* rule
  listed in a group first. Narrating rules top-to-bottom describes the wrong
  execution order — reverse them.
- **Selected methods are the signal.** A Storage Reservoir lists ~25 selected
  methods but the vast majority are numeric-solve defaults (Substitution/Tangent).
  The narrative-worthy ones are the physical choices: `Spill`, `Hydrologic Inflow`,
  `Routing`, `Diversion...`. The driver already drops `None`/`No Method`; you still
  summarize rather than list all of them.
- **`.mdl` embeds RPL too.** Both example models in this repository embed their
  rulesets in the `.mdl`: the operating policy lives in a `loadedSet` block, and
  initialization/MRM rule sets are stored alongside it (you will see `IF_STATEMENT`
  lines there). When a separate `.rls` exists, that file is the operating policy;
  either way, distinguish the operating policy from the init/MRM sets.
- **Descriptions contain `<br>`.** The driver strips them; if you Read raw blocks
  yourself, expect HTML line breaks inside `userDescript` / `DESCRIPTION` text.
- **Console encoding.** The driver emits ASCII (`--`, not em-dash) so it prints
  cleanly on the Windows cp1252 console. Keep it that way if you edit the renderer.

## Troubleshooting

- `error: <file> is not .mdl or .rls` — the driver dispatches on file extension only.
  Rename or pass the correct file.
- Empty `objects: 0` or missing rules — the file may be a newer RiverWare format.
  Check the `# RiverWare_Model <version>` / `# RiverWare_Ruleset <version>` header
  line and confirm the object marker is still `$ws SimObj $obj {...}` and rules still
  use `POLICY_GROUP` / `RULE` keywords. Verified against RiverWare 9.6.3 (model) and
  9.5 (ruleset) file formats.
