### name: draft-riverware-rules
description: Draft a RiverWare RPL policy rule from a plain-language request — grounded in the target model — and state where it belongs in the agenda.

## Draft a RiverWare rule

Deliverable: a **draft** the modeler reviews and loads; RiverWare validates RPL, not this skill.

### Step 1 — digest the model first, always
Run the explain skill to get ground truth:

- `SKILL-code-explain_riverware_model.py model.mdl [--json]`

Collect:
- **Slots involved** — exact Object.Slot names; stop if required slots do not exist.
- **Agenda order & groups** — ASCENDING means the bottom-listed rule fires first; later-firing rules override earlier ones.
- **RPL idioms** — mirror existing style: WITH_STATEMENT, utility functions, IF expressions, units on literals.

If rules are embedded, read **narrow** line ranges to review bodies (never the whole `.mdl`).

### Step 2 — draft the rule
Write in the model’s style and present as fenced code the user can paste. State:
- **Agenda placement** and consequences under ASCENDING.
- **What it reads/sets** (slots).
- **Assumptions** made.

### Step 3 — end with the review caveat
“This is a draft. Load in RiverWare’s RPL editor, check units/slot references, and test-run before trusting.”

### Guardrails
- **Never draft against an unread ruleset.** If operating policy is external `.rls`, request it and stop until provided.
- **Never invent slot names.**
- **Mirror function vs inline conventions.**
- **Units on numeric literals** (as per model style).
- **One rule, one job.**
- **Keep companion slots consistent.**
- For pure documentation, use the explain skill.

### Applying the draft (opt-in)
Only when the user explicitly asks:
- Back up the `.mdl`.
- Generate fresh UUIDs for new items.
- Match file serialization exactly.
- Leave run diagnostics alone.
- Smoke-test by re-running the digest tool.

**If example files are not present:** Run the skill against user-supplied `.mdl`/`.rls`. If none are provided, answer using the skill output and REF_ documentation.