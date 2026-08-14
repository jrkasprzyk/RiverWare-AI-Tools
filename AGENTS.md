# Agent guide — RiverWare-AI-Tools

Entry point for any AI agent working in this repository.

## Repository layout

```
skills/                      One folder per skill: SKILL.md + helper scripts
  explain-riverware-model/   Narrative explanation of .mdl/.rls files
  visualize-riverware-model/ Self-contained interactive HTML dashboard
  draft-riverware-rules/     Draft a pasteable RPL policy rule
  annotate-riverware-model/  Propose + apply model descriptions and comments
  comment-cleanup/           Comment hygiene for source code (language-agnostic)
  report-cleanup/            Rewrite rambling bug reports into structured write-ups
examples/                    RiverWare models + committed skill outputs
  ArborBasin/                CADSWES training model
  TwoResOps/                 Two-reservoir operations model (saratoga)
prototypes/                  Experimental integrations (MCP server)
tests/                       Parser and applier regression tests
docs/                        Integration documentation
.claude-plugin/              Claude Code plugin + marketplace manifests
.claude/skills/              Thin bridges so cloned repos expose the skills
```

Run the tests from the repo root with `python -m unittest discover -s tests`.

## The one hard rule: never read a `.mdl` raw

RiverWare `.mdl` files here are 1.6–1.9 MB Tcl scripts — tens of thousands
of lines. Do not read them start to finish; they will not fit in context.
Always go through the parser:

```bash
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl
```

This emits a structural digest (~500 lines): objects, slots, selected
methods, rule-curve tables, DMIs, and embedded RPL rulesets. Add `--json`
for machine-readable output, or `--annotations` for an inventory of every
description field and whether one is already written. Read narrow line
ranges of the raw file only to verify a specific block the digest
summarized.

## Using the skills

Each skill is self-documenting — read its `SKILL.md` and follow it:

- `skills/explain-riverware-model/SKILL.md` — write a plain-language
  narrative explanation of a model and its ruleset.
- `skills/visualize-riverware-model/SKILL.md` — render a model as a
  self-contained HTML dashboard (schematic, lookup tables, key series).
- `skills/draft-riverware-rules/SKILL.md` — draft a pasteable RPL rule from
  a plain-language policy request, and say where it belongs in the agenda.
- `skills/annotate-riverware-model/SKILL.md` — propose descriptions and RPL
  comments for a model, then apply the approved set to the `.mdl`. Never
  writes to a model without a review artifact and the user's approval.
- `skills/riverware-help/SKILL.md` — answer a RiverWare usage, RPL, DMI, SCT,
  accounting or optimization question from the CADSWES CurrentVersion online
  help, citing the exact page. For a question about the user's own model,
  ground the answer in the digest as well.
- `skills/comment-cleanup/SKILL.md` — comment hygiene for source code, not
  models: no change history in comments, few comments, every tuning parameter
  documented with range, default, units and effect, and all comments written
  in Simplified Technical English. These rules apply to any code written in
  this repository, not only when the skill is invoked.
- `skills/report-cleanup/SKILL.md` — rewrite a rambling bug report or issue
  into Summary/Repro/Hypothesis/Asks, relabeling the writer's own guess as an
  unconfirmed hypothesis instead of promoting it to fact. Uses RiverWare
  vocabulary (Object.Slot references, RPL rule names, Rule Log, DMI, agenda
  order) to tell an observed symptom from a suspected cause.

Skills follow a common pattern: a Python parser (3.10+, stdlib) extracts a
digest; the SKILL.md tells you how to turn the digest into the deliverable;
a worked example in `examples/` shows the target shape and depth.

## Conventions

- Scripts must print ASCII-safe output (Windows cp1252 consoles).
- Cross-platform: everything runs on Windows, macOS, and Linux.
- Stay inside the working directory. A `.mdl` records the path of the `.rls`
  ruleset it last loaded, and that path routinely points elsewhere on the
  user's machine — a network share, a sync folder, a client's directory.
  Report the path and ask for the file; finding a path inside a model file is
  not permission to go read it. If the digest lists no `Rule Based Simulation`
  set, the operating policy is in such a file and you have not seen it.
  The same applies to a file the user named that is not there: if a close
  match sits in the working directory, offer it and stop. Do not scan parent
  directories or sibling projects for a matching name.
- Example outputs committed under `examples/` are polished documentation —
  match their quality if you regenerate or extend them.
