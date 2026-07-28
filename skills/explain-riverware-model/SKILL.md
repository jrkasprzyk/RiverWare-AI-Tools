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
 
**Do not read the raw `.mdl` line by line.** A `.mdl` here is ~6700 lines and blows
the Read token limit. Run the driver instead; it gives you everything narratable in
~500 lines.

Paths below are relative to the repo root (`C:\Github\BorgRWProblems`).

## Step 1 — extract the skeleton (the driver)

`.claude/skills/explain-riverware-model/explain.py` (Python 3.12, stdlib only).

```bash
# from a problem folder, e.g. NorthSouth/
python ../.claude/skills/explain-riverware-model/explain.py NorthSouth20250805.mdl NorthSouth20250805.rls
```

Pass either file alone or both together (order does not matter — the extension picks
the parser). Add `--json` for machine-readable output.

What it pulls out:

- **From `.mdl`:** RiverWare version, run horizon + timestep, object count; every
  simulation object with its type, description, *selected* simulation methods (the
  `None`/`No Method` ones are dropped), and its slots grouped by slot type; the
  rule-curve / lookup tables (`TableSlot`, `PeriodicSlot`) with column labels, row
  count, and a 3-row sample; DMIs, embedded RPL sets, and model scripts.
- **From `.rls`:** (if stored in a separate file) ruleset name, agenda order, precision, 
  description; every policy group and utility group with its active flag; every rule 
  and function with its active flag, notes, and full RPL body.

Redirect long output to the scratchpad if you want to grep it (take note of hard-coded paths
in the below snippet, which may need to be changed if ran on a different machine):

```bash
SC="C:/Users/joka0958/AppData/Local/Temp/claude/C--Github-BorgRWProblems/<session>/scratchpad"
python ../.claude/skills/explain-riverware-model/explain.py NorthSouth20250805.mdl NorthSouth20250805.rls > "$SC/digest.txt"
```

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
   read and write; call out any slots an optimizer writes via DMI.
4. **Ruleset** — respect agenda order: **`ASCENDING` means the bottom rule in a group
   fires first. This is the default behavior. It should not be mentioned in the narrative unless there
   is a very good reason to do so.** List each active group's rules in execution order and say what each
   does. Flag inactive groups/rules as retained history, not live policy.
5. **How it connects** — tie the DMI-written slots and Objectives slots to the
   optimization loop. Note that many of the models you'll be working on are wired for Borg, so don't act like
   it's a special thing that Borg reads outputs, etc. Focus on the names of the objectives, constraints, and metrics.

House style (from `.documentation/.claude/commands/riverware-doc-edit.md`) — apply it
even though the output is narrative, not the strict doc format. See notes and exceptions below:

- **Capitalize** named objects and slots (Pool Elevation, `NorthRC.Zone Reductions`);
  **lowercase** generic types (reservoir, reach, data object, rule, policy group).
- No contractions
- Latin abbreviations are allowed (e.g., "e.g.")
- One word: "timestep", "streamflow".
- Cross-check names and counts against the digest; do not invent slots.

Cross-reference the problem folder's `README.md` and the project memories
(`memory/project-overview.md`, `.plan/` handoffs) for optimization context the files
themselves do not state. For RiverWare object/method/RPL semantics, the online help
is authoritative: https://riverware.org/HelpSystem/CurrentVersion/index.html

However, **do not** mention what changed, or development notes that you know from memory. Act as if the model
is a monolithic thing that is being described and not changed.

Unless otherwise instructed, save the narrative next to the same folder as the model file as `<modelname>_explained.md`.

## Worked example

`NorthSouth/NorthSouth20250805_explained.md` is a finished narrative produced this
way from `NorthSouth20250805.mdl` + `NorthSouth20250805.rls`. Use it as the target
shape and depth.

## Gotchas

- **The `.mdl` will not fit in Read.** ~6700 lines / 160k tokens. Always go through
  the driver; only Read narrow line ranges (via `sed -n` in Bash) if you need to
  verify a specific block the driver summarized.
- **Agenda order is bottom-up.** `AGENDA_ORDER ASCENDING` fires the *last* rule
  listed in a group first. Narrating rules top-to-bottom describes the wrong
  execution order — reverse them.
- **Selected methods are the signal.** A Storage Reservoir lists ~25 selected
  methods but the vast majority are numeric-solve defaults (Substitution/Tangent).
  The narrative-worthy ones are the physical choices: `Spill`, `Hydrologic Inflow`,
  `Routing`, `Diversion...`. The driver already drops `None`/`No Method`; you still
  summarize rather than list all of them.
- **`.mdl` embeds RPL too.** Initialization/MRM rule sets are stored inside the
  `.mdl` (you will see `IF_STATEMENT` lines there). The *operating* policy is the
  external `.rls`; do not confuse the two.
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
