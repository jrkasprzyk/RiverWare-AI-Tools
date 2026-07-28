# Copilot instructions — RiverWare-AI-Tools

This repository demonstrates AI tools interfacing with RiverWare water-resources
models. Key rules for working here:

## Never read a `.mdl` file raw

RiverWare `.mdl` files under `examples/` are 1.6–1.9 MB generated Tcl scripts —
tens of thousands of lines that will not fit in context. Always go through the
parser:

```bash
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl
```

Read narrow line ranges of a raw `.mdl` only to verify a specific block the
parser digest summarized.

## Use the skills

Task-specific instructions live in `skills/<name>/SKILL.md` — read the relevant
one and follow it:

- `skills/explain-riverware-model/SKILL.md` — narrative model explanations
- `skills/visualize-riverware-model/SKILL.md` — self-contained HTML dashboards
- `skills/draft-riverware-rules/SKILL.md` — drafting RPL policy rules

Each skill delegates heavy lifting to a bundled Python script (3.10+, stdlib)
and points at a committed worked example in `examples/` showing the target
quality.

## Conventions

- Scripts print ASCII-safe output (Windows cp1252 consoles) and run on
  Windows/macOS/Linux.
- RiverWare rulesets use `AGENDA_ORDER ASCENDING`: the bottom rule of a
  listing fires first, so later-firing rules override earlier ones.
- Never invent RiverWare slot names — the parser digest is the source of
  truth.
- Committed outputs in `examples/` are polished documentation; match their
  quality when regenerating.
- Commits follow Conventional Commits (`type(scope): imperative subject`).
