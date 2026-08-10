# RiverWare-AI-Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-early%20development-orange)

**A public demonstration of how AI tools can interface with
[RiverWare](https://riverware.org).**

This repository is written for RiverWare modelers who are new to AI coding
tools. It demonstrates AI-assisted workflows that aid in:

- **Understanding model files** — AI agents that parse `.mdl` and `.rls`
  files and write plain-language narrative explanations of a model.
- **Visualizing models** — self-contained HTML dashboards of model
  structure and key time series.
- **Drafting policy rules** — turning a plain-language operating-policy
  request into a pasteable RPL rule.
- **Annotating models** — proposing descriptions for objects, slots, rules
  and functions, and comments on RPL expressions, for the modeler to review
  before they are written into the `.mdl`.
- **Live model control** — a prototype model context protocol
  ([MCP](https://modelcontextprotocol.io)) server that lets an AI agent set
  inputs, run RiverWare in batch mode, and read results back
  *(in development)*.

These tools are based on experimental tools developed for other RiverWare applications. Two example models are included here to demonstrate how the tools can be used, but the goal was to create tools for any RiverWare application.

> This repository is under active construction. The
> [upcoming work](#upcoming-work) section below tracks what is done and what
> is coming.

# Quick start

Instructions are included for [Claude Code](https://claude.com/claude-code) and [GitHub Copilot](https://github.com/copilot); other AI frameworks could also benefit from some of the tools in the repo, but they have not been tested.

## Claude Code

[Claude Code](https://claude.com/claude-code) is Anthropic's agentic coding
tool. It can read and edit repository files, run terminal commands, and carry
out multi-step coding tasks from natural-language prompts. In this repository,
it can follow the skills in `skills/` to analyze RiverWare models and generate
draft outputs. Two ways to get the skills:

**Option A — install as a plugin** (works from any directory):

The tools are available as a Claude Code plugin. This is a good option if you are already a user of RiverWare and Claude Code. This is the quickest option, and it is best if you already have a RiverWare project you'd like to explore with the tools.

First, add the marketplace:

```
/plugin marketplace add jrkasprzyk/RiverWare-AI-Tools
```

then from the marketplace, install the plugin:

```
/plugin install riverware-ai-tools@riverware-ai-tools
```

*Updating the plugin:* this repository is under active development, so the
plugin changes. Updating takes two steps, because the marketplace catalog is
cached separately from the installed plugin. First refresh the catalog:

```
/plugin marketplace update riverware-ai-tools
```

then update the plugin itself:

```
/plugin update riverware-ai-tools
```

Restart Claude Code for the new version to take effect. To check which
version you have, run `/plugin` and look at the installed plugin list, or run
`claude plugin list` from a terminal.

**Option B — clone the entire repository**:

If you would like access to the example RiverWare models and data, the best approach is to clone this repository:

```bash
git clone https://github.com/jrkasprzyk/RiverWare-AI-Tools.git
cd RiverWare-AI-Tools
claude
```

**Using the skills**:

Try:

> Explain the model in examples/ArborBasin/ArborBasin.mdl

## GitHub Copilot

The `skills/` folders use the same `SKILL.md` layout GitHub Copilot
consumes (see [github/awesome-copilot](https://github.com/github/awesome-copilot)).
Clone the repository, open it in [VS Code](https://code.visualstudio.com/) with Copilot enabled, and ask
Copilot to follow a skill, e.g.:

> Follow skills/explain-riverware-model/SKILL.md to explain
> examples/ArborBasin/ArborBasin.mdl

**Other AI tools:** any agent that can read files and run Python can use
these skills — point it at [AGENTS.md](AGENTS.md).

# Contents

## Skills

| Skill | What it does | Status |
|-------|--------------|--------|
| [explain-riverware-model](skills/explain-riverware-model/SKILL.md) | Parse a `.mdl`/`.rls` file and write a narrative explanation of the model | Available |
| [visualize-riverware-model](skills/visualize-riverware-model/SKILL.md) | Render model structure and key series as a self-contained HTML dashboard | Available |
| [draft-riverware-rules](skills/draft-riverware-rules/SKILL.md) | Draft a pasteable RPL rule from a plain-language policy request | Available |
| [annotate-riverware-model](skills/annotate-riverware-model/SKILL.md) | Propose descriptions and RPL comments for a model, then apply the approved set to the `.mdl` | Available |
| [riverware-help](skills/riverware-help/SKILL.md) | Interactive RiverWare help — answers grounded in the CADSWES CurrentVersion online help, with cited pages and model-aware context | Available |
| [comment-cleanup](skills/comment-cleanup/SKILL.md) | Strip changelog-style and repeated comments from AI-written code, document every tuning parameter with its range, default and units, and write the result in Simplified Technical English | Available |

## Examples

| Model | Description | Outputs |
|-------|-------------|---------|
| [ArborBasin](examples/ArborBasin/) | The CADSWES RiverWare training model | [Narrative](examples/ArborBasin/ArborBasin_explained.md) · [Live dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/ArborBasin/ArborBasin_dashboard.html) · [Rule case study](examples/ArborBasin/ArborBasin_rule_case_study.md) · [Annotation review](examples/ArborBasin/ArborBasin_annotations.md) |
| [TwoResOps](examples/TwoResOps/) | Saratoga, a two-reservoir operations testbed | [Narrative](examples/TwoResOps/saratoga_v2.4_explained.md) · [Live dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/TwoResOps/saratoga_v2.4_dashboard.html) · [Rule case study](examples/TwoResOps/saratoga_v2.4_rule_case_study.md) · [Annotation review](examples/TwoResOps/saratoga_v2.4_annotations.md) |

All examples are also browsable from the
[GitHub Pages site](https://jrkasprzyk.github.io/RiverWare-AI-Tools/).
Committed example outputs are produced with these skills and then
human-polished into finished documentation.

## Live-model control (MCP prototype)

[`prototypes/riverware-mcp/`](prototypes/riverware-mcp/) holds an
experimental model context protocol (MCP) server wrapping RiverWare batch mode with tools
`list_objects`, `list_slots`, `set_slots`, `run_model`, and `read_slots`.
These tools allow an AI agent to perturb inputs, rerun a model, and compare
results.

An initial verification was completed using RiverWare 9.7; see the
[demo transcript](prototypes/riverware-mcp/demo_transcript.md) of a
set → run → read policy experiment. A license is required to run RiverWare
with these tools.

# Upcoming Work

- [ ] Verified GitHub Copilot walkthrough
- [ ] Editing example model descriptions and fine-tuning skills
- [ ] Verify the annotated example models load cleanly in RiverWare
- [ ] Widen `COMMENTED_BY` targeting beyond numeric literals, and encode
      quotes in RPL description text as `&quot;` rather than rejecting them

# Contributing

We welcome contributions, including new examples, modifications to skills, and new tools. See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the
[MIT License](LICENSE).
