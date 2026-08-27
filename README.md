# RiverWare-AI-Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-early%20development-orange)

**An exploratory demonstration of how AI tools can interface with
[RiverWare](https://riverware.org).**

This experimental repository shows how tools like Claude Code can aid in RiverWare modeling workflows. It is an exploratory project led by Prof. Joseph Kasprzyk at CADSWES. The tools are not an official part of any CADSWES software.

Demos include:

- **Understanding model files** — AI agents that parse `.mdl` and `.rls`
  files and write plain-language narrative explanations of a model.
- **Visualizing models** — self-contained HTML dashboards of model
  structure and key time series.
- **Drafting policy rules** — turning a plain-language operating-policy
  request into RPL rule logic.
- **Annotating models** — proposing descriptions for objects, slots, rules,
  functions, and RPL expressions, for the modeler to review
  before they are written into the `.mdl` file.
- **Live model control** — a prototype model context protocol
  ([MCP](https://modelcontextprotocol.io)) server that lets an AI agent set
  inputs, run RiverWare in batch mode, and read results back
  *(in development)*.

Two example models are included, but the goal was to create tools for any RiverWare application.

# Quick start

Instructions are included for Claude Code and GitHub Copilot.

## Claude Code

[Claude Code](https://claude.com/claude-code) is Anthropic's agentic coding
tool. It can read and edit repository files, run terminal commands, and carry
out multi-step coding tasks from natural-language prompts. In this repository,
it can follow the skills in `skills/` to analyze RiverWare models and generate
draft outputs. Two ways to get the skills:

**Option A — install as a plugin** (works from any directory):

The tools are available as a Claude Code plugin. This is the quickest option, and the best one if you already have a RiverWare project you'd like to explore.

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

Updates never take effect mid-session on their own: plugins are loaded once
at session start, so after updating run `/reload-plugins` (or restart Claude
Code) to pick up the new version. To check which version
you have, run `/plugin` and look at the installed plugin list, or run
`claude plugin list` from a terminal.

**Option B — clone the entire repository**:

Cloning gives you the example RiverWare models and data, and lets you propose PRs and contribute to the project:

```bash
git clone https://github.com/jrkasprzyk/RiverWare-AI-Tools.git
cd RiverWare-AI-Tools
claude
```

**Using the skills** — try:

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

## Custom GPTs

Each `SKILL.md` file is plain markdown: a self-contained description of a
RiverWare task, the vocabulary involved, and the steps and guardrails for
doing it well. That text can be reused as the system prompt or knowledge
file of a custom GPT — for instance, pasting
`skills/explain-riverware-model/SKILL.md` into a custom GPT's instructions
and then uploading a `.mdl` file to the conversation. Skills that depend
mostly on reading and writing text (explaining models, drafting rules,
cleaning up reports and comments) transfer best. On the other hand, skills that need to run
scripts or fetch web pages need the environment's own code-execution or browsing
features, or a human to run those steps.

This use has not been formally tested — if you try it, we would welcome
feedback or contributed adaptations (see [Contributing](#contributing)).

# Contents

## Skills

| Skill | What it does |
|-------|--------------|
| [explain-riverware-model](skills/explain-riverware-model/SKILL.md) | Parse a `.mdl`/`.rls` file and write a narrative explanation of the model |
| [visualize-riverware-model](skills/visualize-riverware-model/SKILL.md) | Render model structure and key series as a self-contained HTML dashboard |
| [draft-riverware-rules](skills/draft-riverware-rules/SKILL.md) | Draft a pasteable RPL rule from a plain-language policy request |
| [annotate-riverware-model](skills/annotate-riverware-model/SKILL.md) | Propose descriptions and RPL comments for a model, then apply the approved set to the `.mdl` |
| [riverware-help](skills/riverware-help/SKILL.md) | Interactive RiverWare help — answers grounded in the CADSWES CurrentVersion online help, with cited pages and model-aware context |
| [comment-cleanup](skills/comment-cleanup/SKILL.md) | Strip changelog-style and repeated comments from AI-written code, document every tuning parameter with its range, default and units, and write the result in Simplified Technical English |
| [report-cleanup](skills/report-cleanup/SKILL.md) | Rewrite a rambling bug report or issue into Summary/Repro/Hypothesis/Asks, using RiverWare vocabulary to tell an observed symptom from the writer's own guess |

## Examples

| Model | Description | Outputs |
|-------|-------------|---------|
| [ArborBasin](examples/ArborBasin/) | The CADSWES RiverWare training model | [Narrative](examples/ArborBasin/ArborBasin_explained.md) · [Live dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/ArborBasin/ArborBasin_dashboard.html) · [Rule case study](examples/ArborBasin/ArborBasin_rule_case_study.md) · [Annotation review](examples/ArborBasin/ArborBasin_annotations.md) |
| [TwoResOps](examples/TwoResOps/) | Saratoga, a two-reservoir operations testbed | [Narrative](examples/TwoResOps/saratoga_v2.4_explained.md) · [Live dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/TwoResOps/saratoga_v2.4_dashboard.html) · [Rule case study](examples/TwoResOps/saratoga_v2.4_rule_case_study.md) · [Annotation review](examples/TwoResOps/saratoga_v2.4_annotations.md) |

Worked sessions in [examples/sessions/](examples/sessions/) show the skills
that answer, draft, or rewrite rather than produce a per-model artifact:

| Session | Skill |
|---------|-------|
| [Elevation lookup in a rule](examples/sessions/riverware-help_elevation-lookup.md) — a cited help answer checked against Saratoga's own objects | riverware-help |
| [Why is my rule overwritten?](examples/sessions/riverware-help_rule-overwrite.md) — rule priorities and the R flag, mapped onto a real agenda | riverware-help |
| [DMI control-file syntax](examples/sessions/riverware-help_dmi-control-file.md) — line format and %-directives, plus a model-specific wildcard trap | riverware-help |
| [Minimum-flow rule, request to draft](examples/sessions/draft-riverware-rules_roberto-min-flow.md) — a drafting conversation, including the refusal to invent a missing slot | draft-riverware-rules |
| [Comment cleanup, before and after](examples/sessions/comment-cleanup_before-after.md) — history comments out, tuning ranges and units in | comment-cleanup |
| [Report cleanup, before and after](examples/sessions/report-cleanup_before-after.md) — one rambling paragraph into Summary, Repro, Hypothesis, Asks | report-cleanup |

Presenting the repo? [docs/user-group-demo-script.md](docs/user-group-demo-script.md)
is a reproducible run-of-show for the four model-facing skills.

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

For where the integration can go next — and why it works at all — see
[docs/ai-riverware-integration.md](docs/ai-riverware-integration.md).

- [ ] Verified GitHub Copilot walkthrough
- [ ] Verify use within custom GPTs
- [ ] Editing example model descriptions and fine-tuning skills
- [ ] Verify the annotated example models load cleanly in RiverWare
- [ ] Widen `COMMENTED_BY` targeting beyond numeric literals, and encode
      quotes in RPL description text as `&quot;` rather than rejecting them

# Contributing

We welcome contributions, including new examples, modifications to skills, and new tools. See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the
[MIT License](LICENSE).
