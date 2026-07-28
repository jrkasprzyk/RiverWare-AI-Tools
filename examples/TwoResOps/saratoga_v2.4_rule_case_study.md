# Saratoga — rule-drafting case study

*A request → rule walkthrough produced with the
[draft-riverware-rules](../../skills/draft-riverware-rules/SKILL.md) skill and
human-polished. It shows the shape of a delivered draft: grounded in the
model's digest, written in the model's own idiom, placed deliberately in the
agenda, and explicitly flagged as unvalidated.*

## The request

> "Add a drought cutoff: when Cora drops below its Level 2 elevation, stop
> irrigation deliveries to Winifred Valley Farms entirely until the pool
> recovers."

## Grounding in the model

From the parser digest of `saratoga_v2.4.mdl`:

- Cora carries exactly the trigger slot needed: the scalar `Cora.Level 2 PE`
  (alongside `Level 1 PE`, `Dead Pool`, and `Flood Control`).
- Irrigation deliveries are set by the existing `Irrigation` rule in the
  `Cora Rules` group, which writes both `Cora.Release` and
  `Winifred Valley Farms.Incoming Available Water` — a cutoff must set both,
  mirroring that rule.
- The `Cora Rules` group fires, in execution order: `Find Shortage Level`,
  `Irrigation`, `Minimum Fish Flow`, `Supplement for Downstream Eco Flow`,
  `Flood Control`, `Prevent Overtopping` — each later rule able to override
  the release set earlier.
- The model's idiom for exactly this maneuver already exists: the
  `Irrigation` rule uses an `IF_STATEMENT` block testing yesterday's pool
  elevation (`[@"t - 1"]`) and zeroing both slots with `0.00000000 "cfs"`.
  The draft copies that pattern rather than inventing a new one.

## The draft

```rpl
RULE "Drought Cutoff for Irrigation";
DESCRIPTION "Below Level 2 PE, suspend Winifred Valley Farms deliveries
entirely to protect remaining storage. Fish and ecological floors are
restored by the later rules in this group.";
ACTIVE TRUE;
BEGIN

  IF_STATEMENT ($ "Cora.Pool Elevation" [@"t - 1"] < $ "Cora.Level 2 PE" []) THEN
        $ "Cora.Release" [] := 0.00000000 "cfs";

        $ "Winifred Valley Farms.Incoming Available Water" [] := 0.00000000 "cfs";

  END_IF_STATEMENT;

END
```

**Reads:** `Cora.Pool Elevation` (previous timestep), `Cora.Level 2 PE`.
**Sets:** `Cora.Release`, `Winifred Valley Farms.Incoming Available Water`.

## Agenda placement

Insert the rule in the `Cora Rules` policy group, **listed between
`Minimum Fish Flow` and `Irrigation`**. With `ASCENDING` agenda order (bottom
rule fires first) that means:

1. `Find Shortage Level` and `Irrigation` fire first, setting the normal
   shortage-adjusted delivery;
2. the new cutoff fires next and zeroes it in drought;
3. `Minimum Fish Flow` and `Supplement for Downstream Eco Flow` still fire
   afterward, so the Pescado Fishery's floor and the Wildlife Sanctuary's
   supplement are restored on top of the cutoff — the drought rule starves
   the farms, not the river;
4. `Flood Control` and `Prevent Overtopping` keep final priority as before.

Note the interaction with the existing Shortage Table: between elevations
2144 and Level 2, deliveries are already cut 18 percent by
`Find Shortage Level`. This rule turns that graduated rationing into a hard
zero below Level 2 — if a step between 18 percent and zero is wanted instead,
the better edit is a new row in `Cora.Shortage Table`, not a new rule.

## Assumptions made

- "Until the pool recovers" is handled implicitly: the trigger re-evaluates
  every timestep against yesterday's elevation, so deliveries resume the day
  after the pool climbs back above Level 2. No hysteresis band was requested;
  if oscillation at the threshold proves a problem, a recovery offset would
  need a new scalar slot.

## Review before use

This is a draft. Load it in RiverWare's RPL editor, check units and slot
references, and test-run before trusting it. RPL is only validated by
RiverWare itself.
