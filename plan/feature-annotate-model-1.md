---
goal: Annotate RiverWare models — AI-proposed descriptions and RPL comments, tastefully applied
version: 1.0
date_created: 2026-07-30
last_updated: 2026-07-30
owner: Joseph Kasprzyk
status: 'Planned'
tags: [feature, skill, annotation, documentation]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

RPL code allows comments, and many slots and objects in RiverWare carry a
Description field — but in older models these are almost always empty. This
plan adds an `annotate-riverware-model` skill: the AI interprets a model
(via the existing `explain.py` digest), proposes a *tasteful* set of
descriptions and comments (not everything needs long comments), presents
them for user review, and applies the approved set to a **copy** of the
`.mdl` with a deterministic Python script. The user validates by loading
the annotated copy in RiverWare.

## 1. Requirements & Constraints

- **REQ-001**: Deliver a new skill `skills/annotate-riverware-model/` with a `SKILL.md` workflow and an `annotate.py` applier script, following the layout of the three existing skills.
- **REQ-002**: Support these annotation surfaces, all grounded in the `.mdl` serialization observed in `examples/ArborBasin/ArborBasin.mdl`:
  - RPL set / policy-group / rule / function `DESCRIPTION "…"` fields (serialized as `DESCRIPTION "";\` lines in the embedded RPL sections, e.g. lines 19075–19345).
  - RPL expression comments via the `COMMENTED_BY "…"` postfix (existing instance at line 19430: `0.00000000 "kcfs" COMMENTED_BY "Do not let flow be negative"`).
  - Object-level and slot-level Description fields (serialization grammar unknown — see TASK-001; this surface ships only after the grammar is captured).
- **REQ-003**: Two-phase workflow: **propose** (a review Markdown file listing every proposed annotation with its target and rationale) then **apply** (script consumes an approved JSON proposal file). The AI never writes annotations directly into the `.mdl` without the review artifact existing first.
- **REQ-004**: The applier writes to `<model>_annotated.mdl` next to the source. In-place editing only behind an explicit `--in-place` flag.
- **REQ-005**: Never overwrite existing non-empty descriptions or comments. Conflicts are listed in the review doc as `SKIPPED (existing text)`.
- **REQ-006**: Tastefulness rubric (enforced by SKILL.md instructions, checked in the review doc):
  - Rules and functions: at most one or two sentences each, and only where the name alone is not self-explanatory.
  - Expression `COMMENTED_BY`: only for magic numbers, unit-bearing thresholds, and non-obvious constructs (e.g. an `IF` with no `ELSE` deliberately leaving a slot unset). Cap: no more than one comment per rule body unless the rule is unusually dense.
  - Slots: only custom/data slots whose purpose is not evident from the name; never standard simulation slots (Inflow, Outflow, Storage, Pool Elevation).
  - Objects: one sentence on the object's role in the basin, major objects only.
- **SEC-001**: All file writes stay inside the user's working directory (or the repo's `examples/` when run against the bundled models); the skill inherits the "stay inside the working directory" rules from `skills/draft-riverware-rules/SKILL.md`.
- **CON-001**: `.mdl` files are 1.6–1.9 MB Tcl scripts; the AGENTS.md hard rule "never read a `.mdl` raw" applies. All model understanding flows through `python skills/explain-riverware-model/explain.py <model.mdl>`; raw reads are narrow line ranges only.
- **CON-002**: Embedded RPL lines end with a `\` continuation character and RPL strings are double-quoted. The applier must preserve line-continuation structure and escape embedded quotes exactly as RiverWare does; any byte it does not intend to change must survive unchanged.
- **CON-003**: Only RiverWare itself validates a `.mdl`. Every skill output ends with the standing caveat that the annotated copy must be loaded in RiverWare before trusting it (same pattern as the draft-riverware-rules review caveat).
- **GUD-001**: The proposal JSON is the single interface between propose and apply — schema: `{"target_type": "rpl_description" | "rpl_comment" | "object_description" | "slot_description", "target": "<set>/<group>/<rule or Object.Slot>", "text": "…"}` per entry.
- **PAT-001**: Mirror the existing skill conventions: full skill under `skills/`, thin bridge under `.claude/skills/`, committed example outputs under `examples/`, parser-first workflow, plugin path prefix `${CLAUDE_PLUGIN_ROOT}` documented in SKILL.md.

## 2. Implementation Steps

### Implementation Phase 1 — capture the serialization grammar

- GOAL-001: Know exactly how every annotation surface is serialized in a `.mdl` before writing any code that edits one.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create a fixture: open `examples/ArborBasin/ArborBasin.mdl` in RiverWare, set an object description (Aspen), a slot description (a custom data slot), a rule DESCRIPTION, and an expression comment; save as `tests/fixtures/ArborBasin_described.mdl` (or a minimal new model if file size is a concern). Diff against the original to capture the exact serialization of each surface. **Requires a RiverWare license — owner action.** | | |
| TASK-002 | Document the captured grammar in `skills/annotate-riverware-model/reference.md`: token names, quoting/escaping rules (embedded `"` in RPL strings, `{}` brace strings elsewhere), line-continuation behavior, and where each field sits relative to its parent block. Include the already-known forms: `DESCRIPTION "…";\` and `COMMENTED_BY "…"`. | | |
| TASK-003 | Extend `skills/explain-riverware-model/explain.py` (or add a `--annotations` mode) to report existing descriptions/comments per object, slot, and rule, so the propose step can honor REQ-005 without raw reads. Add coverage in `tests/test_parsers.py`. | | |

### Implementation Phase 2 — the applier script

- GOAL-002: A deterministic, tested `annotate.py` that applies an approved proposal JSON to a copy of the `.mdl`.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-004 | Implement `skills/annotate-riverware-model/annotate.py`: CLI `python annotate.py <model.mdl> <proposals.json> [--in-place]`; locates each target by its structural path (set/group/rule name, or Object.Slot), fills empty `DESCRIPTION ""` fields, inserts `COMMENTED_BY` postfixes, and (once TASK-002 lands) writes object/slot descriptions. Emits a summary: applied / skipped-existing / target-not-found. | | |
| TASK-005 | Round-trip safety: applying an empty proposal list must produce a byte-identical file. Implement as the first test in `tests/test_annotate.py`. | | |
| TASK-006 | Add `tests/test_annotate.py` cases: DESCRIPTION fill on a rule/function/group; COMMENTED_BY insertion preserving the `\` continuations; refusal to overwrite non-empty text (REQ-005); correct escaping of quotes and braces in annotation text; unknown target reported, not silently dropped. Run against a small extracted fixture, not the full 1.9 MB model. | | |

### Implementation Phase 3 — the skill

- GOAL-003: A SKILL.md that produces tasteful proposals and drives the review-then-apply workflow.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-007 | Write `skills/annotate-riverware-model/SKILL.md`: digest-first (explain.py), then propose annotations into `<model>_annotations.md` (human review doc) + `<model>_annotations.json` (machine proposal), then apply with annotate.py only after user approval. Embed the tastefulness rubric (REQ-006) as explicit guardrails with a worked good-vs-bad example ("`Cedar Guide Curve` does not need 'This is the guide curve for Cedar'"). Include the working-directory rules and the RiverWare-validation caveat verbatim from the existing skills. | | |
| TASK-008 | Frontmatter description written for trigger matching: "Use when asked to add comments, descriptions, or documentation to a RiverWare model, ruleset, or RPL code." | | |
| TASK-009 | Add the thin bridge `.claude/skills/annotate-riverware-model/SKILL.md` (same frontmatter, body points to the full skill — copy the pattern from `.claude/skills/draft-riverware-rules/SKILL.md`). | | |

### Implementation Phase 4 — examples and repo integration

- GOAL-004: Committed demonstration outputs and repo wiring.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Run the full workflow on `examples/TwoResOps/saratoga_v2.4.mdl`; commit `saratoga_v2.4_annotations.md`, the proposal JSON, and the annotated `.mdl` copy after loading it in RiverWare to verify it opens cleanly. **RiverWare load check is an owner action.** | | |
| TASK-011 | Repeat for `examples/ArborBasin/ArborBasin.mdl` (larger model — demonstrates the rubric holding the line on volume: expect proposals for a minority of rules/slots, not all). | | |
| TASK-012 | Update `README.md` (feature bullet + upcoming-work section), `AGENTS.md` repository-layout tree and skill list, and bump `.claude-plugin/plugin.json` to 0.3.0. | | |

## 3. Alternatives

- **ALT-001**: Write annotations directly into the model via the MCP server / RiverWare scripting instead of text-editing the `.mdl`. Rejected for now: the MCP prototype is not yet stable, RiverWare's script API for setting descriptions is unverified, and the text-edit path works offline against a copy. Revisit once the MCP server matures.
- **ALT-002**: Single-shot workflow where the AI edits the `.mdl` directly without a review artifact. Rejected: violates the repo's draft-for-review philosophy; annotation quality ("tasteful") is exactly the judgment a human should confirm cheaply in a Markdown doc before the file is touched.
- **ALT-003**: Emit an annotation *report* only (no `.mdl` writing), leaving the user to paste text into RiverWare dialogs by hand. Rejected as the end state — manual transcription across dozens of fields is the pain point — but the Phase 3 review doc doubles as this deliverable, so users without trust in the applier still get value.

## 4. Dependencies

- **DEP-001**: `skills/explain-riverware-model/explain.py` — digest source for the propose step and host for the TASK-003 extension.
- **DEP-002**: Python 3 standard library only (matches existing scripts; no new packages).
- **DEP-003**: A RiverWare installation for TASK-001 fixture capture and TASK-010/011 load verification — owner actions; everything else runs without RiverWare.

## 5. Files

- **FILE-001**: `skills/annotate-riverware-model/SKILL.md` — new skill (TASK-007, TASK-008).
- **FILE-002**: `skills/annotate-riverware-model/annotate.py` — applier script (TASK-004).
- **FILE-003**: `skills/annotate-riverware-model/reference.md` — serialization grammar (TASK-002).
- **FILE-004**: `.claude/skills/annotate-riverware-model/SKILL.md` — bridge (TASK-009).
- **FILE-005**: `skills/explain-riverware-model/explain.py` — modified for existing-annotation reporting (TASK-003).
- **FILE-006**: `tests/test_annotate.py`, `tests/fixtures/` — new tests + fixture (TASK-001, TASK-005, TASK-006).
- **FILE-007**: `examples/TwoResOps/` and `examples/ArborBasin/` — committed annotation outputs (TASK-010, TASK-011).
- **FILE-008**: `README.md`, `AGENTS.md`, `.claude-plugin/plugin.json` — repo wiring (TASK-012).

## 6. Testing

- **TEST-001**: Round-trip no-op — empty proposal list yields a byte-identical output file (TASK-005).
- **TEST-002**: Each annotation surface applies correctly on the fixture and the result still matches the captured grammar (TASK-006).
- **TEST-003**: Non-empty existing text is never overwritten; the skip is reported (REQ-005).
- **TEST-004**: Annotation text containing `"`, `{`, `}`, and newlines is escaped per the grammar or rejected with a clear message.
- **TEST-005**: Manual: annotated copies of both example models load cleanly in RiverWare and the annotations appear in the GUI (rule editor description tab, open-object dialog, slot dialog) — owner-run, results recorded in the example READMEs.

## 7. Risks & Assumptions

- **RISK-001**: Object/slot description serialization is unobserved (both example models have none set). If the grammar turns out to be version-dependent or structurally awkward, that surface may slip to a v2; RPL DESCRIPTION and COMMENTED_BY are already grounded and ship regardless.
- **RISK-002**: A text-level edit that RiverWare parses but silently misinterprets (e.g. mangled continuation) is worse than a load failure. Mitigated by TEST-001/002 byte-discipline and the mandatory RiverWare load check before committing any annotated example.
- **RISK-003**: LLM verbosity drift — proposals ballooning past the rubric over time. Mitigated by hard caps in SKILL.md and the review doc making volume visible at a glance.
- **ASSUMPTION-001**: RiverWare 9.x tolerates `DESCRIPTION` text of reasonable length (a few hundred characters) in all surfaced fields.
- **ASSUMPTION-002**: The `COMMENTED_BY` postfix is valid on any RPL expression, not only numeric literals (the one observed instance is on a literal). To be confirmed during TASK-001 fixture capture.

## 8. Related Specifications / Further Reading

- `AGENTS.md` — repository conventions, the never-read-a-`.mdl`-raw rule
- `skills/draft-riverware-rules/SKILL.md` — working-directory rules and review-caveat pattern this skill inherits
- `skills/explain-riverware-model/SKILL.md` — the digest workflow the propose step builds on
- [RiverWare documentation](https://riverware.org/HelpSystem/index.html) — RPL comments and object/slot descriptions in the GUI
