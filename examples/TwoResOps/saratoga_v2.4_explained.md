# Saratoga — model narrative

*A narrative explanation of `saratoga_v2.4.mdl` (RiverWare 9.7), produced with
the [explain-riverware-model](../../skills/explain-riverware-model/SKILL.md)
skill and human-edited. Regenerate the underlying structural digest with:*

```bash
python skills/explain-riverware-model/explain.py examples/TwoResOps/saratoga_v2.4.mdl
```

## Overview

Saratoga is a compact two-reservoir operations model: 12 simulation objects on
a single river stem, run at a one-day timestep over six years (1 January 2007
through 31 December 2012). Its operating policy is an embedded ruleset,
`RPL Set`, and the model's purpose is legible in its design: two reservoirs
with distinct jobs, four downstream interests competing for the same water
(irrigation, a fishery, a flood-prone city, and an ecological flow target),
and a data object named Objectives that scores how well a given operating
policy balances them.

## Physical network

Water enters from two gaged tributaries. The **Sara** gage feeds **Cora**, the
upstream storage reservoir (pool elevations roughly 2124–2174, with a Dead
Pool at the bottom of that range and a Max Release table that permits no
release below elevation 2140). Cora's outflow passes down the **Pescado
Fishery** reach, which carries a scalar Min Fish Flow, to the Saratoga
Confluence, where the **Toga** gage's tributary joins.

The combined flow enters **Roberto**, the downstream reservoir (elevations
roughly 1852–1916, with a finely resolved elevation-volume table and a 46-row
Max Release table). Roberto releases into the **Winifred Valley Reach**, where
**Winifred Valley Farms** — the model's single irrigation water user, with a
monthly Periodic Diversion Request peaking in summer — diverts what is
available. The reach continues to **Lafayette City**, a control point with a
scalar Preferred Flow Limit and a Flood Damage Curve that converts flows above
roughly 1000 into dollar damages. Below the city, the farms' return flow
rejoins at the Sara below Lafayette confluence, and everything exits past the
**Wildlife Sanctuary** gage, which carries a monthly Eco Flow Pattern — an
ecological flow floor shaped to follow the natural hydrograph — plus Eco
Deficit and Eco Provided series that the post-processing rule fills.

Cora also carries the policy's rationing machinery: a Shortage Table mapping
pool elevation to an irrigation Shortage Fraction (no shortage above elevation
2173, 15 percent at 2154, 18 percent at 2144), with companion scalars (Level 1
PE, Level 2 PE, Flood Control) marking the trigger elevations.

The **Objectives** data object holds eight scalar performance measures:
Roberto Flood Reliability, Cora Supply Reliability, Irrigation Volumetric
Reliability, Eco Volumetric Reliability, Flood Damage, Fraction of Days Above
1000 cms at City, Cora Minimum Level, and Cora Average Storage.

## Data exchange (DMIs)

Two exec DMIs wire the model for an external workflow: `to_rw` (input) writes
the operating thresholds before a run, and `from_rw` (output) exports the
Objectives slots after it. Any external tool can therefore propose a policy —
threshold elevations, flow limits, shortage levels — run the model, and read
back the eight performance measures.

## Ruleset

The operating policy lives in two policy groups plus a post-processing group.
Execution runs Cora first, then Roberto, then post-processing; within each
group the rules below fire in the order listed, and each later rule can
override the release the earlier ones set — so each group reads as an
escalation from routine operation to hard safety limits.

**Cora Rules** ration the upstream supply:

1. `Find Shortage Level` looks up the irrigation Shortage Fraction from the
   Shortage Table using yesterday's pool elevation.
2. `Irrigation` sets Cora's release to serve Winifred Valley Farms' request,
   cut back by the Shortage Fraction — but only if Roberto's pool stood above
   its Delivery Threshold yesterday; if not, the irrigation release is zero,
   because Roberto cannot pass the water through. (Irrigation water is sourced
   from Cora alone; Roberto is the conveyance.)
3. `Minimum Fish Flow` raises the release to the Pescado Fishery's Min Fish
   Flow if the irrigation release fell short of it.
4. `Supplement for Downstream Eco Flow` adds water for the Wildlife
   Sanctuary's ecological target when the deficit there exceeds 1 cms, but
   only down to the Level 2 Restrictions elevation — conservation storage is
   not emptied for the ecosystem.
5. `Flood Control` draws the pool down to the Flood Control elevation during
   flood season.
6. `Prevent Overtopping` fires last and overrides everything, releasing
   whatever is needed to hold the pool at Pool Elevation Max.

**Roberto Rules** manage the pass-through and the city:

1. `Pass-Through Flow for Winifred Farms` releases what the farms have been
   allocated upstream.
2. `Downstream Ecological Flow` adds release when the Wildlife Sanctuary is
   below its Eco Flow Pattern.
3. `Flood Control` draws down to the Flood Control Level during flood season.
4. `Avoid City Flooding` *cuts* the release when Lafayette City's inflow
   exceeds its Preferred Flow Limit — the one rule in the model that reduces
   flow, trading stored flood risk at Roberto against damages in the city.
5. `Prevent Overtopping` again fires last and wins.

**Post Processing** contains one rule, `Wildlife Sanctuary Calculations`,
which records the daily Eco Deficit and Eco Provided series — crediting flow
only up to the requirement, so exceeding the ecological target scores no
better than meeting it.

The ruleset's utility groups are half its character: alongside generic release
helpers (`ReleaseToElevation`, `GetPossibleRelease`,
`ReleaseFlowrateLimitedToElevation`) and problem-specific helpers
(`FloodSeason`, `GetShortageFromTable`, `WinifredFarmsRequestWithShortage`),
a **Performance Metrics** group provides a small library of scoring functions
— volumetric and time-based reliability, resilience, vulnerability, and
shortage-index measures — from which the Objectives slots are computed. A
separate initialization rule, `Copy Cora Shortage Table into Scalars`,
prepares the shortage thresholds before the run.

## How it connects

The model is a policy-evaluation loop in miniature. The levers are the
threshold slots the input DMI writes: Cora's Flood Control and shortage-level
elevations, Roberto's Delivery Threshold and Flood Control Level, the Pescado
Fishery's Min Fish Flow, and Lafayette City's Preferred Flow Limit. The
ruleset turns those thresholds into daily releases; the Performance Metrics
functions condense six years of daily behavior into the eight Objectives
scalars; and the output DMI hands them back. Every downstream interest has a
measure watching it — flood reliability and damages for the city, volumetric
reliability for the farms and the sanctuary, storage statistics for Cora — so
the tensions between them (release for irrigation now, or hold flood space;
supplement the ecosystem, or protect conservation storage) are exactly what
the eight numbers trade off.
