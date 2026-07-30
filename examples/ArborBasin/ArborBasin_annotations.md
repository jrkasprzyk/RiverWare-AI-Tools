# Proposed annotations — ArborBasin.mdl

**40 annotations proposed, of 1,116 available targets (3.6%).** Nothing already
described is touched. Produced by the `annotate-riverware-model` skill; this is
the review artifact the modeler approves before `annotate.py` writes anything.

Companion machine proposal: `ArborBasin_annotations.json`.

| Surface | Proposed | Available | Already described |
|---|---|---|---|
| Model description | 1 | 1 | 0 |
| Object descriptions | 10 | 41 | 0 |
| Slot descriptions | 15 | 1,017 | 11 |
| RPL set / group / rule / function | 11 | 57 | 1 |
| Expression comments (`COMMENTED_BY`) | 3 | — | — |

**This model is the volume test.** It has 1,028 slots, and 15 of them are
proposed for a description — under 1.5%. Nearly all the rest are standard
power-reservoir plumbing (`Turbine Release with Down Reserve`,
`Regulated Spill Capacity with Up Reserve`, thirty-odd LP-parameter tables per
reservoir) which carry no model-specific policy meaning. Describing them would
bury the fifteen that matter.

---

## Model description

1. **(model)** — "Arbor Basin is the CADSWES training model: a west basin of
   five reservoirs in series (Aspen, Birch, Cedar, Dogwood, Elm) and an east
   basin centered on Hickory, linked by a transbasin diversion from Cedar into
   Hickory's inflow. The east basin serves irrigation districts and an
   interstate minimum flow requirement."
   *Rationale: the file currently offers a reader no orientation at all.*

## Object descriptions

Ten of forty-one. Every reservoir, the diversion that links the two basins, the
gage that carries the interstate requirement, the aggregate irrigation site
whose rights drive the Hickory rules, and the data object that holds the
system totals.

2. **Aspen** — "Top reservoir of the west-basin power cascade. Its tailwater is
   set by Birch's pool elevation, so Birch's level directly controls the head on
   Aspen's turbines." *Rationale: the head coupling is a link, invisible from
   the object itself.*
3. **Birch** — the other half of that coupling.
4. **Cedar** — "Storage workhorse of the west basin and the source of the
   transbasin diversion. Its Diversion Min Elevation is the floor below which
   the diversion to the east basin is cut off entirely."
5. **Dogwood** — "Power reservoir below Cedar that also diverts directly to
   Dogwood Irrigation. Its tailwater is set by Elm's pool elevation."
6. **Elm** — "Bottom reservoir of the west cascade. It is operated to a Pool
   Elevation Target rather than a guide curve, and it honors an externally
   supplied Spill Required series when one is input."
   *Rationale: Elm is the one cascade reservoir that does not follow a guide
   curve — worth saying once, on the object.*
7. **Hickory** — "Storage reservoir at the head of the east basin… It balances
   Juniper Irrigation deliveries, the interstate flow requirement, and its own
   minimum pool."
8. **Transbasin Diversion** — "Moves water from Cedar in the west basin into
   Hickory's inflow in the east. It is the structural hinge of the model: what
   the west basin can spare determines what the east basin has to work with."
9. **Interstate Flow Requirement** — "Gage where the downstream interstate
   minimum flow is enforced and its violation measured. It holds the requirement
   itself rather than any physical routing."
   *Rationale: it is typed `StreamGage` and named like a constraint; a reader
   needs to know which it is.*
10. **Juniper Irrigation** — "Aggregate diversion site serving four irrigation
    districts below Hickory. Its unmet request is what drives Hickory both to
    cut its own diversion and to supplement releases from storage."
11. **System Data** — "Data object holding basin-wide totals computed by the
    Post-processing rules: spill volume, depletion shortage, and energy summed
    across all reservoirs."

**Not proposed (31):** every reach, canal, groundwater store, individual
irrigation district, confluence, and inline power object. Their names and types
already say what they are, and none holds a policy decision.

## Slot descriptions

Fifteen of 1,017. Each is read by a rule, holds a policy threshold, is a
decision variable, or is a reported metric.

12. **Cedar.Diversion Min Elevation** — "Pool elevation below which no water is
    available to the transbasin diversion…"
    *Rationale: the single most consequential threshold in the model.*
13. **Cedar.Guide Curve** — "Monthly target pool elevation… On non-month-end
    days the rule forecasts toward this same target rather than chasing it
    daily." *Rationale: the forecast-vs-solve distinction is invisible here.*
14. **Aspen.Elevation Guide Curve** — monthly target for Aspen.
15. **Birch.Outflow Target** — "Desired release from Birch, applied after the
    elevation limits have had their say." *Rationale: firing order matters.*
16. **Elm.Pool Elevation Target** — "Elm has no guide curve; this scalar is what
    the rule solves toward each timestep."
17. **Elm.Spill Required** — "Optional externally supplied spill. Where a value
    is input for a timestep, Elm must pass at least that much, and the
    pool-elevation target rule yields to it."
    *Rationale: a slot that is sometimes input and sometimes absent, with
    different policy consequences either way, is exactly what a description is
    for.*
18. **Hickory.Pool Elevation Min to Supplement Irrigation** — "…It sits above
    Pool Elevation Min, so supplementing stops well before the hard minimum."
    *Rationale: the relationship between the two minimums is the point.*
19. **Interstate Flow Requirement.Min Flow** — "…The policy never requires more
    than the natural inflow available at Gage Above Hickory, so in a dry period
    the effective requirement is the inflow itself."
    *Rationale: a reader would otherwise assume this is a hard floor.*
20. **Interstate Flow Requirement.Min Flow Violation** — "Zero unless the gage
    outflow falls more than a small tolerance below the requirement."
21. **Juniper Diversion.Minimum Diversion Bypass** — "…This is how the
    interstate requirement is actually enforced."
22. **Transbasin Diversion.Diversion Schedule Monthly** — the monthly input.
23. **Transbasin Diversion.Diversion Request** — "It is not an input:
    initialization rules derive it from the monthly schedule and may then scale
    it per trace." *Rationale: prevents someone editing a slot that gets
    overwritten before the run starts.*
24. **System Data.Spill Volume**
25. **System Data.Depletion Shortage**
26. **System Data.Energy** — "…every power reservoir plus Mulberry Canal Power."
    *Rationale: the inclusion of the canal power plant is not guessable.*

**Not proposed:** the ~1,000 remaining slots. In bulk these are the standard
`LevelPowerReservoir` inventory — reserve-scenario series, LP-parameter tables,
tailwater lookup tables, drift indices — replicated across six reservoirs. The
elevation limits (`Pool Elevation Max`, `Pool Elevation Min`) are read by rules
and so pass the first half of the policy-meaning test, but their names are their
definitions, so they fail the second: a description would restate the name.

## RPL descriptions

Eleven of 57. Twelve of the model's rules are named `<Reservoir> Elevation Max`,
`<Reservoir> Elevation Min`, or `<Reservoir> Outflow Min`; none is proposed,
because in each case the name is the behavior.

27. **`Arbor Basin Rules (from MRM run)`** (set) — one-paragraph statement of
    the policy.
28. **`…/Post-processing`** (group) — "Reporting rules that run after the policy
    rules have set flows… and set no releases."
29. **`…/Post-processing/Interstate Flow Requirement Violation`** — the capped
    requirement and the tolerance.
30. **`…/Hickory Rules/Hickory Elevation Min Reduce Diversion`** — "It reduces
    the request rather than the release, so downstream deliveries are protected
    first." *Rationale: which quantity gets cut is the whole content of the
    rule, and the name does not say.*
31. **`…/Hickory Rules/Reduce Hickory Diversion`** — "…honoring Juniper's senior
    rights. It issues a warning so the reallocation is visible in the run log."
32. **`…/Hickory Rules/Supplement Juniper from Hickory Storage`** — "…but only
    down to Pool Elevation Min to Supplement Irrigation. Below that elevation
    the shortage stands."
33. **`…/Hickory Rules/Hickory Pass Natural Flows for Juniper and Interstate`** —
    "Sets Hickory's baseline release to the smallest of three limits…"
    *Rationale: a three-way `MinItem` deserves its terms spelled out.*
34. **`…/Hickory Rules/Interstate Flow Requirement`** — "Despite the name, this
    sets no flow requirement directly: it tells the Juniper Diversion how much
    to bypass, which is what actually delivers the interstate minimum flow."
    *Rationale: the clearest case in the model of a name that misleads.*
35. **`…/Elm Rules/Elm Required Spill`** — "…Sets nothing on timesteps where no
    value was input."
36. **`…/Transbasin Diversion/Cedar Available for Diversion`** — the availability
    formula and its zero case.
37. **`Initialization Rules Set/Transbasin Diversion/ Trace Diversion Schedule
    Variation`** — "Perturbs the transbasin diversion request for one trace
    only, so a multiple-run study can compare a reduced schedule against the
    baseline." *(Note the leading space in this rule's name — it is part of the
    name as stored, and the proposal path reproduces it exactly.)*

**Not proposed:** the reservoir policy groups, all twelve elevation-limit and
outflow-minimum rules, `Energy Cumulative`, `System Spill`,
`System Depletion Shortage`, `System Energy`,
`Convert Monthly Diversion Schedule to Daily Diversion Request`,
`Convert Hickory Monthly Diversion Schedule to Daily Diversion Request`,
`Dogwood Available for Diversion`, `Aspen Operate to Guide Curve`,
`Elm Pool Elevation Target`, `Birch Outflow Target`, and
`Cedar End of Month Guide Curve` — names that are their own descriptions.

## Expression comments

Three, one per rule, all on magic numbers whose value is not derivable from
context.

38. **`…/Post-processing/Interstate Flow Requirement Violation`** on
    `0.10000000 "cms"` — "Tolerance band: misses smaller than this are treated
    as rounding, not violations."
39. **`…/Aspen Rules/Cause Sporadic Error`** on `220.00000000 "m"` — "Lower end
    of the elevation range this model is calibrated for; below it the run is
    halted rather than allowed to produce misleading results."
    *Rationale: the rule's existing description reads only "Range is 205 - 242",
    which does not explain what 220 is doing in the test.*
40. **`Initialization Rules Set/…/ Trace Diversion Schedule Variation`** on
    `0.90000000` — "Trace 1 runs the schedule at 90 percent of the baseline
    request." *Rationale: a bare unitless multiplier with no other clue.*

**Not proposed:** the `0.00000000 "kcfs"` floors in `Aspen Operate to Guide
Curve` and `Elm Pool Elevation Target` already carry the modeler's own
"Do not let flow be negative" comment.

---

## Skipped — already described, left untouched (REQ-005)

- **Slots (11):** the eleven `Subbasin Membership List Slot` descriptions
  RiverWare generates on the subbasin list slots.
- **Rules (1):** `Arbor Basin Rules (from MRM run)/Aspen Rules/Cause Sporadic
  Error` ("Range is 205 - 242"). Its rule description is kept as written;
  proposal 39 adds a comment on the literal instead of touching it.

---

## Before trusting this

Only RiverWare validates a `.mdl`. Load the annotated model in RiverWare and
confirm the descriptions appear where they should — the open-object dialog, the
slot dialog, and the RPL editor's description tab — before trusting it.
