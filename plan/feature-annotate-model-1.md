---
goal: Annotate RiverWare models — AI-proposed descriptions and RPL comments, tastefully applied
version: 1.2
date_created: 2026-07-30
last_updated: 2026-07-30
owner: Joseph Kasprzyk
status: 'Implemented — pending owner verification'
tags: [feature, skill, annotation, documentation]
---

# Introduction

![Status: Implemented](https://img.shields.io/badge/status-implemented%20%E2%80%94%20pending%20verification-yellow)

> **Where this stands (2026-07-30).** All twelve tasks are built and the test
> suite is green (34 tests). Two things are outstanding, both owner actions,
> both listed in [§9 Outstanding](#9-outstanding): the annotated example models
> have **not** been loaded in RiverWare, and nothing has been committed. Until
> the load check passes, treat the annotated `.mdl` files as unverified.

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
- **REQ-002**: Support these annotation surfaces, all grounded in observed `.mdl` serialization (`examples/ArborBasin/ArborBasin.mdl`; described-fixture diff of `examples/TwoResOps/saratoga_v2.4.mdl` vs its `.bak`, captured 2026-07-30):
  - RPL set / policy-group / rule / function `DESCRIPTION "…"` fields (serialized as `DESCRIPTION "";\` lines in the embedded RPL sections — annotation fills the existing empty field).
  - RPL expression comments via the `COMMENTED_BY "…"` postfix — **v1 scope: numeric-literal targets only** (decision 2026-07-30; the grounded instance is ArborBasin.mdl:19430: `0.00000000 "kcfs" COMMENTED_BY "Do not let flow be negative"`). Comments on arbitrary expressions ~~deferred until the grammar is observed~~ — grammar since observed (ASSUMPTION-002), but deferred anyway because the attachment point is not recoverable from the serialized line; see §9 item 4.
  - Object descriptions: `"$o" userDescript {text}` line inserted after the object's header lines (line is absent entirely when no description is set).
  - Slot descriptions: `"$s" userDescript {text}` line inserted in the slot's block (same absent-when-empty rule).
  - Model-level description: `$ws.Model.FileInfo comment {text}` (line always present; empty braces when unset).
- **REQ-003**: Two-phase workflow: **propose** (a review Markdown file listing every proposed annotation, numbered, with its target and rationale) then **apply** (script consumes an approved JSON proposal file). Approval is conversational (decision 2026-07-30): the user reads the review doc and tells the AI what to drop or reword by number; the AI edits the JSON accordingly and only then runs the applier. The AI never writes annotations directly into the `.mdl` without the review artifact existing first and the user having approved.
- **REQ-004**: The applier writes to `<model>_annotated.mdl` next to the source by default. In-place editing behind an explicit `--in-place` flag. For the repo's own bundled examples the committed pattern is in-place + git (decision 2026-07-30): git history is the before/after artifact, no duplicate 2 MB models in the tree.
- **REQ-005**: Never overwrite existing non-empty descriptions or comments. Conflicts are listed in the review doc as `SKIPPED (existing text)`.
- **REQ-006**: Tastefulness rubric (enforced by SKILL.md instructions, checked in the review doc):
  - Rules and functions: at most one or two sentences each, and only where the name alone is not self-explanatory.
  - Expression `COMMENTED_BY`: only for magic numbers, unit-bearing thresholds, and non-obvious constructs (e.g. an `IF` with no `ELSE` deliberately leaving a slot unset). Cap: no more than one comment per rule body unless the rule is unusually dense.
  - Slots — the policy-meaning test (decision 2026-07-30): any slot, standard or custom, gets a description iff it carries model-specific policy meaning (read by rules, holds a threshold, is a decision variable or metric). Pure physics slots stay bare. The owner's hand-written Cora Pool Elevation description in saratoga (commit 6bed09b) is the worked example of a standard slot that *earns* one.
  - Objects: one sentence on the object's role in the basin, major objects only. The owner's saratoga object descriptions (Cora, Roberto, Winifred Valley Reach, metrics data object) are the style calibration set — cite them in SKILL.md.
- **SEC-001**: All file writes stay inside the user's working directory (or the repo's `examples/` when run against the bundled models); the skill inherits the "stay inside the working directory" rules from `skills/draft-riverware-rules/SKILL.md`.
- **CON-001**: `.mdl` files are 1.6–1.9 MB Tcl scripts; the AGENTS.md hard rule "never read a `.mdl` raw" applies. All model understanding flows through `python skills/explain-riverware-model/explain.py <model.mdl>`; raw reads are narrow line ranges only.
- **CON-002**: Embedded RPL lines end with a `\` continuation character and RPL strings are double-quoted. The applier must preserve line-continuation structure and escape embedded quotes exactly as RiverWare does; any byte it does not intend to change must survive unchanged.
- **CON-003**: Only RiverWare itself validates a `.mdl`. Every skill output ends with the standing caveat that the annotated copy must be loaded in RiverWare before trusting it (same pattern as the draft-riverware-rules review caveat).
- **GUD-001**: The proposal JSON is the single interface between propose and apply — schema: `{"target_type": "rpl_description" | "rpl_comment" | "object_description" | "slot_description" | "model_description", "target": "<set>/<group>/<rule or Object.Slot>", "text": "…"}` per entry.
- **GUD-002**: No provenance markers in the model text (decision 2026-07-30). Approved annotations are human-endorsed; the review doc, proposal JSON, and git history are the audit trail. Annotation text never mentions AI.
- **PAT-001**: Mirror the existing skill conventions: full skill under `skills/`, thin bridge under `.claude/skills/`, committed example outputs under `examples/`, parser-first workflow, plugin path prefix `${CLAUDE_PLUGIN_ROOT}` documented in SKILL.md.

## 2. Implementation Steps

### Implementation Phase 1 — capture the serialization grammar

- GOAL-001: Know exactly how every annotation surface is serialized in a `.mdl` before writing any code that edits one.

Legend: ✅ done · ◐ partly done, remainder named in the row · ⬜ not started.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | ~~Create a fixture~~ Done: owner set descriptions in RiverWare 9.7 and re-saved `examples/TwoResOps/saratoga_v2.4.mdl` (committed 6bed09b; pre-description copy at `saratoga_v2.4.mdl.bak`). Diff captured the grammar: `"$o"/"$s" userDescript {…}` inserted lines, `$ws.Model.FileInfo comment {…}`, filled `DESCRIPTION "…"`. ~~Remaining: confirm `COMMENTED_BY` is valid on non-literal expressions (ASSUMPTION-002) and probe how RiverWare escapes `{`/`}` and newlines inside brace strings.~~ Both resolved from the existing models, no new fixture needed: `COMMENTED_BY` on arbitrary expressions confirmed (ASSUMPTION-002), newlines serialize as literal `<br>`, `"` in RPL strings escapes as `&quot;` (FINDING-002). `{`/`}` inside a brace string remains unobserved — CON-004 rejects them, so nothing rests on it. | ✅ | 2026-07-30 |
| TASK-002 | Document the captured grammar in `skills/annotate-riverware-model/reference.md`: token names, quoting/escaping rules (embedded `"` in RPL strings, `{}` brace strings elsewhere), line-continuation behavior, insertion position of `userDescript` relative to its parent block, and the note that a RiverWare re-save also perturbs unrelated bytes (timestamps, window coords) — so validation diffs must be applier-vs-source, never save-vs-save. | ✅ | 2026-07-30 |
| TASK-003 | Extend `skills/explain-riverware-model/explain.py` (or add a `--annotations` mode) to report existing descriptions/comments per object, slot, and rule, so the propose step can honor REQ-005 without raw reads. Add coverage in `tests/test_parsers.py`. | ✅ | 2026-07-30 |

### Implementation Phase 2 — the applier script

- GOAL-002: A deterministic, tested `annotate.py` that applies an approved proposal JSON to a copy of the `.mdl`.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-004 | Implement `skills/annotate-riverware-model/annotate.py`: CLI `python annotate.py <model.mdl> <proposals.json> [--in-place]`; locates each target by its structural path (set/group/rule name, or Object.Slot), fills empty `DESCRIPTION ""` fields, inserts `COMMENTED_BY` postfixes, and (once TASK-002 lands) writes object/slot descriptions. Emits a summary: applied / skipped-existing / target-not-found. | ✅ | 2026-07-30 |
| TASK-005 | Round-trip safety: applying an empty proposal list must produce a byte-identical file. Implement as the first test in `tests/test_annotate.py`. | ✅ | 2026-07-30 |
| TASK-006 | Add `tests/test_annotate.py` cases: DESCRIPTION fill on a rule/function/group; COMMENTED_BY insertion preserving the `\` continuations; refusal to overwrite non-empty text (REQ-005); correct escaping of quotes and braces in annotation text; unknown target reported, not silently dropped. Run against a small extracted fixture, not the full 1.9 MB model. | ✅ | 2026-07-30 |

### Implementation Phase 3 — the skill

- GOAL-003: A SKILL.md that produces tasteful proposals and drives the review-then-apply workflow.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-007 | Write `skills/annotate-riverware-model/SKILL.md`: digest-first (explain.py), then propose annotations into `<model>_annotations.md` (human review doc) + `<model>_annotations.json` (machine proposal), then apply with annotate.py only after user approval. Embed the tastefulness rubric (REQ-006) as explicit guardrails with a worked good-vs-bad example ("`Cedar Guide Curve` does not need 'This is the guide curve for Cedar'"). Include the working-directory rules and the RiverWare-validation caveat verbatim from the existing skills. | ✅ | 2026-07-30 |
| TASK-008 | Frontmatter description written for trigger matching: "Use when asked to add comments, descriptions, or documentation to a RiverWare model, ruleset, or RPL code." | ✅ | 2026-07-30 |
| TASK-009 | Add the thin bridge `.claude/skills/annotate-riverware-model/SKILL.md` (same frontmatter, body points to the full skill — copy the pattern from `.claude/skills/draft-riverware-rules/SKILL.md`). | ✅ | 2026-07-30 |

### Implementation Phase 4 — examples and repo integration

- GOAL-004: Committed demonstration outputs and repo wiring.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Run the full workflow on `examples/TwoResOps/saratoga_v2.4.mdl` applying `--in-place`; commit the model plus `saratoga_v2.4_annotations.md` and the proposal JSON. The owner's hand-written descriptions (commit 6bed09b) must all survive untouched (REQ-005 in the wild) — the AI pass fills only what remains empty. Load in RiverWare to verify before committing. **RiverWare load check is an owner action.** — *Applied: 28 annotations of 162 available targets (17%), zero expression comments (see review doc for why). All 17 owner-written descriptions survived; re-applying reports 28/28 SKIPPED. Review doc + JSON written.* **Not done: RiverWare load check, and the commit that depends on it.** | ◐ | 2026-07-30 |
| TASK-011 | Repeat for `examples/ArborBasin/ArborBasin.mdl`, in-place (larger model — demonstrates the rubric holding the line on volume: expect proposals for a minority of rules/slots, not all). — *Applied: 40 annotations of 1,116 available (3.6%); 15 slot descriptions against 1,017 empty slot fields. Volume expectation met. Exposed RISK-004 (multi-line `objAttributes`), fixed and regression-tested.* **Not done: RiverWare load check, and the commit.** | ◐ | 2026-07-30 |
| TASK-012 | Update `README.md` (feature bullet + upcoming-work section), `AGENTS.md` repository-layout tree and skill list, and bump `.claude-plugin/plugin.json` to 0.3.0. | ✅ | 2026-07-30 |

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

`python -m unittest discover -s tests` — **34 tests, green as of 2026-07-30**
(24 in `test_annotate.py`, 10 in `test_parsers.py`).

- ✅ **TEST-001**: Round-trip no-op — empty proposal list yields a byte-identical output file (TASK-005). Verified on the fixture in both LF and CRLF form, and by hand against both full example models.
- ✅ **TEST-002**: Each annotation surface applies correctly on the fixture and the result still matches the captured grammar (TASK-006). Covers both `objAttributes` forms, the `computedByExpr` anchor shift, and a slot with no UUID line.
- ✅ **TEST-003**: Non-empty existing text is never overwritten; the skip is reported (REQ-005). Also confirmed in the wild — re-applying either committed proposal reports 100% SKIPPED.
- ✅ **TEST-004**: Annotation text containing `{`, `}`, or newlines is rejected with a clear message (CON-004); `"` is rejected in RPL surfaces and accepted in brace-string surfaces.
- ⬜ **TEST-005**: Manual: annotated copies of both example models load cleanly in RiverWare and the annotations appear in the GUI (rule editor description tab, open-object dialog, slot dialog) — owner-run, results recorded in the example READMEs. **Outstanding.** Both example READMEs currently carry an explicit "Not yet verified in RiverWare" note, to be replaced with the result.

## 7. Risks & Assumptions

- **RISK-001** *(resolved 2026-07-30)*: Object/slot description serialization was unobserved; the described saratoga fixture captured it (`userDescript` brace strings). Residual: `{`/`}` escaping inside a brace string is still unobserved, but CON-004 rejects those characters so nothing depends on it. Newline escaping is resolved — RiverWare writes a literal `<br>`.
- **RISK-002**: A text-level edit that RiverWare parses but silently misinterprets (e.g. mangled continuation) is worse than a load failure. Mitigated by TEST-001/002 byte-discipline and the mandatory RiverWare load check before committing any annotated example.
- **RISK-003**: LLM verbosity drift — proposals ballooning past the rubric over time. Mitigated by hard caps in SKILL.md and the review doc making volume visible at a glance.
- **ASSUMPTION-001**: RiverWare 9.x tolerates `DESCRIPTION` text of reasonable length (a few hundred characters) in all surfaced fields.
- **ASSUMPTION-002** *(resolved affirmative 2026-07-30 during TASK-002)*: `COMMENTED_BY` **does** attach to arbitrary expressions — saratoga carries one on a function call and one sitting between a slot reference and its `[]` index. v1 still ships literals-only, because the serializer's attachment point is not recoverable from the flattened line; the constraint is now a deliberate limit rather than an unknown. See `reference.md` §6.
- **RISK-004** *(found and fixed 2026-07-30 during TASK-011)*: `objAttributes` has two serialized forms, and only the multi-line one appears in ArborBasin. Anchoring the object description on the opening line would have written it into the middle of the XML. Both example models were needed to see this; covered by a fixture object and a regression test.
- **FINDING-001** *(2026-07-30)*: A `DESCRIPTION` field can also appear inside a rule body, attached to a statement rather than the rule (saratoga's `Irrigation`). Such a rule is documented even though its own field reads empty. Both the applier and the inventory stop at `BEGIN`, so neither confuses the two, but the propose step must read bodies rather than trusting the inventory. v1 does not write statement-level descriptions.
- **FINDING-002** *(2026-07-30)*: Inside an RPL string, RiverWare escapes `"` as `&quot;`. v1 still rejects quotes per CON-004; encoding them is queued as follow-up work.
- **CON-004**: v1 annotation text is restricted to single-line, brace-free strings (no `{`, `}`, no newlines) of at most ~400 characters — matches every observed serialized description and eliminates the unprobed brace/newline escaping question. The applier rejects violating text with a clear message (TEST-004).

## 8. Related Specifications / Further Reading

- `AGENTS.md` — repository conventions, the never-read-a-`.mdl`-raw rule
- `skills/draft-riverware-rules/SKILL.md` — working-directory rules and review-caveat pattern this skill inherits
- `skills/explain-riverware-model/SKILL.md` — the digest workflow the propose step builds on
- [RiverWare documentation](https://riverware.org/HelpSystem/index.html) — RPL comments and object/slot descriptions in the GUI

## 9. Outstanding

Everything in Phases 1–3 is done and tested. What remains is Phase 4's tail.

### Blocking — owner actions, in order

1. **Load both annotated models in RiverWare** (TEST-005, the unfinished half of
   TASK-010/011). Confirm the annotations appear in the open-object dialog, the
   slot dialog, and the RPL editor's description tab. This is the only check
   that can catch RISK-002 — a text edit RiverWare parses but silently
   misreads. Both models are currently annotated **in the working tree,
   uncommitted**: saratoga has 20 inserted lines and 8 replaced fields,
   ArborBasin 25 and 15. `git diff` is the review surface; `git checkout` on the
   two `.mdl` files reverts cleanly if anything is wrong.
2. **Record the result** in `examples/TwoResOps/README.md` and
   `examples/ArborBasin/README.md`, replacing the "Not yet verified in
   RiverWare" note each currently carries.
3. **Commit.** Nothing from this work has been committed. Suggested split: one
   commit for the skill, applier, tests and repo wiring; a second for the two
   annotated models plus their review docs and proposal JSON, so the model diff
   is reviewable on its own.

### Non-blocking — deferred by decision, tracked in README upcoming work

4. **Widen `COMMENTED_BY` targeting** beyond numeric literals. ASSUMPTION-002 is
   now resolved affirmative, so the blocker is no longer "is it valid" but "can
   a subexpression's extent be recovered from the flattened line" — it cannot,
   in general. Needs a fixture showing how the GUI attaches a comment to a
   compound node before this is worth attempting.
5. **Encode `"` as `&quot;`** in RPL description and comment text instead of
   rejecting it (FINDING-002). Cheap to implement; wants one RiverWare round
   trip first to confirm the entity decodes back to `"` in the GUI rather than
   displaying literally.
6. **Statement-level `DESCRIPTION`** (FINDING-001) as a writable surface. Low
   value — the rule-level field covers the same ground — but worth noting that
   the propose step currently has to read rule bodies to avoid double-documenting
   a rule the inventory reports as empty.
7. **Auto-detect the `Irrigation`-style case** in `explain.py --annotations`:
   flag a rule whose header field is empty but whose body carries a
   statement-level description, so the propose step is not relying on the model
   author reading SKILL.md carefully.
