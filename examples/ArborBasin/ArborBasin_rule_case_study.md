# Arbor Basin — rule-drafting case study

*A request → rule walkthrough produced with the
[draft-riverware-rules](../../skills/draft-riverware-rules/SKILL.md) skill and
human-polished. It shows the shape of a delivered draft: grounded in the
model's digest, written in the model's own idiom, placed deliberately in the
agenda, and explicitly flagged as unvalidated.*

## The request

> "Add a spring flood-control drawdown for Cedar — in March through May, keep
> the pool a couple of meters below the guide curve so there is space to catch
> the snowmelt."

## Grounding in the model

From the parser digest of `ArborBasin.mdl`:

- Cedar is a storage reservoir with the slots the rule needs: `Cedar.Outflow`,
  `Cedar.Inflow`, `Cedar.Storage`, `Cedar.Pool Elevation`, and a monthly
  `Cedar.Guide Curve` periodic slot (values 231–235).
- The existing `Cedar Rules` policy group fires, in execution order:
  `Cedar End of Month Guide Curve` (the base operation), then
  `Cedar Outflow Min`, `Cedar Elevation Min`, and `Cedar Elevation Max` as
  overriding safeguards.
- The ruleset's idiom: `IF` expressions inside assignments, quoted predefined
  functions (`"SolveOutflow"`, `"ElevationToStorage"`,
  `"GetMaxOutflowGivenInflow"`), units on every literal, and physical caps
  applied with `"Min"`/`"Max"` wrappers.

The request supplies no slot for the drawdown offset, so the draft uses a
literal `2 "m"` below the Guide Curve. If the offset should be tunable (for
example, by an external workflow through the input DMI), Cedar needs a new
scalar slot for it first — drafting alone cannot create one.

## The draft

```rpl
RULE "Cedar Spring Flood Drawdown";
DESCRIPTION "March-May: hold Cedar 2 m below the Guide Curve to preserve
flood space for snowmelt.";
ACTIVE TRUE;
BEGIN

  $ "Cedar.Outflow" [] := IF ( "GetMonth"( @"t" ) >= 3.00000000 AND
                               "GetMonth"( @"t" ) <= 5.00000000 AND
                               $ "Cedar.Pool Elevation" [] >
                                 $ "Cedar.Guide Curve" [] - 2.00000000 "m" )
 THEN
  "Min"( "SolveOutflow"( % "Cedar", $ "Cedar.Inflow" [],
                         "ElevationToStorage"( % "Cedar",
                             $ "Cedar.Guide Curve" [] - 2.00000000 "m" ),
                         $ "Cedar.Storage" [@"t - 1"], @"t" ),
         "GetMaxOutflowGivenInflow"( % "Cedar", $ "Cedar.Inflow" [], @"t" ) )
 ENDIF;

END
```

**Reads:** `Cedar.Pool Elevation`, `Cedar.Guide Curve`, `Cedar.Inflow`,
`Cedar.Storage` (previous timestep).
**Sets:** `Cedar.Outflow`.

## Agenda placement

Insert the rule in the `Cedar Rules` policy group, **listed directly above
`Cedar End of Month Guide Curve`**. The ruleset uses `ASCENDING` agenda order
— the bottom rule of the listing fires first — so this placement means:

1. `Cedar End of Month Guide Curve` fires first and sets the routine
   operation;
2. the new drawdown rule fires next and, in spring, overrides it with the
   lower target;
3. `Cedar Outflow Min`, `Cedar Elevation Min`, and `Cedar Elevation Max` still
   fire afterward, so the existing floors and ceilings keep final priority
   over the drawdown.

Listing it at the top of the group instead would let the drawdown override the
elevation safeguards — almost certainly not what is wanted.

## Assumptions made

- "A couple of meters" became exactly `2 "m"`.
- "Spring" became calendar March–May (`"GetMonth"` 3–5).
- The rule only acts when the pool is *above* the drawdown target; it never
  adds water to reach it.

## Review before use

This is a draft. Load it in RiverWare's RPL editor, check units and slot
references, and test-run before trusting it. RPL is only validated by
RiverWare itself.
