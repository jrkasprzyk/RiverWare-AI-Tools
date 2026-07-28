---
goal: Turn RiverWare-AI-Tools into a public-facing AI + RiverWare demo repository
version: 2.0
date_created: 2026-07-28
last_updated: 2026-07-28
owner: Joseph Kasprzyk (jkasprzyk@gmail.com)
status: 'In progress'
tags: [feature, architecture, documentation, skills, riverware, mcp]
---

# Introduction

![Status: In progress](https://img.shields.io/badge/status-In%20progress-yellow)

This plan converts the current repository (one Claude Code skill, two example `.mdl` models) into a public demonstration of how AI tools interface with RiverWare today and how they could integrate in the future. Version 2.0 incorporates the owner's design-interview decisions of 2026-07-28: primary audience is RiverWare modelers new to AI; the repo goes public early (after Phases 1–2) and is built in the open at `github.com/jrkasprzyk/RiverWare-AI-Tools`; v1 ships three skills (explain, visualize, draft-rules), GitHub Pages hosting for dashboards, a working MCP server prototype wrapping RiverWare batch mode, and fully tested support for both Claude Code and GitHub Copilot (no other tools maintained).

## 1. Requirements & Constraints

- **REQ-001**: Repository must be fully self-contained and public-safe: no references to the private `BorgRWProblems` repository, personal machine paths (`C:\Users\joka0958`, `C:\Github\BorgRWProblems`), private folder names (`NorthSouth`, `.documentation`), or optimization-project memories.
- **REQ-002**: Skills live in a top-level `skills/` directory, one folder per skill, each containing `SKILL.md` plus any helper scripts (pattern already established by `skills/explain-riverware-model/`).
- **REQ-003**: Skills must be invokable as slash commands in Claude Code both (a) for users who install the repo as a plugin via `/plugin marketplace add jrkasprzyk/RiverWare-AI-Tools` and (b) for users who simply clone the repo and open Claude Code inside it.
- **REQ-004**: `examples/` must contain, for each model, both the raw `.mdl` input and committed outputs (narrative explanation, visualization dashboard, rule-drafting case study) so visitors see results without running anything. Per owner decision, committed outputs are heavily polished — authored documentation produced with the skills, not raw generations.
- **REQ-005**: The repository must frame AI + RiverWare broadly — file-format understanding, model explanation, visualization, rule authoring, and live-model control — and must NOT present itself as Borg-RiverWare-specific.
- **REQ-006**: Two tools are supported full-depth with tested quick-starts: Claude Code and GitHub Copilot. No Cursor/Codex/other per-tool support is written or maintained; `AGENTS.md` remains as the generic entry point for any other agent.
- **REQ-007**: Primary audience is RiverWare modelers new to AI. README teaches AI-tool setup step by step and assumes RiverWare fluency; docs explain the AI interface, never RiverWare itself.
- **REQ-008**: Zero-install demo experience is committed outputs plus GitHub Pages: dashboards and example narratives reachable as live links from the README (e.g. `jrkasprzyk.github.io/RiverWare-AI-Tools/...`).
- **REQ-009**: v1 ships a working MCP server prototype in `prototypes/riverware-mcp/` wrapping RiverWare batch mode with tools: `list_objects`, `list_slots` (parser digest), `run_model` (RCL batch), `read_slots` (post-run data export), `set_slots` (write DMI input before run) — a closed loop letting an agent perturb inputs, rerun, and compare.
- **SEC-001**: Before the public flip (end of Phase 2), grep the entire repo for `joka0958`, `BorgRWProblems`, `NorthSouth`, `scratchpad`, and absolute `C:\` / `C:/` paths; zero matches allowed outside `plan/`. The same grep runs in CI thereafter.
- **SEC-002**: Both example models are cleared for public release (owner confirmed 2026-07-28). ArborBasin is the CADSWES training model — examples documentation must attribute it.
- **CON-001**: Prefer minimal dependencies but do not enforce stdlib-only (owner decision 2026-07-28). Skills keep their current stdlib parsers; the MCP prototype carries its own `requirements.txt` (MCP SDK).
- **CON-002**: `.mdl` files are 1.6–1.9 MB Tcl scripts; no skill or doc may instruct reading them raw. All access goes through the parsers.
- **CON-003**: All scripts and docs must run on Windows (cp1252 console: ASCII-only script output) and on macOS/Linux.
- **CON-004**: Visualization outputs must be single self-contained HTML files (inline CSS/JS, no CDN dependencies) so they render from file:// and GitHub Pages without a build step.
- **CON-005**: RiverWare itself cannot run in CI (licensed desktop application). CI tests only what runs without it: parsers, RCL-script generation, and output parsing against canned fixtures. Live end-to-end MCP verification happens manually on the owner's machine (RiverWare 9.x installed).
- **GUD-001**: Skill authoring follows Anthropic's published guidance: `description` frontmatter written as trigger conditions, SKILL.md body under ~500 lines, heavy lifting delegated to bundled scripts.
- **GUD-002**: Follow `awesome-copilot` repo conventions where applicable: per-resource README tables, CONTRIBUTING.md, LICENSE, badge row in README.
- **PAT-001**: Every skill mirrors the `explain-riverware-model` pattern: parser script emits a digest; SKILL.md tells the agent how to narrate/render/draft from the digest; a "Worked example" section points at a committed output in `examples/`.

## 2. Implementation Steps

### Implementation Phase 1 — Repository packaging and scaffold

- GOAL-001: Make the repo installable as a Claude Code plugin and presentable as a public project, with all governance files in place.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create `.claude-plugin/plugin.json` at repo root with `{"name": "riverware-ai-tools", "description": "Skills for explaining, visualizing, and automating RiverWare models with AI", "version": "0.1.0"}`. Claude Code plugin loading auto-discovers the top-level `skills/` directory, satisfying REQ-002/REQ-003(a). | ✅ | 2026-07-28 |
| TASK-002 | Create `.claude-plugin/marketplace.json` listing the single plugin with source `"./"`, so `/plugin marketplace add jrkasprzyk/RiverWare-AI-Tools` works directly against the GitHub repo. | ✅ | 2026-07-28 |
| TASK-003 | Create `.claude/skills/` bridge for clone-users (REQ-003(b)): for each skill in `skills/`, add `.claude/skills/<name>/SKILL.md` whose frontmatter copies name/description and whose body is one line pointing at `skills/<name>/SKILL.md`. Under 15 lines each. | ✅ | 2026-07-28 |
| TASK-004 | Write root `README.md` for RiverWare modelers new to AI (REQ-007): what this repo demonstrates (AI ↔ RiverWare, optimizer-agnostic per REQ-005); step-by-step quick-starts for Claude Code (plugin install AND clone-and-run) and GitHub Copilot; skills table; examples table with GitHub Pages live links (REQ-008, links added in TASK-020); "Live-model control (MCP prototype)" section; roadmap link to `docs/ai-riverware-integration.md`. | ✅ | 2026-07-28 |
| TASK-005 | Write `AGENTS.md` at repo root: repo layout, where skills live, the CON-002 never-read-raw rule, how to run the parsers, pointers to each SKILL.md. Generic entry point for any non-Claude, non-Copilot agent (REQ-006). | ✅ | 2026-07-28 |
| TASK-006 | Add `LICENSE` (MIT, copyright Joseph Kasprzyk — confirmed 2026-07-28), `CONTRIBUTING.md` (skill folder layout, SKILL.md checklist per GUD-001, worked-example requirement per PAT-001), and `.gitignore` (`__pycache__/`, `*.pyc`, `.DS_Store`, `.venv/`, `digest.txt`). | ✅ | 2026-07-28 |
| TASK-007 | Rename default branch `master` → `main` (`git branch -m master main`). | ✅ | 2026-07-28 |

### Implementation Phase 2 — Generalize the explain skill, scrub, and go public

- GOAL-002: Portable, self-contained explain skill with its first polished worked example; repo scrubbed and flipped public (owner decision: build in the open from here on).

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-008 | Edit `skills/explain-riverware-model/SKILL.md`: replace the repo-root claim `C:\Github\BorgRWProblems` (line 21) with "the root of this repository"; replace `NorthSouth/` invocation examples (lines 29, 51) with `examples/ArborBasin/ArborBasin.mdl`; delete the hardcoded scratchpad path block (lines 46–52) in favor of "redirect to a temp file of your choice". | ✅ | 2026-07-28 |
| TASK-009 | Same file: remove private-context instructions — the `.documentation/.claude/commands/riverware-doc-edit.md` citation (line 79; inline the style rules, already listed), the `memory/project-overview.md` / `.plan/` cross-reference paragraph (lines 89–92), and Borg-specific narration guidance (lines 76–77), rewritten as "if the model is wired to an external optimizer or DMI-driven workflow, name the objective/constraint slots involved". | ✅ | 2026-07-28 |
| TASK-010 | Same file: repoint the "Worked example" section (lines 99–103) at `examples/ArborBasin/ArborBasin_explained.md` (TASK-012). Both example models embed their rulesets in the `.mdl` (verified 2026-07-28: saratoga carries operating policy groups "Roberto Rules"/"Cora Rules"/"Post Processing" in `loadedSet`; ArborBasin carries MRM and init rule sets) — update the embedded-ruleset guidance and the verified-formats note accordingly. | ✅ | 2026-07-28 |
| TASK-011 | Audit `skills/explain-riverware-model/explain.py` for absolute paths or private references (grep `joka0958`, `BorgRW`, `C:/`, `C:\\`); fix any found. Run it against both example models; confirm non-empty object, slot, and embedded-ruleset output for each. (Also scrubbed private metadata found inside both `.mdl` files: autosave temp paths, save-history usernames, OneDrive ruleset paths, provenance slot note.) | ✅ | 2026-07-28 |
| TASK-012 | Run the explain skill on `examples/ArborBasin/ArborBasin.mdl`, then polish the narrative to authored-documentation quality (REQ-004: heavily polished, fact-checked against the digest) → commit `examples/ArborBasin/ArborBasin_explained.md`. Write `examples/ArborBasin/README.md` with CADSWES training-model attribution (SEC-002) and the regeneration command. | ✅ | 2026-07-28 |
| TASK-013 | Run the SEC-001 scrub grep (`grep -rniE "joka0958|BorgRWProblems|NorthSouth|scratchpad|C:[/\\\\]" --exclude-dir=.git --exclude-dir=plan .`); fix all hits. Push to `github.com/jrkasprzyk/RiverWare-AI-Tools` and flip visibility to public. | | |

### Implementation Phase 3 — Skill: visualize-riverware-model

- GOAL-003: Dashboard skill rendering model structure plus curated result time series as a self-contained HTML file.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-014 | Create `skills/visualize-riverware-model/digest_to_json.py`: reuse the parser from `explain.py` (extract shared parsing into `skills/_shared/mdl_parser.py` if import friction) and emit JSON: objects (name, type, description); link topology from `$ws Link {Obj.Slot} {Obj.Slot}` lines (verified extractable 2026-07-28, e.g. ArborBasin lines 15435+); table slots with numeric data for elevation-volume and rule-curve tables; run horizon; and curated time series (owner decision: structure + key series) — Pool Elevation, Outflow, Storage SeriesSlot values per reservoir where populated, via a slot whitelist constant `KEY_SERIES_SLOTS = ["Pool Elevation", "Outflow", "Storage"]`. | | |
| TASK-015 | Create `skills/visualize-riverware-model/SKILL.md` + `template.html`: skill runs `digest_to_json.py`, injects JSON into `template.html` (inline JS/CSS, no CDN per CON-004) → `<modelname>_dashboard.html` with: object-network schematic (SVG nodes typed by object class, edges from link topology), model summary header (horizon, timestep, object counts), elevation-volume curve plots, rule-curve table viewer, and time-series plots for the curated slots. Frontmatter description: "Use when asked to visualize, chart, dashboard, or diagram a RiverWare model." | | |

### Implementation Phase 4 — Skill: draft-riverware-rules

- GOAL-004: Rule-writing skill — plain-language policy request in, pasteable RPL rule out (owner decision: drafting focus is the differentiator; deep rule explanation stays a supporting move, not the headline).

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-016 | Create `skills/draft-riverware-rules/SKILL.md`: workflow is (1) run the explain-skill parser to digest the target model's objects, slots, and existing ruleset (agenda order, group structure, RPL idioms already in use); (2) draft a new RPL rule or function from the user's plain-language policy description, matching the model's existing RPL style and referencing only slots present in the digest; (3) state where the rule belongs in the agenda (group, position, ASCENDING-order consequence) and emit the RPL as a pasteable text block; (4) always end with an explicit review-before-use caveat — the skill never claims the rule is validated, only RiverWare loading/running validates RPL. Explaining an existing rule is included as a secondary mode used to ground edits, not promoted as the skill's purpose. | | |
| TASK-017 | Add drafting guardrails to the SKILL.md: never invent slot names (digest is the source of truth); mirror the model's function-vs-inline conventions; flag when a request needs a new slot or object that drafting alone cannot create. Include one fully-worked RPL syntax reference example in the SKILL.md body (predecessor-style rule with IF/THEN structure). | | |

### Implementation Phase 5 — Examples buildout and GitHub Pages

- GOAL-005: Every skill has a polished committed worked example for both models where applicable, browsable live via GitHub Pages.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-018 | Explain skill, second model: run on `examples/TwoResOps/saratoga_v2.4.mdl`, polish → commit `examples/TwoResOps/saratoga_v2.4_explained.md` + `examples/TwoResOps/README.md` (attribution + regeneration command). | | |
| TASK-019 | Visualize skill: generate, review, and commit `examples/ArborBasin/ArborBasin_dashboard.html` and `examples/TwoResOps/saratoga_v2.4_dashboard.html`. Verify both render with network disabled (CON-004). | | |
| TASK-020 | Draft-rules skill: one request→rule case study per model (owner decision) — markdown doc containing the plain-language policy request (e.g. "add a spring flood-control drawdown rule for Cedar"), the drafted RPL block, and short commentary on agenda placement → commit `examples/ArborBasin/ArborBasin_rule_case_study.md` and `examples/TwoResOps/saratoga_v2.4_rule_case_study.md`. Polished per REQ-004. | | |
| TASK-021 | Enable GitHub Pages (deploy from `main`, root, with `.nojekyll`): add a minimal hand-written `index.html` at repo root linking every example narrative, dashboard, and case study. Update README example-table links to the live `jrkasprzyk.github.io/RiverWare-AI-Tools/...` URLs (REQ-008). | | |
| TASK-022 | Write `examples/README.md`: table of both models (what each basin is, CADSWES attribution, which outputs exist, which skill produced each, regeneration commands), stating outputs are produced with the skills and human-polished. | | |

### Implementation Phase 6 — MCP server prototype (live RiverWare control)

- GOAL-006: Working `prototypes/riverware-mcp/` server giving an AI agent read + run + write control of a local RiverWare installation via batch mode.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-023 | Create `prototypes/riverware-mcp/` with `requirements.txt` (MCP Python SDK), `server.py`, and `README.md`. Tools (REQ-009): `list_objects` and `list_slots` served from the shared `.mdl` parser digest; `run_model(model_path)` generating and executing an RCL batch script against a configured RiverWare executable path (config via `RIVERWARE_EXE` environment variable or `config.json`); `set_slots(assignments)` writing a DMI input file consumed at run start; `read_slots(slot_names)` reading a post-run data export. Design the RCL/DMI exchange during implementation against RiverWare 9.x batch-mode docs. | | |
| TASK-024 | Separate generation from execution for testability (CON-005): pure functions `build_rcl_script(...)`, `build_dmi_input(...)`, `parse_slot_export(...)` with no subprocess calls, plus a thin executor. Unit tests cover the pure functions against canned fixture files in `prototypes/riverware-mcp/tests/fixtures/`. | | |
| TASK-025 | Live end-to-end verification on the owner's machine (RiverWare 9.x, owner-confirmed 2026-07-28): register the MCP server in Claude Code, then via agent tool calls set a decision slot on ArborBasin, run the model, read result slots back, and confirm values change between two runs with different inputs. Record the verified RiverWare version in `prototypes/riverware-mcp/README.md` with an "experimental — requires a licensed local RiverWare install" banner. | | |
| TASK-026 | Document the prototype in `docs/ai-riverware-integration.md` (TASK-027) and add a demo transcript (the actual set→run→read tool-call sequence, polished per REQ-004) as `prototypes/riverware-mcp/demo_transcript.md`, linked from README. | | |

### Implementation Phase 7 — Integration docs, Copilot verification, CI

- GOAL-007: The AI ↔ RiverWare story is documented, both supported tools are verified end-to-end, and CI guards regressions.

| Task | Task Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-027 | Write `docs/ai-riverware-integration.md`. "What works today": parsing `.mdl`/`.rls` formats (explain/visualize skills), drafting RPL policy code (draft-rules skill), live batch-mode control (MCP prototype), analyzing RiverWare output data. "Prototype directions": natural-language Q&A over a loaded model, AI-assisted calibration workflows, automated run-report narration, deeper RiverWare-native integration hooks. Optimizer-agnostic throughout (REQ-005); optimization mentioned once as one workflow the MCP loop enables. | | |
| TASK-028 | Copilot full support (REQ-006, owner decision): add `.github/copilot-instructions.md` mirroring AGENTS.md key rules; verify once in Copilot (CLI or VS Code) that the `skills/<name>/SKILL.md` folders load and execute (same layout as github/awesome-copilot); write the tested Copilot quick-start into README with exact commands. If Copilot's skill discovery needs an additional manifest or path, add it. | | |
| TASK-029 | Add `tests/test_parsers.py` (`unittest`): both models — `explain.py` exits 0 with >0 objects; `digest_to_json.py` emits valid JSON with non-empty `objects`, `links`, and at least one curated series for ArborBasin; parser stdout ASCII-encodable (CON-003). Include MCP pure-function tests from TASK-024 in the run. | | |
| TASK-030 | Add `.github/workflows/ci.yml`: run tests on `ubuntu-latest` + `windows-latest`, Python 3.10 + 3.12; final job step runs the SEC-001 scrub grep and fails on any match. | | |
| TASK-031 | Final verification pass: `/plugin marketplace add jrkasprzyk/RiverWare-AI-Tools` from a clean directory exposes all three skills as commands; clone-and-open path exposes them via the `.claude/skills/` bridge; all Pages links in README resolve. | | |

## 3. Alternatives

- **ALT-001**: Duplicate full skill content into `.claude/commands/*.md` files instead of plugin + bridge. Rejected: two copies drift; single source of truth stays in `skills/`.
- **ALT-002**: Keep skills under `.claude/skills/` only. Rejected: owner wants a visible top-level `skills/` folder, which is also the Copilot/awesome-copilot convention.
- **ALT-003**: Python plotting pipeline (matplotlib → PNG) for the dashboard. Rejected: inline-JS HTML is dependency-free, interactive, and serves directly from GitHub Pages.
- **ALT-004**: Center the repo on Borg-RiverWare optimization. Rejected by REQ-005.
- **ALT-005**: Docs-only "future integration" section without a working prototype. Rejected by owner 2026-07-28 — a live MCP prototype is the strongest form of the argument; CON-005 testing strategy contains the risk.
- **ALT-006**: Commit skill outputs as-generated for authenticity. Rejected by owner 2026-07-28 — committed examples are polished, authored documentation; README words this as "produced with these skills" without claiming raw output quality.
- **ALT-007**: Support Cursor/Codex/other tools. Rejected by owner 2026-07-28 — maintenance limited to Claude Code + Copilot; AGENTS.md covers everyone else generically.
- **ALT-008**: Hold the repo private until everything ships. Rejected by owner 2026-07-28 — public after Phase 2, built in the open.

## 4. Dependencies

- **DEP-001**: Python 3.10+ for parsers and tests; skills stay stdlib in practice, but stdlib-only is not enforced (CON-001).
- **DEP-002**: Claude Code plugin/marketplace mechanism (`.claude-plugin/plugin.json`, `marketplace.json`).
- **DEP-003**: RiverWare `.mdl` text format as parsed by `explain.py`; both committed models verified to contain parseable object, link, and embedded-ruleset markers (2026-07-28 inspection).
- **DEP-004**: GitHub Actions (`ubuntu-latest`, `windows-latest`) and GitHub Pages on `jrkasprzyk/RiverWare-AI-Tools`.
- **DEP-005**: MCP Python SDK (`pip install mcp`) for the prototype only.
- **DEP-006**: Licensed RiverWare 9.x on the owner's machine for MCP live verification (owner confirmed available 2026-07-28); RiverWare batch mode / RCL / DMI documentation at riverware.org.
- **DEP-007**: GitHub Copilot (CLI or VS Code) access for the one-time TASK-028 verification.

## 5. Files

- **FILE-001**: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — new; plugin packaging (TASK-001/002).
- **FILE-002**: `.claude/skills/<name>/SKILL.md` × 3 — new; thin bridges for clone users (TASK-003).
- **FILE-003**: `README.md`, `AGENTS.md`, `LICENSE`, `CONTRIBUTING.md`, `.gitignore`, `index.html` — new; governance, entry points, Pages index (TASK-004/005/006/021).
- **FILE-004**: `skills/explain-riverware-model/SKILL.md` — modified; portability scrub and repointing (TASK-008/009/010).
- **FILE-005**: `skills/explain-riverware-model/explain.py` — audited (TASK-011); shared parsing optionally extracted to `skills/_shared/mdl_parser.py` (TASK-014).
- **FILE-006**: `skills/visualize-riverware-model/{SKILL.md, digest_to_json.py, template.html}` — new (TASK-014/015).
- **FILE-007**: `skills/draft-riverware-rules/SKILL.md` — new (TASK-016/017).
- **FILE-008**: `examples/**`: `*_explained.md`, `*_dashboard.html`, `*_rule_case_study.md`, per-folder `README.md`, `examples/README.md` — new worked examples (TASK-012/018/019/020/022).
- **FILE-009**: `prototypes/riverware-mcp/{server.py, requirements.txt, README.md, demo_transcript.md, tests/}` — new MCP prototype (TASK-023–026).
- **FILE-010**: `docs/ai-riverware-integration.md`, `.github/copilot-instructions.md` — new docs (TASK-027/028).
- **FILE-011**: `tests/test_parsers.py`, `.github/workflows/ci.yml` — new validation (TASK-029/030).

## 6. Testing

- **TEST-001**: `tests/test_parsers.py` — for each model: `explain.py` exits 0, reports > 0 objects, output includes embedded-ruleset content.
- **TEST-002**: `tests/test_parsers.py` — `digest_to_json.py` output parses with `json.loads`; `objects` and `links` non-empty; every object has `name` and `type`; ArborBasin digest contains ≥ 1 curated time series.
- **TEST-003**: `tests/test_parsers.py` — parser stdout ASCII-encodable (CON-003 cp1252 safety).
- **TEST-004**: MCP unit tests — `build_rcl_script`, `build_dmi_input`, `parse_slot_export` verified against canned fixtures with no RiverWare present (CON-005).
- **TEST-005**: Manual — both committed dashboards render fully with network disabled (CON-004), and via their GitHub Pages URLs.
- **TEST-006**: Manual — TASK-025 live MCP loop on owner machine: set slot → run → read; values differ across two runs with different inputs; verified RiverWare version recorded.
- **TEST-007**: Manual — TASK-028 Copilot verification and TASK-031 Claude Code plugin + clone-path verification.
- **TEST-008**: CI scrub gate — SEC-001 grep returns zero matches; runs as final CI step so regressions fail the build.

## 7. Risks & Assumptions

- **RISK-001**: Claude Code plugin manifest schema or skill-discovery behavior may differ from what TASK-001/003 assume; mitigated by TASK-031 end-to-end verification, adjusting layout if either path fails.
- **RISK-002**: Copilot's skill discovery may need more than the bare `skills/` layout (extra manifest, registration); TASK-028 verification catches this before the README promises it.
- **RISK-003**: RCL batch mode may not expose slot read/write as directly as assumed — the exchange may need DMI dataset files with model-side DMI objects configured. TASK-023 designs against 9.x batch docs; fallback is shipping `run_model` + `read_slots` (export-based) first and documenting `set_slots` limitations, keeping the prototype honest.
- **RISK-004**: Curated series slots may be empty in a committed model (no saved run results); TASK-014 handles absent series gracefully (dashboard omits the panel), and TASK-019 review confirms at least one model shows series plots.
- **RISK-005**: Public-early strategy means visitors may arrive mid-build; mitigated by an accurate README status/roadmap section from day one and the Phase-2 scrub guaranteeing nothing private is ever public.
- **ASSUMPTION-001**: Both models cleared for public redistribution — owner confirmed 2026-07-28; ArborBasin attributed as the CADSWES training model.
- **ASSUMPTION-002**: MIT license — owner confirmed 2026-07-28.
- **ASSUMPTION-003**: Owner's local RiverWare 9.x install is available for TASK-025 live verification — confirmed 2026-07-28.
- **ASSUMPTION-004**: Visitors are water-resources practitioners fluent in RiverWare (REQ-007); no RiverWare tutorial content is written.

## 8. Related Specifications / Further Reading

- [skills/explain-riverware-model/SKILL.md](../skills/explain-riverware-model/SKILL.md) — the pattern-setting existing skill
- [Anthropic Agent Skills documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) — SKILL.md format and authoring guidance
- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic's public skills collection (reference for repo conventions)
- [Claude Code plugins & marketplaces](https://docs.claude.com/en/docs/claude-code/plugins) — plugin.json / marketplace.json mechanics
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP SDK and server authoring for the prototype
- [github/awesome-copilot](https://github.com/github/awesome-copilot) — cross-tool skills/plugins repo conventions (local clone: `C:\Github\awesome-copilot`)
- [RiverWare online help](https://riverware.org/HelpSystem/CurrentVersion/index.html) — authoritative batch mode / RCL / DMI / RPL documentation
