---
goal: PowerPoint deck skill — explain a RiverWare model as a presentation
version: 1.3
date_created: 2026-08-28
last_updated: 2026-08-28
owner: Joseph Kasprzyk
status: 'Completed'
tags: [feature, skill, presentation, pptx, visualization]
---

# Introduction

![Status: Completed](https://img.shields.io/badge/status-completed-brightgreen)

Users asked for the dashboard, but in PowerPoint form: a skill that turns a
`.mdl` (and its ruleset) into a slide deck that explains the model, in a file a
modeler can present at a stakeholder meeting or fold into an existing briefing.

Skill name: `present-riverware-model` (decision 2026-08-28). Architecture
(decisions 2026-08-28, grill session): the AI writes a **deck-spec JSON** —
ordered slide list, which objects/series each slide shows, bullets, speaker
notes — grounded in the explain/visualize digests; a deterministic
`build_pptx.py` **renders** that spec to `.pptx` using **python-pptx**
(required dependency, no stdlib fallback). Unlike the dashboard, slide
selection is itself AI judgment: the primary audience is engineering
consultants presenting to stakeholders, so the default deck is a story, not an
inventory. Physical-data tables (E-V curves etc.) are available slide types
but not part of the default story.

All four v1.0 decision points are resolved, plus five workflow decisions from
the second grill round (intake, ruleset handling, speaker notes, example
commit, provenance); §7 records the outcomes.

## 1. Requirements & Constraints

- **REQ-001**: New skill `skills/present-riverware-model/` with `SKILL.md` + `build_pptx.py`, plus the thin bridge `.claude/skills/present-riverware-model/SKILL.md`, following the existing skill layout (PAT-001).
- **REQ-002**: Output is a single `.pptx` written next to the model as `<modelname>_deck.pptx` (`-o` to override), openable without repair prompts in PowerPoint desktop (2016+), PowerPoint for the web, and LibreOffice Impress.
- **REQ-003**: Slide-type vocabulary the renderer supports and a spec may reference (core story types first — decision 2026-08-28):
  - `title` — model name, file, run horizon, timestep, object counts, date.
  - `network` — object-network schematic as native shapes and connectors (presenter can nudge nodes), reusing the layered layout and flow/data edge classification from `digest_to_json.py`.
  - `summary` — objects-by-type table with short descriptions.
  - `policy` — ruleset narrative: agenda order, rule-group roles, key thresholds; content leans on the explain digest. Highest-value section for stakeholder decks.
  - `series` — native line chart (python-pptx chart part, editable in PowerPoint) for chosen Object.Slot result series; NaN entries become gaps, same sparse-series rule as the dashboard.
  - `table` — physical-data lookup table (Elevation Volume, Max Release, Guide Curve…) as a native table, paged/truncated with an "N more rows" note. Available on request in the spec; **not** in the `--auto` baseline.
  - `chart-xy` — curve chart for lookup tables (e.g. E-V curve) when the spec asks.
  - `bullets` — free narrative slide (spec-supplied text only, for story glue).
  - `caveats` — standing "generated from the .mdl; verify against RiverWare" closing slide, always last.
- **REQ-004**: Deck-spec JSON is the single interface between AI judgment and the renderer (pattern: annotate's proposal JSON). Shape: `{"deck_title": …, "template": null | "path.pptx", "slides": [{"type": "<REQ-003 type>", "id": "<stable-id>", "refs": {…object/slot/table selectors…}, "bullets": […], "notes": "…"}]}`. Renderer validates: unknown type or unresolvable ref → reported error listing valid targets, non-zero exit, no partial deck.
- **REQ-005**: `--auto` escape hatch: with no spec, the script generates and renders a generic baseline spec (title, network, summary, policy skeleton, top-N reservoir series, caveats) for smoke tests and non-AI users, and writes that spec JSON next to the deck so it can be edited and re-rendered.
- **REQ-006**: Deterministic rendering: same spec + same model → equivalent `.pptx` on every run (fixed core-properties timestamps; byte-identical is the target, verified in tests — see RISK-004 if python-pptx internals prevent it).
- **REQ-007**: `--template <file.pptx>` inherits a user/client theme (colors, fonts, master) — v1, best-effort (decision 2026-08-28): defensive placeholder lookup, documented as "works with most templates, guaranteed with none"; SKILL.md review step catches mismatches. Default: one clean built-in theme matching the dashboard palette.
- **REQ-008**: Never read the raw `.mdl` (AGENTS.md hard rule); extraction goes through the shared parser/digest. Refactor the extraction half of `digest_to_json.py` into an importable `build_digest(mdl_path) -> dict` both skills call.
- **SEC-001**: All writes stay inside the user's working directory; skill inherits the "stay inside the working directory" rules verbatim from the existing skills.
- **REQ-009**: Intake before spec-writing (decision 2026-08-28, round 2 — always ask, rich): audience (stakeholder vs technical), rough length, emphasis (policy vs results vs physical data), client template to inherit (REQ-007), and — when the digest shows no embedded ruleset — whether a `.rls` is available. One structured question set, not a drawn-out interview.
- **REQ-010**: Ruleset handling (decision 2026-08-28, round 2): if no ruleset is embedded and none provided at intake, the deck ships without the policy section and the summary slide carries a visible "ruleset not included" note — never silently thinner. The `.rls` path recorded inside the `.mdl` is reported, not opened (working-directory rule).
- **REQ-011**: Speaker notes are **factual annotations**, not a talk track (decision 2026-08-28, round 2): terse per-slide notes naming data sources (Object.Slot), caveats, and table/series provenance — safe when the deck is forwarded to clients. No spoken-style script.
- **REQ-012**: Slide footer: model filename + generation date, no AI/tooling mention (decision 2026-08-28, round 2 — consistent with annotate GUD-002: reviewed content is human-endorsed; the footer is a staleness signal, not attribution).
- **SEC-002**: Spec bullets and speaker notes must contain nothing conversation-derived beyond the model's own content (privacy vigilance — decks get emailed around more than dashboards). Stated explicitly in SKILL.md.
- **CON-001**: Requires `python-pptx` (decision 2026-08-28 — target users are consultants who have pip; see ALT-001). Missing import → clear message naming `pip install python-pptx`, exit. No stdlib fallback deck.
- **CON-002**: ASCII-safe console output (Windows cp1252); deck text itself is UTF-8 via python-pptx.
- **CON-003**: Renderer stays dumb: no content selection logic beyond `--auto`'s generic baseline. What belongs in the deck is the spec's (AI's) job; keeping judgment out of the script is what keeps the output reviewable.
- **GUD-001**: SKILL.md instructs the AI to build a *story* spec (~10–15 slides typical): orient (network/summary) → policy narrative → evidence (series) → caveats, sized to the model and the user's stated audience; the spec is shown to the user for review before or alongside the deck.
- **PAT-001**: Mirror existing conventions: full skill under `skills/`, bridge under `.claude/skills/`, committed example output under `examples/`, `${CLAUDE_PLUGIN_ROOT}` path guidance in SKILL.md, tests under `tests/`.

## 2. Implementation Steps

### Implementation Phase 1 — shared extraction + renderer skeleton

- GOAL-001: Importable digest and a python-pptx renderer that opens cleanly everywhere.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Refactor `digest_to_json.py`: move digest construction (objects, links, tables, series, layered layout coordinates) into `build_digest(mdl_path) -> dict`; dashboard CLI behavior unchanged (regression: regenerate `examples/ArborBasin/ArborBasin_dashboard.html`, confirm identical). | Yes | 2026-08-28 |
| TASK-002 | Renderer skeleton `skills/present-riverware-model/build_pptx.py`: CLI `python build_pptx.py <model.mdl> (--spec deck.json | --auto) [--template t.pptx] [-o out.pptx]`; python-pptx import guard with install message (CON-001); spec load + validation (REQ-004); `title`, `bullets`, `caveats` slide types; fixed core-properties for determinism (REQ-006). Verify output opens without repair in PowerPoint desktop/web and LibreOffice; record matrix in `reference.md`. | Yes | 2026-08-28 |
| TASK-003 | `reference.md`: spec JSON schema (authoritative copy), slide-type reference with required refs per type, determinism notes, template best-effort caveats, compatibility matrix. | Yes | 2026-08-28 |

### Implementation Phase 2 — full slide vocabulary

- GOAL-002: Every REQ-003 slide type rendered and tested.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-004 | `network` slide: map the dashboard's layered layout onto EMU slide coordinates; nodes as rounded rectangles colored by object type, flow links solid connectors, data links dashed; legend. Overflow rule: past N objects drop slot labels then shrink fonts; report readability concerns on stdout. | Yes | 2026-08-28 |
| TASK-005 | `summary`, `table` slide types: native tables, paging/truncation with "N more rows" (REQ-003 caps as documented tuning constants). | Yes | 2026-08-28 |
| TASK-006 | `series` and `chart-xy` slide types: native python-pptx charts (line for time series with date axis and NaN gaps; scatter/line for lookup curves); dashboard palette. | Yes | 2026-08-28 |
| TASK-007 | `policy` slide type: renders agenda-ordered rule/group list with spec-supplied one-liners; renderer draws structure from the digest, wording comes from the spec (CON-003). | Yes | 2026-08-28 |
| TASK-008 | `--auto` baseline spec generator (REQ-005) + `--template` theme inheritance with defensive placeholder lookup (REQ-007). | Yes | 2026-08-28 |
| TASK-009 | Tests `tests/test_pptx.py`: spec validation errors (unknown type, bad ref) listed and fatal; determinism (two runs compared, REQ-006); table paging; empty-results model renders spec without series slides when spec omits them and `--auto` skips them; template fallback when placeholders missing; zip inventory + XML well-formedness of emitted parts. Small fixture digest; full models smoke-only. | Yes | 2026-08-28 |

### Implementation Phase 3 — the skill

- GOAL-003: A SKILL.md that produces story-quality specs and drives spec → render → review.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Write `skills/present-riverware-model/SKILL.md`: digest first (explain + build_digest); run the REQ-009 intake (audience, length, emphasis, template, ruleset if none embedded); write the deck-spec JSON per GUD-001 (story arc, grounding rule SEC-002, REQ-011 note style, E-V tables only when the model's physical data *is* the story); render; review checklist (open the deck, schematic readable, charts look like results, notes read aloud sensibly, template mismatches). Include working-directory rules and `${CLAUDE_PLUGIN_ROOT}` guidance verbatim from existing skills, plus the python-pptx prerequisite up front. | Yes | 2026-08-28 |
| TASK-011 | Frontmatter description for trigger matching: "Create a PowerPoint presentation, slide deck, or briefing that explains a RiverWare model — use when asked for slides, a deck, a .pptx, or a presentation about a model." Add bridge `.claude/skills/present-riverware-model/SKILL.md`. | Yes | 2026-08-28 |

### Implementation Phase 4 — examples and repo integration

- GOAL-004: Committed demonstration deck and repo wiring.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-012 | Full workflow on `examples/ArborBasin/ArborBasin.mdl`; commit `ArborBasin_deck.pptx` + its spec JSON (the reviewable artifact). Owner verification: open in PowerPoint, present-mode sanity check. Smoke-only (not committed) on saratoga, including a `--template` run against any handy corporate-style template. | Yes | 2026-08-28 |
| TASK-013 | Update `README.md` (feature bullet + python-pptx prerequisite), `AGENTS.md` (layout tree + skill list), bump `.claude-plugin/plugin.json`; note the digest refactor in the visualize SKILL.md if paths changed. | Yes | 2026-08-28 |

## 3. Alternatives

- **ALT-001**: Stdlib-only OOXML writer (v1.0 recommendation). Rejected 2026-08-28: primary users are engineering consultants already running python workflows — pip is available to them before Claude Code is. The zero-dependency guarantee mattered less than assumed for this skill, and hand-rolled OOXML added a phase of work plus repair-prompt risk. A try-import/degrade dual path was considered and rejected in the same session: the fallback writer is the expensive half, serving an audience judged small.
- **ALT-002**: Export the existing HTML dashboard to slides (print-to-PDF or headless-browser screenshots). Rejected: image output — not editable, not presentable text, worse dependency than pip.
- **ALT-003**: Script-selected slides with caps (dashboard-parity deck, or fixed executive subset). Rejected 2026-08-28: slide selection is judgment about audience and story, exactly what the AI layer is for; a parity deck punishes the audience with completeness. The `--auto` baseline preserves a no-AI path without baking editorial logic into the renderer.
- **ALT-004**: Defer client-template support to v2. Rejected 2026-08-28: with python-pptx it is cheap, and consultants under mandated templates would otherwise rebuild the deck by hand, halving the skill's value. Shipped best-effort in v1 (REQ-007).
- **ALT-005**: MCP server capability instead of a skill. Rejected: MCP prototype not stable (same reasoning as annotate ALT-001), and deck generation is a batch file-in/file-out job — exactly the skill pattern.

## 4. Dependencies

- **DEP-001**: `skills/explain-riverware-model/explain.py` — parser underlying the digest, and source for policy-narrative facts.
- **DEP-002**: `skills/visualize-riverware-model/digest_to_json.py` — digest + layout logic refactored into `build_digest` (TASK-001).
- **DEP-003**: `python-pptx` (pip; pulls `lxml`, `Pillow`) — first external package in the repo; called out in README and SKILL.md prerequisites. Pin a minimum version, not an exact one.
- **DEP-004**: PowerPoint (or LibreOffice) for TASK-002 compatibility checks and TASK-012 owner verification — human actions; generation itself needs neither.

## 5. Files

- **FILE-001**: `skills/present-riverware-model/SKILL.md` — new skill (TASK-010, TASK-011).
- **FILE-002**: `skills/present-riverware-model/build_pptx.py` — spec renderer CLI (TASK-002, TASK-004..008).
- **FILE-003**: `skills/present-riverware-model/reference.md` — spec schema + slide-type reference + compatibility matrix (TASK-003).
- **FILE-004**: `.claude/skills/present-riverware-model/SKILL.md` — bridge (TASK-011).
- **FILE-005**: `skills/visualize-riverware-model/digest_to_json.py` — refactored for shared digest (TASK-001).
- **FILE-006**: `tests/test_pptx.py` + small fixture digest (TASK-009).
- **FILE-007**: `examples/ArborBasin/ArborBasin_deck.pptx` + spec JSON (TASK-012).
- **FILE-008**: `README.md`, `AGENTS.md`, `.claude-plugin/plugin.json` — wiring (TASK-013).

## 6. Testing

- **TEST-001**: Spec validation — unknown slide type or unresolvable object/slot ref is a listed, fatal error; no partial deck (REQ-004).
- **TEST-002**: Determinism — two runs on the same spec+model compare equal (REQ-006).
- **TEST-003**: Every slide type renders from the fixture digest; emitted parts are well-formed XML and match the zip inventory.
- **TEST-004**: Table paging/truncation with "N more rows" (REQ-003 caps).
- **TEST-005**: Model without stored results: `--auto` emits no series slides; a spec that requests one gets the validation error, not an empty chart.
- **TEST-006**: `--template` — theme inherited when placeholders exist; graceful fallback (built-in layout) when they do not (REQ-007).
- **TEST-007**: Regression — dashboard output unchanged after the TASK-001 refactor (byte-compare regenerated ArborBasin dashboard).
- **TEST-008**: Manual compatibility matrix — deck opens without repair prompt in PowerPoint desktop, PowerPoint web, LibreOffice Impress; recorded in `reference.md` (TASK-002, TASK-012).

## 7. Risks & Assumptions

Decision log (grill session, 2026-08-28) — supersedes the v1.0 DECISION items:

- **DECISION-1 resolved**: python-pptx, required, no stdlib fallback. Rationale: consultant audience has pip; fallback writer was the expensive half serving a small audience. (Interim "try import, degrade" position was itself grilled and dropped.)
- **DECISION-2 resolved**: `present-riverware-model` — verb-first, matches sibling naming.
- **DECISION-3 resolved**: `--template` in v1, best-effort (REQ-007).
- **DECISION-4 resolved**: AI selects slides via required deck-spec JSON; `--auto` escape hatch; core vocabulary = schematic/summary, policy narrative, results series; physical-data tables optional spec types only ("fine for proof of concept, not as important in real work").

Round 2 (same date):

- **DECISION-5 resolved**: Intake is a rich, always-asked question set (REQ-009) — owner chose fit over friction; the consultant audience tolerates a short intake for a correctly aimed deck.
- **DECISION-6 resolved**: Missing ruleset → ask at intake, omit policy section with a visible note if unavailable (REQ-010).
- **DECISION-7 resolved**: Speaker notes are factual annotations, not a presenter talk track (REQ-011) — forward-safety over presentability.
- **DECISION-8 resolved**: Commit the ArborBasin `.pptx` + spec JSON (zero-effort demo artifact; TASK-012 unchanged).
- **DECISION-9 resolved**: Footer = model filename + date, no AI/tooling mention (REQ-012).

Risks:

- **RISK-001**: python-pptx chart/table API limits (e.g. date-axis quirks on line charts, no per-point gap control) forcing workarounds. Mitigated: TASK-006 is scheduled early enough to swap chart style (category axis with year-month labels) without touching the spec schema.
- **RISK-002**: Schematic legibility on a fixed 13.33"×7.5" slide for large models — worse than HTML pan/zoom. Mitigated by TASK-004 overflow rules and SKILL.md instructing the AI to flag (not hide) a tangled layout.
- **RISK-003**: Spec drift — AI bullets asserting policy behavior the digest does not support. Mitigated by the SKILL.md grounding rule (digest facts only), the spec being the review artifact, and the review checklist.
- **RISK-004**: python-pptx internals (part ordering, generated ids) may frustrate byte-identical output. Fallback stance: REQ-006 relaxes to structural equality (unzip + normalized XML compare) in tests; committed example still regenerates honestly from its spec.
- **RISK-005**: Arbitrary client templates with nonstandard masters break placeholder lookup. Accepted per REQ-007's best-effort contract; TEST-006 covers the graceful-fallback path.
- **ASSUMPTION-001**: The dashboard's layered layout coordinates transfer to slide geometry without a new layout engine.
- **ASSUMPTION-002**: python-pptx (latest) runs on Python 3.10+ on Windows/macOS/Linux wheels without compilation for target users.

## 8. Related Specifications / Further Reading

- `plan/feature-annotate-model-1.md` — the deterministic-script + AI-judgment-via-JSON pattern this plan reuses (proposal JSON → deck-spec JSON)
- `skills/visualize-riverware-model/SKILL.md` — digest content and review checklist being adapted
- `AGENTS.md` — repository conventions, never-read-a-`.mdl`-raw rule
- [python-pptx documentation](https://python-pptx.readthedocs.io/) — presentation, chart, and template API

## 9. Implementation notes (2026-08-28)

Where the build differs from the plan as written, and why.

- **TASK-001, layout coordinates stay out of the digest.** `build_digest`
  already existed, so the refactor was a widening, not an extraction. The
  layered layout was ported from `template.html` into `layout_nodes()` and
  exported as a function rather than added to the digest dict: the dashboard
  embeds the digest verbatim, so a new key would change every committed
  dashboard. Policy is likewise opt-in (`build_digest(path,
  include_policy=True)`, CLI `--policy`). Both dashboards regenerate
  byte-identically under the refactored script.
- **TEST-007 asserts the property, not the committed file.** The committed
  `ArborBasin_dashboard.html` already differed from what the *old* code
  produced, from before this work: it predates the annotations that were
  applied to `ArborBasin.mdl`, so its object descriptions are empty. The
  regression was therefore verified as old-code output versus new-code output
  (byte-identical for both example models), and the test asserts the digest key
  set and that no HTML output can embed the policy tree. Regenerating the
  committed dashboards is a separate, unrelated change.
- **REQ-006 achieved as byte-identical; RISK-004 did not materialise**, but
  only after normalising the *embedded chart workbook*. A chart's data is an
  `.xlsx` inside the `.pptx` — a zip within a zip, with its own entry
  timestamps and its own creation date. Byte-identical output also requires a
  pinned date (`--date`, or `date` in the spec), because the footer carries the
  generation date by REQ-012.
- **`refs.groups` orders as well as filters** on a `policy` slide. An
  `ASCENDING` set is stored in the reverse of its firing order, and which order
  a room should see is spec-author judgment, not renderer logic (CON-003). The
  `#` column remains the rule's agenda position in the full set, matching
  `explain.py`'s numbering.
- **Network slides scale each axis separately**, bounded by an absolute node
  size and by each other. Uniform scaling wasted the lower half of the slide on
  wide basins and blew a three-object model off the edge. Readability is
  reported when labels fall under 8 pt or the object count passes 45 — the
  ArborBasin example takes the SKILL.md's own advice and splits the schematic
  into a west-basin and an east-basin slide, which clears the warning.
- **Figure captions are measured, not counted.** Reserved height comes from
  estimated wrapped line count and shrinks 14 → 12 → 10 pt against a share of
  the body area, so a long caption cannot push text over the footer or starve
  the figure.
- **TASK-012 example is 14 slides** (title, agenda, two network, summary, five
  policy, levers, two series, caveats), committed with its spec. It regenerates
  byte-identically from that spec.
- **TEST-008 remains open.** Package structure, content-type inventory, XML
  well-formedness and slide geometry are asserted on every build. Opening the
  deck in PowerPoint desktop, PowerPoint for the web and LibreOffice Impress is
  an owner action; the matrix in `reference.md` section 8 records those rows as
  pending. A `--template` run against a real corporate template is likewise an
  owner check — the automated coverage uses a synthetic template for both the
  inheritance and the missing-layout fallback paths.
