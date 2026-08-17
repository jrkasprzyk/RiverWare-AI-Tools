# draft-riverware-rules — worked session

Produced with [draft-riverware-rules](../../skills/draft-riverware-rules/SKILL.md)
against the [TwoResOps](../TwoResOps/) model and human-polished. Unlike the
[rule case study](../TwoResOps/saratoga_v2.4_rule_case_study.md), which shows
the shape of a finished deliverable, this file shows the **conversation** — how
a plain-language request becomes a grounded draft, including the moment the
skill refuses to invent a slot that does not exist. The request is constructed
for the example; every model fact below comes from the parser digest and the
embedded ruleset of `saratoga_v2.4.mdl`.

---

**Request.** "The river below Roberto goes bone dry in late summer. Add a rule
so Roberto always releases at least some minimum flow for the channel itself,
not just what the farms ordered."

---

**Grounding.** From the digest
(`python skills/explain-riverware-model/explain.py examples/TwoResOps/saratoga_v2.4.mdl`)
and the embedded `RPL Set`:

- The `Roberto Rules` group fires, in execution order (`ASCENDING` agenda —
  bottom of the listing first): `Pass-Through Flow for Winifred Farms`,
  `Downstream Ecological Flow`, `Flood Control`, `Avoid City Flooding`,
  `Prevent Overtopping`. Each later rule has higher priority and can overwrite
  the release set before it.
- The model already has a minimum-flow idiom to copy: Cora's
  `Minimum Fish Flow` rule raises `Cora.Release` to
  `Pescado Fishery.Min Fish Flow` via `"GetPossibleRelease"` only when the
  release is below the floor. The draft mirrors that rule exactly.
- **The threshold slot does not exist.** The model's precedent is to keep the
  floor on the protected reach (`Pescado Fishery.Min Fish Flow`, a scalar),
  but the reach below Roberto — `Winifred Valley Reach` — has no such slot,
  and neither does Roberto. Drafting alone cannot add a slot.

**The choice the user had to make.** Two honest options, stated before any
RPL was written:

1. Create a scalar slot `Winifred Valley Reach.Min Flow` in RiverWare first
   (matching the Pescado Fishery pattern), then reference it — the better
   long-term shape, and it keeps the threshold visible and editable in the
   model rather than buried in a rule.
2. Hard-code a literal now and accept that changing the floor means editing
   the rule.

The user chose the literal (`5 cms`) to test the behavior first, with the slot
migration noted as the follow-up.

---

**The draft.**

```rpl
RULE "Minimum Channel Flow Below Roberto";
DESCRIPTION "Keep the reach below Roberto wet: raise the release to the
channel minimum when the rules before this one left it lower. Flood rules
fire later and keep priority over this floor.";
ACTIVE TRUE;
BEGIN

  $ "Roberto.Release" [] := IF ( $ "Roberto.Release" [] < 5.00000000 "cms" )
 THEN
  "GetPossibleRelease"( % "Roberto", 5.00000000 "cms" )
 ENDIF;

END
```

**Reads:** `Roberto.Release` (as set by the rules that fired before it).
**Sets:** `Roberto.Release`.

**Agenda placement.** Insert in the `Roberto Rules` group, **listed between
`Flood Control` and `Downstream Ecological Flow`**. With `ASCENDING` order
that means it fires after the pass-through and ecological-flow rules — so the
floor applies to whatever release they produced — while `Flood Control`,
`Avoid City Flooding`, and `Prevent Overtopping` still fire later with higher
priority. The consequence, said out loud: **during a flood emergency,
`Avoid City Flooding` can cut the release below 5 cms.** If the floor must
survive even that, list the rule above `Avoid City Flooding` instead — but
then a flooding city cannot buy relief from this water, which is a policy
decision, not a syntax one.

**Assumptions made.**

- 5 cms is a placeholder magnitude, chosen by the user for testing — not
  derived from any habitat analysis.
- The floor applies year-round. A seasonal floor would mirror the
  `"FloodSeason"()` utility-function pattern already in the ruleset.
- `"GetPossibleRelease"` caps the floor at what Roberto can physically
  release at its current elevation (its `Max Release` table reaches zero near
  dead pool), so the rule cannot demand water the outlet works cannot pass.

**Review before use.** This is a draft. Load it in RiverWare's RPL editor,
check units and slot references, and test-run before trusting it. RPL is only
validated by RiverWare itself.

---

## What this demonstrates

| Skill behavior | Where it shows up |
|---|---|
| Digest before drafting | Agenda order and the existing minimum-flow idiom came from the parser, not from memory |
| Never invent slot names | The missing threshold slot became an explicit user choice, not a fabricated `Roberto.Min Flow` reference |
| Mirror the model's idiom | The draft is structurally identical to the existing `Minimum Fish Flow` rule, down to `"GetPossibleRelease"` |
| Placement with consequences | The flood-vs-floor priority tradeoff is stated as a policy decision the modeler owns |
| Always end unvalidated | The review caveat closes the draft |
