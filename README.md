# RiverWare-AI-Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-early%20development-orange)

**A public demonstration of how AI tools can interface with
[RiverWare](https://riverware.org) — today and in the future.**

This repository is written for RiverWare modelers who are new to AI coding
tools. It assumes you know RiverWare (models, slots, RPL rulesets, batch
mode) and walks you through the AI side step by step. It demonstrates:

- **Understanding model files** — AI agents that parse `.mdl` and `.rls`
  files and write plain-language narrative explanations of a model.
- **Visualizing models** — self-contained HTML dashboards of model
  structure and key time series.
- **Drafting policy rules** — turning a plain-language operating-policy
  request into a pasteable RPL rule.
- **Live model control** — a prototype [MCP](https://modelcontextprotocol.io)
  server that lets an AI agent set inputs, run RiverWare in batch mode, and
  read results back *(in development)*.

This is a general AI + RiverWare demonstration. It is not tied to any
particular optimizer or downstream tool.

> **Building in the open.** This repository is under active construction.
> The [roadmap](#roadmap) section below tracks what is done and what is
> coming.

## Quick start — Claude Code

[Claude Code](https://claude.com/claude-code) is Anthropic's agentic coding
tool. Two ways to get the skills:

**Option A — install as a plugin** (works from any directory):

```
/plugin marketplace add jrkasprzyk/RiverWare-AI-Tools
/plugin install riverware-ai-tools@riverware-ai-tools
```

**Option B — clone and open** (good if you also want the example models):

```bash
git clone https://github.com/jrkasprzyk/RiverWare-AI-Tools.git
cd RiverWare-AI-Tools
claude
```

Either way, the skills become available automatically. Try:

> Explain the model in examples/ArborBasin/ArborBasin.mdl

## Quick start — GitHub Copilot

The `skills/` folders use the same `SKILL.md` layout GitHub Copilot
consumes (see [github/awesome-copilot](https://github.com/github/awesome-copilot)).
Clone the repository, open it in VS Code with Copilot enabled, and ask
Copilot to follow a skill, e.g.:

> Follow skills/explain-riverware-model/SKILL.md to explain
> examples/ArborBasin/ArborBasin.mdl

*A fully verified Copilot walkthrough is on the roadmap.*

**Other AI tools:** any agent that can read files and run Python can use
these skills — point it at [AGENTS.md](AGENTS.md).

## Skills

| Skill | What it does | Status |
|-------|--------------|--------|
| [explain-riverware-model](skills/explain-riverware-model/SKILL.md) | Parse a `.mdl`/`.rls` file and write a narrative explanation of the model | Available |
| [visualize-riverware-model](skills/visualize-riverware-model/SKILL.md) | Render model structure and key series as a self-contained HTML dashboard | Available |
| [draft-riverware-rules](skills/draft-riverware-rules/SKILL.md) | Draft a pasteable RPL rule from a plain-language policy request | Available |

## Examples

| Model | Description | Outputs |
|-------|-------------|---------|
| [ArborBasin](examples/ArborBasin/) | The CADSWES RiverWare training model | [Narrative](examples/ArborBasin/ArborBasin_explained.md) · [Live dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/ArborBasin/ArborBasin_dashboard.html) · [Rule case study](examples/ArborBasin/ArborBasin_rule_case_study.md) |
| [TwoResOps](examples/TwoResOps/) | Saratoga, a two-reservoir operations testbed | [Narrative](examples/TwoResOps/saratoga_v2.4_explained.md) · [Live dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/TwoResOps/saratoga_v2.4_dashboard.html) · [Rule case study](examples/TwoResOps/saratoga_v2.4_rule_case_study.md) |

All examples are also browsable from the
[GitHub Pages site](https://jrkasprzyk.github.io/RiverWare-AI-Tools/).
Committed example outputs are produced with these skills and then
human-polished into finished documentation.

## Live-model control (MCP prototype)

[`prototypes/riverware-mcp/`](prototypes/riverware-mcp/) holds an
experimental MCP server wrapping RiverWare batch mode with tools
`list_objects`, `list_slots`, `set_slots`, `run_model`, and `read_slots` —
enough for an AI agent to perturb inputs, rerun a model, and compare
results. Verified live against RiverWare 9.7; see the
[demo transcript](prototypes/riverware-mcp/demo_transcript.md) of a real
set → run → read policy experiment. It requires a licensed local RiverWare
installation.

## Roadmap

- [x] Repository scaffold and Claude Code plugin packaging
- [x] Portable explain skill + first polished example (ArborBasin)
- [x] Visualization skill + dashboards on GitHub Pages
- [x] Rule-drafting skill + request→rule case studies
- [x] MCP server prototype (live batch-mode control, verified on RiverWare 9.7)
- [ ] Integration overview: `docs/ai-riverware-integration.md`
- [ ] Verified GitHub Copilot walkthrough + CI

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the
[MIT License](LICENSE).
