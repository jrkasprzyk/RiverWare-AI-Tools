# Agent guide — RiverWare-AI-Tools

Entry point for any AI agent working in this repository.

## Repository layout

```
skills/                      One folder per skill: SKILL.md + helper scripts
  explain-riverware-model/   Narrative explanation of .mdl/.rls files
examples/                    RiverWare models + committed skill outputs
  ArborBasin/                CADSWES training model
  TwoResOps/                 Two-reservoir operations model (saratoga)
prototypes/                  Experimental integrations (MCP server)
docs/                        Integration documentation
.claude-plugin/              Claude Code plugin + marketplace manifests
.claude/skills/              Thin bridges so cloned repos expose the skills
```

## The one hard rule: never read a `.mdl` raw

RiverWare `.mdl` files here are 1.6–1.9 MB Tcl scripts — tens of thousands
of lines. Do not read them start to finish; they will not fit in context.
Always go through the parser:

```bash
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl
```

This emits a structural digest (~500 lines): objects, slots, selected
methods, rule-curve tables, DMIs, and embedded RPL rulesets. Add `--json`
for machine-readable output. Read narrow line ranges of the raw file only
to verify a specific block the digest summarized.

## Using the skills

Each skill is self-documenting — read its `SKILL.md` and follow it:

- `skills/explain-riverware-model/SKILL.md` — write a plain-language
  narrative explanation of a model and its ruleset.

Skills follow a common pattern: a Python parser (3.10+, stdlib) extracts a
digest; the SKILL.md tells you how to turn the digest into the deliverable;
a worked example in `examples/` shows the target shape and depth.

## Conventions

- Scripts must print ASCII-safe output (Windows cp1252 consoles).
- Cross-platform: everything runs on Windows, macOS, and Linux.
- Example outputs committed under `examples/` are polished documentation —
  match their quality if you regenerate or extend them.
