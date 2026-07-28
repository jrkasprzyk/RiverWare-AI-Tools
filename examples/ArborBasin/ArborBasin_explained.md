# Arbor Basin — model narrative

*A narrative explanation of `ArborBasin.mdl` (RiverWare 9.4), produced with the
[explain-riverware-model](../../skills/explain-riverware-model/SKILL.md) skill
and human-edited. Regenerate the underlying structural digest with:*

```bash
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl
```

## Overview

Arbor Basin is the CADSWES RiverWare training model: a two-basin river system
with 41 simulation objects, run at a one-day timestep over calendar year 2018
(1 January 2018 through 1 January 2019). The model solves with rule-based
simulation using an embedded ruleset, `Arbor Basin Rules`, and carries
supporting initialization and MRM rule sets alongside it.

The system divides into a **west basin** — a five-reservoir stem running Aspen,
Birch, Cedar, Dogwood, Elm — and an **east basin** centered on Hickory
Reservoir, which supplies irrigation districts, an interstate minimum-flow
point, and a canal-and-groundwater conjunctive-use complex. A Transbasin
Diversion moves water from Cedar in the west basin to Hickory's inflow in the
east, and it is the structural hinge of the model: how much the west basin can
spare determines how much the east basin has to work with.

## Physical network

### West basin: the power cascade

**Aspen**, at the top of the watershed, is a level power reservoir (pool
elevations roughly 273–282) with a 68-row Plant Power Table and a monthly
Elevation Guide Curve holding the pool near elevation 274. Its Outflow passes
through the Aspen to Birch reach (time-lag routing) into **Birch**, a second
level power reservoir (elevations roughly 245–253). The two operate in tandem:
Aspen's Tailwater Base Value is linked to Birch's Pool Elevation, so Birch's
pool directly sets the head on Aspen's turbines.

Birch releases into **Cedar**, the west basin's storage workhorse. Cedar is a
storage reservoir (elevations roughly 196–243, spillway crest at 240.79) with a
monthly Guide Curve ranging 231–235, a Max Release table that shuts off
releases below elevation 198, and two slots that matter to everything
downstream and east: Diversion Min Elevation, the floor below which the
transbasin diversion is cut off, and the Pool Elevation Limits table, which
stores adjustable maximum and minimum operating elevations.

Below Cedar, the Cedar to Dogwood reach (impulse-response routing) feeds
**Dogwood**, a level power reservoir (elevations roughly 162–174) that also
diverts directly to the Dogwood Irrigation water user. Dogwood's outflow passes
through the Reach for Diversion, where **Eastern Irrigation** diverts (its
return flow re-enters at Elm), and continues to **Elm**, the bottom reservoir of
the cascade (elevations roughly 147–149). Dogwood and Elm are also
head-coupled: Dogwood's Tailwater Base Value is linked to Elm's Pool Elevation.
Elm carries a Pool Elevation Target scalar and gated bypass tables in addition
to the standard power-reservoir slots.

### East basin: Hickory and the irrigation complex

Inflow to the east basin arrives at the **Gage Above Hickory** stream gage,
joined by the Transbasin Diversion's outflow, and enters **Hickory**, a storage
reservoir (elevations roughly 129–139) with a modest Max Release of 548 and a
scalar Pool Elevation Min to Supplement Irrigation that defines the storage
pool it may draw on for irrigation support.

Hickory's releases enter the **Juniper Diversion** reach, which serves the
Juniper Irrigation aggregate site (four lumped water-user districts) and loses
water to head-based seepage into Linden Groundwater. The reach's outflow passes
the **Interstate Flow Requirement** gage — which carries a Min Flow series and
a Min Flow Violation series — and continues into the Mulberry Seepage reach.

A second withdrawal, the **Hickory Diversion** object, pulls water from Hickory
into the Linden Canal, serving the two Linden Irrigation districts, then drops
through **Mulberry Canal Power**, a small inline power plant (up to 60 units of
power at a flow of 200), into the Mulberry Canal serving Mulberry Irrigation.
Mulberry Irrigation is a sequential-structure aggregate site whose three
districts practice conjunctive use: when surface deliveries fall short, they
pump supplemental groundwater from **Mulberry Groundwater**, with the allowable
pumping set by each district's Max Request Table as a function of groundwater
elevation. Canal seepage and irrigation return flows recharge the linked
**Linden Groundwater** and **Mulberry Groundwater** objects, which exchange
water laterally as a head-based groundwater grid. Surface flows reconverge at
the Mulberry Canal Return confluence.

### System Data

A data object, **System Data**, collects the model's summary measures. Series
slots accumulate Energy, Energy Cumulative, Spill Volume, and Depletion
Shortage each timestep; scalar slots hold run totals, including Total Energy,
per-district irrigation totals rolled up into Total West Basin Irrigation
(Dogwood plus Eastern) and Total East Basin Irrigation (Juniper plus Mulberry),
Total Spill Volume, Total Transbasin Diversion, and Total Depletion Shortage.
Three of the scalars — Total Energy Neg, Total W Basin Irrig Neg, and Total E
Basin Irrig Neg — store negated copies of the corresponding totals.

## Data exchange (DMIs)

The model is wired for an external, DMI-driven workflow. The input DMIs
(`From Borg-RiverWare`, `ArborInputDMI`, `ArborMRMInputs`) write decision-type
scalar slots before a run — the operating thresholds such as
`Cedar.Diversion Min Elevation`, `Dogwood.Diversion Min Elevation`,
`Hickory.Pool Elevation Min to Supplement Irrigation`, and Cedar's Pool
Elevation Limits. The output DMIs (`To Borg-RiverWare Single Run`,
`To Borg-RiverWare MRM Run`, `ArborOutputToText`, `ArborOutputs`) export the
System Data summary slots after the run. Any external tool — an optimizer, a
sampler, a script — can therefore set the thresholds, run the model, and read
back the system-wide consequences.

## Ruleset

The operating policy is the embedded ruleset `Arbor Basin Rules (from MRM
run)`. Execution proceeds group by group: Aspen first, then down the west-basin
cascade, across the transbasin link, through the east basin, and finishes with
post-processing.

**Aspen Rules** open the run. The first rule to fire, `Cause Sporadic Error`,
is a deliberate tripwire for batch workflows: it stops the run with the message
"Invalid Cedar Diversion Min Elevation" whenever `Cedar.Diversion Min
Elevation` is below 220 (the slot's externally set range is 205–242, so some
inputs abort by design — useful for testing how a driving workflow handles
failed runs). `Aspen Operate to Guide Curve` then sets Aspen.Outflow to draw
the pool toward the Elevation Guide Curve, capped by the physical maximum
outflow and floored at zero. Three safeguard rules follow — `Aspen Outflow
Min`, `Aspen Elevation Min`, `Aspen Elevation Max` — overriding the operation
when a floor or ceiling is crossed; because they fire later, the elevation
limits take final priority.

**Birch Rules** repeat the pattern with `Birch Outflow Target` as the base
operation, followed by the same three safeguards.

**Transbasin Diversion** contains one rule, `Cedar Available for Diversion`:
if Cedar's pool sat above Diversion Min Elevation at the previous timestep, the
water above that threshold (plus inflow, less the required minimum outflow) is
offered to the Transbasin Diversion; otherwise nothing is.

**Cedar Rules** operate the reservoir to its monthly Guide Curve with `Cedar
End of Month Guide Curve` — on the last day of each month the rule solves
directly for the guide-curve storage, and on other days it uses
`TargetHWGivenInflow` with forecast inflows to walk the pool toward the
end-of-month target. `Cedar Outflow Min`, `Cedar Elevation Min`, and `Cedar
Elevation Max` then apply the floors and ceilings, with the elevation rules
solving to the "New" column of the Pool Elevation Limits table.

**Dogwood Irrigation** computes `Dogwood Available for Diversion` the same way
Cedar's transbasin availability is computed, gated by Dogwood's own Diversion
Min Elevation. **Dogwood Rules** and **Elm Rules** then apply the safeguard
pattern to their reservoirs; Elm adds `Elm Pool Elevation Target` as its base
operation and `Elm Required Spill` for flood releases.

**Hickory Rules** hold the east basin's water-rights logic, and their firing
order tells the policy story. `Interstate Flow Requirement` first reserves the
interstate minimum by setting the Juniper Diversion's Minimum Diversion Bypass.
`Hickory Pass Natural Flows for Juniper and Interstate` sets Hickory's outflow
to pass the natural flow arriving above the reservoir, up to what Juniper's
requests and the interstate minimum require. If Juniper is still short and the
pool stands above Pool Elevation Min to Supplement Irrigation, `Supplement
Juniper from Hickory Storage` releases stored water to cover the shortfall.
If Juniper remains short even then, `Reduce Hickory Diversion` cuts the
Hickory Diversion (the canal supply to Linden and Mulberry) in favor of
Juniper's senior rights, issuing a warning, and `Hickory Elevation Min Reduce
Diversion` makes a further cut when the pool is below its minimum. `Hickory
Elevation Min` and `Hickory Elevation Max` close the group.

**Post-processing** fires last, writing the summary slots: the Interstate Flow
Requirement Violation series (any shortfall below the minimum flow, with a
small tolerance), System Data's Energy, Depletion Shortage, and Spill Volume
totals summed across the relevant object sets, and each power object's Energy
Cumulative series.

A utility group supplies the three shared outflow functions the safeguard
rules call (`OutflowForMinOutflowRules`, `OutflowForMinElevationRules`,
`OutflowForMaxElevationRules`).

Separately from the operating set, the **Initialization Rules Set** prepares
inputs before each run: it converts the monthly diversion schedules on the
Transbasin Diversion and Hickory Diversion objects into daily diversion
requests, and — in multiple-run contexts — ` Trace Diversion Schedule
Variation` reduces the transbasin request by ten percent on trace 1. The model
also stores an Iterative MRM Rules Set and an Expression Slot Functions Set.

## How it connects

The model's decision levers are the four DMI-written thresholds: Cedar's
Diversion Min Elevation and Pool Elevation Limits control how much water leaves
the west basin, Dogwood's Diversion Min Elevation controls west-basin
irrigation access, and Hickory's Pool Elevation Min to Supplement Irrigation
controls how deeply east-basin storage is drawn down for irrigation. The
consequences flow to the System Data totals: energy from the four-plant west
cascade plus Mulberry Canal Power, irrigation deliveries split into west- and
east-basin totals, spill volume, depletion shortage, and the transbasin
diversion itself. Raising Cedar's diversion floor keeps water in the west for
power and irrigation there; lowering it feeds the east basin's users and the
interstate obligation. The ruleset arbitrates the rest.
