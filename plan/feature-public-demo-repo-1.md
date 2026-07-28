---
goal: Turn RiverWare-AI-Tools into a public-facing AI + RiverWare demo repository
version: 1.0
date_created: 2026-07-28
last_updated: 2026-07-28
owner: Joseph Kasprzyk (jkasprzyk@gmail.com)
status: 'Planned'
tags: [feature, architecture, documentation, skills, riverware]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan converts the current two-file repository (one Claude Code skill, two example `.mdl` models) into a public demonstration of how AI tools interface with RiverWare today and how they could integrate in the future. It packages the `skills/` folder so skills are both browsable files and invokable slash commands, builds worked examples (narrative explanations, a visualization dashboard) in `examples/`, and documents the broader AI-to-RiverWare integration landscape beyond the Borg-RiverWare optimization tooling. The repository must work for Claude Code users first-class, with documented paths for GitHub Copilot and other agentic tools.

## 1. Requirements & Constraints

- **REQ-001**: Repository must be fully self-contained and public-safe: no references to the private `BorgRWProblems` repository, personal machine paths (`C:\Users\joka0958`, `C:\Github\BorgRWProblems`), private folder names (`NorthSouth`, `.documentation`), or optimization-project memories.
- **REQ-002**: Skills live in a top-level `skills/` directory, one folder per skill, each containing `SKILL.md` plus any helper scripts (pattern already established by `skills/explain-riverware-model/`).
- **REQ-003**: Skills must be invokable as slash commands in Claude Code both (a) for users who install the repo as a plugin via the marketplace mechanism and (b) for users who simply clone the repo and open Claude Code inside it.
- **REQ-004**: `examples/` must contain, for each model, both the raw `.mdl` input and committed AI-produced outputs (narrative explanation, visualization dashboard) so visitors see results without running anything.
- **REQ-005**: The repository must frame AI + RiverWare broadly — file-format understanding, model explanation, visualization, scripting/automation, and future integration prototypes — and must NOT present itself as Borg-RiverWare-specific.
- **REQ-006**: README and docs must state that the skills are usable from other AI tools (GitHub Copilot supports the same `SKILL.md` folder format; any agent can follow `AGENTS.md`), with concrete install/use instructions per tool.
- **SEC-001**: Before first public push, grep the entire repo for `joka0958`, `BorgRWProblems`, `NorthSouth`, `scratchpad`, and absolute `C:\` / `C:/` paths; zero matches allowed outside this plan file's history notes.
- **SEC-002**: Verify both `.mdl` files are shareable (no proprietary basin data or credentials embedded in slot descriptions or DMI dataset paths) before the repo is made public.
- **CON-001**: Helper scripts remain Python 3.10+ standard library only — no pip installs required to run any skill.
- **CON-002**: `.mdl` files are 1.6–1.9 MB Tcl scripts; no skill or doc may instruct reading them raw. All access goes through `explain.py`-style parsers.
- **CON-003**: All scripts and docs must run on Windows (cp1252 console: ASCII-only output, per existing `explain.py` convention) and on macOS/Linux.
- **CON-004**: Visualization outputs must be single self-contained HTML files (inline CSS/JS, no CDN dependencies) so they render from a file:// open or GitHub Pages without a build step.
- **GUD-001**: Skill authoring follows Anthropic's published guidance: `description` frontmatter written as trigger conditions ("Use when asked to…"), SKILL.md body under ~500 lines, heavy lifting delegated to bundled scripts (progressive disclosure).
- **GUD-002**: Follow `awesome-copilot` repo conventions where applicable: per-resource-type README tables with one-line descriptions, CONTRIBUTING.md, LICENSE, badge row in README.
- **PAT-001**: Every new skill mirrors the `explain-riverware-model` pattern: parser script emits a digest; SKILL.md tells the agent how to narrate/render the digest; a "Worked example" section points at a committed output in `examples/`.

## 2. Implementation Steps

### Implementation Phase 1 — Repository packaging and scaffold

- GOAL-001: Make the repo installable as a Claude Code plugin and presentable as a public project, with all governance files in place.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create `.claude-plugin/plugin.json` at repo root with `{"name": "riverware-ai-tools", "description": "Skills for explaining, visualizing, and automating RiverWare models with AI", "version": "0.1.0"}`. Claude Code plugin loading auto-discovers the top-level `skills/` directory, satisfying REQ-002/REQ-003(a). | | |
| TASK-002 | Create `.claude-plugin/marketplace.json` listing the single plugin with source `"./"`, so `/plugin marketplace add jrkasprzyk/RiverWare-AI-Tools` works directly against the GitHub repo. | | |
| TASK-003 | Create `.claude/skills/` containing a symlink-free bridge for clone-users (REQ-003(b)): for each skill in `skills/`, add `.claude/skills/<name>/SKILL.md` whose frontmatter copies name/description and whose body is one line: "Follow the instructions in `skills/<name>/SKILL.md` at the repo root." Keep bridge files under 15 lines each. | | |
| TASK-004 | Write root `README.md`: project purpose (AI ↔ RiverWare demo, not Borg-specific per REQ-005), quick-start table (Claude Code plugin install, Claude Code clone-and-run, GitHub Copilot, other agents), skills table (name, one-line description, worked-example link), examples table, and a "Roadmap: future AI integration prototypes" section linking to `docs/ai-riverware-integration.md`. | | |
| TASK-005 | Write `AGENTS.md` at repo root: repo layout, where skills live, the CON-002 rule (never read `.mdl` raw — use the parsers), Python version, and pointers to each SKILL.md. This is the entry point for non-Claude agents (REQ-006). | | |
| TASK-006 | Add `LICENSE` (MIT, copyright Joseph Kasprzyk — confirmed by owner 2026-07-28), `CONTRIBUTING.md` (how to add a skill: folder layout, SKILL.md checklist from GUD-001, worked-example requirement from PAT-001), and `.gitignore` (`__pycache__/`, `*.pyc`, `.DS_Store`, `digest.txt`). | | |
| TASK-007 | Rename default branch `master` → `main` (`git branch -m master main`) to match the configured PR default branch. | | |

### Implementation Phase 2 — Generalize the existing skill for public use

- GOAL-002: Make `skills/explain-riverware-model/` portable, self-contained, and pointed at this repo's examples instead of private material.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-008 | Edit `skills/explain-riverware-model/SKILL.md`: replace the repo-root claim `C:\Github\BorgRWProblems` (line 21) with "the root of this repository"; replace the `NorthSouth/` invocation examples (lines 29, 51) with `examples/ArborBasin/ArborBasin.mdl`; delete the hardcoded scratchpad path block (lines 46–52) in favor of "redirect to a temp file of your choice". | | |
| TASK-009 | Same file: remove private-context instructions — the `.documentation/.claude/commands/riverware-doc-edit.md` house-style citation (line 79; inline the style rules themselves, which are already listed), the `README.md`/`memory/project-overview.md`/`.plan/` cross-reference paragraph (lines 89–92), and Borg-specific narration guidance in step 5 (lines 76–77), rewriting it as "if the model is wired to an external optimizer or DMI-driven workflow, name the objective/constraint slots involved". | | |
| TASK-010 | Same file: repoint the "Worked example" section (lines 99–103) at `examples/ArborBasin/ArborBasin_explained.md` (produced in TASK-015). | | |
| TASK-011 | Verify `skills/explain-riverware-model/explain.py` has no absolute paths or private references (grep for `joka0958`, `BorgRW`, `C:/`, `C:\\`); fix any found. Run it against both example models and confirm non-empty object and slot output for each. | | |
| TASK-012 | Update the SKILL.md `description` frontmatter to also mention embedded rulesets explicitly, and confirm the two example models' formats parse (ArborBasin and saratoga_v2.4 may be embedded-ruleset models with no `.rls`; the Troubleshooting section already covers format drift — update the verified-versions note after TASK-011 runs). | | |

### Implementation Phase 3 — New skill: visualize-riverware-model

- GOAL-003: Add a second skill that renders a `.mdl` digest as a self-contained interactive HTML dashboard, demonstrating a visual AI-RiverWare interface.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-013 | Create `skills/visualize-riverware-model/digest_to_json.py`: import/reuse the parser from `../explain-riverware-model/explain.py` (refactor shared parsing into `skills/_shared/mdl_parser.py` if import friction; keep stdlib-only per CON-001) and emit JSON: objects (name, type, description), link topology if extractable from the `.mdl` `$ws Link` entries, table slots with full numeric data for elevation-volume and rule-curve tables, run horizon. | | |
| TASK-014 | Create `skills/visualize-riverware-model/SKILL.md` + `template.html`: the skill runs `digest_to_json.py`, injects the JSON into `template.html` (inline `<script>` data block, no CDN per CON-004), producing `<modelname>_dashboard.html` with: object-network schematic (SVG, reservoirs/reaches/gages as typed nodes), elevation-volume curve plots per reservoir, rule-curve table viewer, and a model summary header (horizon, timestep, object counts). Frontmatter description: "Use when asked to visualize, chart, dashboard, or diagram a RiverWare model." | | |

### Implementation Phase 4 — Worked examples

- GOAL-004: Commit finished AI outputs for both example models so the repo demos itself without any tool running.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-015 | Run the explain skill end-to-end on `examples/ArborBasin/ArborBasin.mdl` → commit `examples/ArborBasin/ArborBasin_explained.md`. | | |
| TASK-016 | Run the explain skill on `examples/TwoResOps/saratoga_v2.4.mdl` → commit `examples/TwoResOps/saratoga_v2.4_explained.md`. | | |
| TASK-017 | Run the visualize skill on both models → commit `examples/ArborBasin/ArborBasin_dashboard.html` and `examples/TwoResOps/saratoga_v2.4_dashboard.html`. | | |
| TASK-018 | Write `examples/README.md` and a short `README.md` inside each example folder: what the basin is, where the model came from / attribution, which outputs were AI-generated and by which skill, and the exact command to regenerate them. | | |

### Implementation Phase 5 — AI + RiverWare integration docs and multi-tool support

- GOAL-005: Document the present and future AI-RiverWare interface landscape (REQ-005) and make the skills usable from non-Claude tools (REQ-006).

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-019 | Write `docs/ai-riverware-integration.md` with two sections. "What works today": parsing `.mdl`/`.rls` text formats (these skills), generating/reviewing RPL policy code, writing RCL batch scripts and DMI control files for automation, analyzing RiverWare CSV/Excel/HDB output data. "Prototype directions": an MCP server wrapping RiverWare batch mode (run model, read slots as tool calls), natural-language Q&A over a loaded model, AI-assisted RPL rule authoring with digest context, automated run-report narration. Each future item gets a one-paragraph concrete sketch, explicitly optimizer-agnostic. | | |
| TASK-020 | Add Copilot support: `.github/copilot-instructions.md` mirroring AGENTS.md key rules. Note in README that the `skills/<name>/SKILL.md` folder format is directly consumable by GitHub Copilot's skills support (same convention as github/awesome-copilot), so no file duplication is needed. | | |
| TASK-021 | Add a "Using other AI tools" README section: any agent that can run Python and read markdown can execute these skills manually (point at AGENTS.md); list the manual recipe (run parser → follow SKILL.md narration/render steps). | | |

### Implementation Phase 6 — Validation and publication

- GOAL-006: Automated checks pass, public-safety scrub is clean, repo is pushed public.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-022 | Add `tests/test_parsers.py` (stdlib `unittest`): for each example `.mdl`, assert `explain.py` exits 0, digest reports > 0 objects, and `digest_to_json.py` emits valid JSON with non-empty `objects` array. Add `.github/workflows/ci.yml` running it on `ubuntu-latest` and `windows-latest`, Python 3.10 and 3.12. | | |
| TASK-023 | Run SEC-001 scrub: `grep -rniE "joka0958|BorgRWProblems|NorthSouth|scratchpad|C:[/\\\\]" --exclude-dir=.git --exclude-dir=plan .` must return zero matches; fix any hits. Perform SEC-002 review of both `.mdl` files' descriptions and DMI dataset paths. | | |
| TASK-024 | Verify plugin install path end-to-end: from a clean directory, `/plugin marketplace add jrkasprzyk/RiverWare-AI-Tools` (or local-path equivalent), confirm both skills appear as invokable commands; separately confirm the clone-and-open path exposes them via the `.claude/skills/` bridge. Then push and flip repo visibility to public. | | |

## 3. Alternatives

- **ALT-001**: Duplicate full skill content into `.claude/commands/*.md` slash-command files instead of the plugin + bridge approach. Rejected: two copies of every skill drift apart; the plugin manifest serves marketplace users and the thin bridge serves clone users with a single source of truth in `skills/`.
- **ALT-002**: Keep skills under `.claude/skills/` only (Claude Code's native discovery location) and drop the top-level `skills/` folder. Rejected: owner explicitly wants a visible, simple `skills/` folder for repo browsers, and top-level `skills/` is also the convention Copilot and awesome-copilot use.
- **ALT-003**: Build the dashboard as a Python plotting pipeline (matplotlib → PNG). Rejected: violates CON-001/CON-004 spirit — inline-JS HTML is dependency-free, interactive, and viewable directly on a cloned repo or GitHub Pages.
- **ALT-004**: Center the repo on the Borg-RiverWare optimization connection. Rejected by REQ-005: the public framing is the general AI ↔ RiverWare interface; optimization is one workflow among several.

## 4. Dependencies

- **DEP-001**: Python 3.10+ standard library (parser scripts, tests). No third-party packages.
- **DEP-002**: Claude Code plugin/marketplace mechanism (`.claude-plugin/plugin.json`, `marketplace.json`) for command installation.
- **DEP-003**: RiverWare `.mdl` text format as parsed by `explain.py` (verified against RiverWare 9.6.3 model / 9.5 ruleset formats); the two committed example models must parse under it (verified in TASK-011).
- **DEP-004**: GitHub Actions (`ubuntu-latest`, `windows-latest` runners) for CI in TASK-022.
- **DEP-005**: Owner decisions — all resolved 2026-07-28: license is MIT, public URL is `github.com/jrkasprzyk/RiverWare-AI-Tools`, and both example models are cleared for public release (SEC-002).

## 5. Files

- **FILE-001**: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — new; plugin packaging (TASK-001/002).
- **FILE-002**: `.claude/skills/explain-riverware-model/SKILL.md`, `.claude/skills/visualize-riverware-model/SKILL.md` — new; thin bridges for clone users (TASK-003).
- **FILE-003**: `README.md`, `AGENTS.md`, `LICENSE`, `CONTRIBUTING.md`, `.gitignore` — new; governance and entry points (TASK-004/005/006).
- **FILE-004**: `skills/explain-riverware-model/SKILL.md` — modified; portability scrub and repointing (TASK-008/009/010/012).
- **FILE-005**: `skills/explain-riverware-model/explain.py` — audited, possibly modified (TASK-011); parsing logic optionally extracted to `skills/_shared/mdl_parser.py` (TASK-013).
- **FILE-006**: `skills/visualize-riverware-model/SKILL.md`, `digest_to_json.py`, `template.html` — new skill (TASK-013/014).
- **FILE-007**: `examples/ArborBasin/ArborBasin_explained.md`, `examples/ArborBasin/ArborBasin_dashboard.html`, `examples/TwoResOps/saratoga_v2.4_explained.md`, `examples/TwoResOps/saratoga_v2.4_dashboard.html`, `examples/README.md`, per-folder READMEs — new worked examples (TASK-015–018).
- **FILE-008**: `docs/ai-riverware-integration.md`, `.github/copilot-instructions.md` — new docs (TASK-019/020).
- **FILE-009**: `tests/test_parsers.py`, `.github/workflows/ci.yml` — new validation (TASK-022).

## 6. Testing

- **TEST-001**: `tests/test_parsers.py::test_explain_arborbasin` — `explain.py examples/ArborBasin/ArborBasin.mdl` exits 0, stdout contains `objects:` with count > 0.
- **TEST-002**: `tests/test_parsers.py::test_explain_tworesops` — same assertions for `saratoga_v2.4.mdl`.
- **TEST-003**: `tests/test_parsers.py::test_digest_json` — `digest_to_json.py` output parses with `json.loads`, `objects` array non-empty, every object has `name` and `type` keys, for both models.
- **TEST-004**: `tests/test_parsers.py::test_ascii_output` — parser stdout is ASCII-encodable (CON-003 cp1252 safety).
- **TEST-005**: Manual — open both committed `*_dashboard.html` files from disk in a browser with network disabled; schematic and plots render (CON-004).
- **TEST-006**: Manual — TASK-024 plugin-install and clone-and-open verification that `/explain-riverware-model` and `/visualize-riverware-model` are invokable both ways.
- **TEST-007**: Scrub gate — SEC-001 grep returns zero matches; run in CI as a final job step so regressions fail the build.

## 7. Risks & Assumptions

- **RISK-001**: Claude Code plugin manifest schema or skill-discovery behavior may differ from what TASK-001/003 assume; mitigated by TASK-024 end-to-end verification before publicizing, adjusting layout if either invocation path fails.
- **RISK-002**: The two example `.mdl` files may use format variants `explain.py` does not fully parse (embedded rulesets, newer slot markers); TASK-011 surfaces this early, and parser fixes stay within Phase 2.
- **RISK-003**: Link topology may not be cleanly extractable from `.mdl` text for the network schematic (TASK-013); fallback is a typed object grid grouped by object type rather than a connected graph — dashboard remains valuable.
- **RISK-004**: Example models may carry data that cannot be public (SEC-002); if so, they must be replaced with cleared models before publication, which blocks Phase 4.
- **ASSUMPTION-001**: ArborBasin and TwoResOps models are cleared for public redistribution — confirmed by owner 2026-07-28.
- **ASSUMPTION-002**: MIT license — confirmed by owner 2026-07-28.
- **ASSUMPTION-003**: GitHub Copilot's skills support consumes the same `skills/<name>/SKILL.md` layout used by github/awesome-copilot, so no per-tool duplication is required (TASK-020 verifies against Copilot docs at implementation time).
- **ASSUMPTION-004**: Visitors are water-resources practitioners familiar with RiverWare concepts; docs explain the AI interface, not RiverWare itself.

## 8. Related Specifications / Further Reading

- [skills/explain-riverware-model/SKILL.md](../skills/explain-riverware-model/SKILL.md) — the pattern-setting existing skill
- [Anthropic Agent Skills documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) — SKILL.md format and authoring guidance
- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic's public skills collection (reference for repo conventions)
- [Claude Code plugins & marketplaces](https://docs.claude.com/en/docs/claude-code/plugins) — plugin.json / marketplace.json mechanics
- [github/awesome-copilot](https://github.com/github/awesome-copilot) — cross-tool skills/plugins repo conventions (local clone: `C:\Github\awesome-copilot`)
- [RiverWare online help](https://riverware.org/HelpSystem/CurrentVersion/index.html) — authoritative object/method/RPL semantics
