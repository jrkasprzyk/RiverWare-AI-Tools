# Proposed annotations — saratoga_v2.4.mdl

**28 annotations proposed, of 162 available targets (17%).** Nothing already
described is touched. Produced by the `annotate-riverware-model` skill; this is
the review artifact the modeler approves before `annotate.py` writes anything.

Companion machine proposal: `saratoga_v2.4_annotations.json`.

| Surface | Proposed | Available | Already described |
|---|---|---|---|
| Model description | 0 | 0 | 1 |
| Object descriptions | 4 | 8 | 4 |
| Slot descriptions | 16 | 97 | 11 |
| RPL set / group / rule / function | 8 | 57 | 1 |
| Expression comments (`COMMENTED_BY`) | **0** | — *(see below)* | — |

---

## Object descriptions

1. **Pescado Fishery** — "Reach immediately below Cora. It carries no diversion;
   its role in the policy is to hold the Min Fish Flow threshold that Cora's
   releases must satisfy."
   *Rationale: a reader sees a bare Reach and has no way to know it exists only
   to carry a policy threshold.*

2. **Winifred Valley Reach** — "Reach between Roberto and Lafayette City. It uses
   Available Flow Based Diversion to serve Winifred Valley Farms, so the farms
   can only take what Roberto has already released past it."
   *Rationale: the diversion method is the whole reason the Roberto pass-through
   rule exists.*

3. **Lafayette City** — "Control point representing the downstream city. Its
   Preferred Flow Limit is the flood-damage decision variable, and its inflow
   drives the Flood Damage Curve."
   *Rationale: this object is where two optimization quantities meet; the type
   name `ControlPoint` says none of that.*

4. **Wildlife Sanctuary** — "Gage below the confluence where the ecological flow
   requirement is evaluated. Its Eco Flow Pattern is the monthly requirement;
   Eco Deficit and Eco Provided record how well the requirement was met."
   *Rationale: it is typed as a StreamGage but functions as the eco-flow
   compliance point.*

**Not proposed:** `Sara`, `Toga`, `Saratoga Confluence`, `Sara below Lafayette`
— routing plumbing with no policy role. Their names and types already say what
they are.

## Slot descriptions

Each of these passes the policy-meaning test: read by a rule, holds a threshold,
is a decision variable, or is a reported metric.

### Cora

5. **Cora.Pool Elevation Max** — "Maximum pool elevation. The Prevent Overtopping
   rule releases down to this level whenever the pool exceeds it."
6. **Cora.Flood Control** — "Flood-control pool elevation for Cora. The Flood
   Control rule draws the pool down to this level, but only during the flood
   season." *Rationale: the seasonal gate is invisible from the slot.*
7. **Cora.Dead Pool** — "Lowest usable pool elevation. At or below it the Shortage
   Table delivers nothing to the irrigators."
8. **Cora.Level 1 PE** — "Pool elevation at which Level 1 irrigation restrictions
   begin. Copied from the Shortage Table by an initialization rule so that rules
   and plots can reference it as a scalar."
   *Rationale: a reader finding two sources of truth for the same number needs
   to know which one is authoritative.*
9. **Cora.Level 2 PE** — as above, plus: "also the floor that the eco-flow
   supplement rule refuses to draw below."
10. **Cora.Shortage Fraction** — "Fraction of the irrigation request withheld this
    timestep, looked up from the Shortage Table using the previous timestep's
    pool elevation. Set by Find Shortage Level and consumed by the Irrigation
    rule." *Rationale: the one-timestep lag is a genuine trap.*

### Roberto

11. **Roberto.Pool Elevation Max** — "Maximum pool elevation. The Prevent
    Overtopping rule releases down to this level whenever the pool exceeds it."
12. **Roberto.Delivery Threshold** — "Pool elevation below which Roberto cannot
    pass Cora's releases downstream. When the previous timestep is below it, the
    Irrigation rule delivers nothing to Winifred Valley Farms."
13. **Roberto.Flood Control Level** — "Flood-control pool elevation for Roberto
    and a decision variable in the optimization. The Flood Control rule draws
    the pool down to this level during the flood season to leave room for a
    flood wave."

### Policy thresholds elsewhere

14. **Pescado Fishery.Min Fish Flow** — "Minimum instream flow required below
    Cora. The Minimum Fish Flow rule raises Cora's release to meet it whenever
    the release would otherwise fall short."
15. **Lafayette City.Preferred Flow Limit** — "Flow through the city above which
    flooding is considered to begin, and a decision variable in the
    optimization. Note that it is deliberately allowed to differ from where the
    Flood Damage Curve starts charging damage."
    *Rationale: this is the exact point the modeler worked out in the Flood
    Damage Curve note; it belongs on the slot too.*
16. **Wildlife Sanctuary.Eco Deficit** — "Shortfall of gaged flow against the Eco
    Flow Pattern requirement, computed each timestep by the Post Processing
    group." *Rationale: its complement, Eco Provided, is already described.*

### Performance metrics (`Objectives`)

17. **Objectives.Roberto Flood Reliability** — "Fraction of timesteps in which
    Roberto's pool elevation stays at least 2 m below its maximum, so the
    reservoir is credited only when it holds real freeboard."
    *Rationale: the 2 m offset lives only in the expression.*
18. **Objectives.Eco Volumetric Reliability** — "Volume of ecological flow
    provided divided by the volume requested by the Eco Flow Pattern, over the
    whole run."
19. **Objectives.Flood Damage** — "Total flood damage over the run, obtained by
    running Lafayette City's inflow through its Flood Damage Curve. Calibrate
    this metric by its spread across policies, not its absolute value."
20. **Objectives.Fraction of Days Above 1000 cms at City** — "Fraction of
    timesteps with city inflow above 1000 cms. This is a fixed reporting
    threshold and is independent of the Preferred Flow Limit decision variable."
    *Rationale: the name invites exactly the confusion this sentence prevents.*

**Not proposed:** `Objectives.Cora Minimum Level` and
`Objectives.Cora Average Storage` — the names are the definitions. Also the
~110 physics slots (`Inflow`, `Outflow`, `Storage`, `Previous Storage`, spill
capacity fractions, and so on), which carry no model-specific policy meaning.

## RPL descriptions

21. **`RPL Set`** (set) — "Operating policy for the Saratoga basin: keep both
    reservoirs below their maximum elevations, evacuate flood space in season,
    meet the fish and ecological flow requirements, and deliver irrigation water
    subject to a pool-elevation-based shortage."
    *Rationale: the set is named `RPL Set`, which tells a reader nothing.*
22. **`RPL Set/Post Processing`** (group) — "Bookkeeping that runs after the
    policy rules have set flows. It computes reporting quantities and sets no
    releases."
23. **`RPL Set/Post Processing/Wildlife Sanctuary Calculations`** — "Records how
    the ecological flow requirement fared this timestep. When flow fell short it
    stores the shortfall and the amount actually provided; when it did not, it
    stores the requirement itself, so exceeding the target earns no extra credit
    in the metrics." *Rationale: the else-branch behavior is genuinely
    surprising and the rule name gives no hint of it.*
24. **`RPL Set/Roberto Rules/Flood Control`** — "Draws Roberto down to its Flood
    Control Level, but only during the flood season defined by FloodSeason.
    Outside that window the rule sets nothing and the pool is free to fill."
25. **`RPL Set/Roberto Rules/Avoid City Flooding`** — "Cuts Roberto's release by
    exactly the amount by which the city's inflow exceeds its Preferred Flow
    Limit, subject to what the reservoir can physically hold back."
26. **`RPL Set/Roberto Rules/Pass-Through Flow for Winifred Farms`** —
    "Unconditionally sets Roberto's release to the water Cora already sent down
    for the farms, so the delivery passes through rather than being stored."
    *Rationale: it is the only rule in the group with no condition at all.*
27. **`RPL Set/Cora Rules/Flood Control`** — as for Roberto.
28. **`RPL Set/Problem Specific Functions/FloodSeason`** — "True between May 1
    and August 31. This is the window in which both reservoirs' Flood Control
    rules are allowed to draw the pools down."
    *Rationale: the season is a hard-coded date range that four rules depend on.*

**Not proposed:** the `Cora Rules` and `Roberto Rules` groups, the
`Generic Functions` and `Problem Specific Functions` utility groups, and rules
whose names are their behavior — `Prevent Overtopping` (×2),
`Minimum Fish Flow`, `Downstream Ecological Flow`, and the initialization rule
`Copy Cora Shortage Table into Scalars`. Also `GetPossibleRelease`,
`ReleaseToElevation`, `ReleaseFlowrateLimitedToElevation`, and
`WinifredFarmsRequestWithShortage`, which already carry thorough
`COMMENTED_BY` documentation in their bodies.

## Expression comments — none proposed

**Zero, deliberately.** Every numeric literal in this ruleset that would qualify
under the rubric is already explained:

- `Supplement for Downstream Eco Flow` — the `1.00000000 "cms"` deficit trigger
  sits directly beside the modeler's own `COMMENTED_BY` covering that logic.
- `Irrigation` — the `0.00000000 "cfs"` zero-delivery case is covered by the
  statement-level description already in the rule body.
- `GetShortageFromTable`, `GetPossibleRelease`,
  `ReleaseFlowrateLimitedToElevation`, `WinifredFarmsRequestWithShortage` —
  already commented.

Adding comments here would be duplication, so nothing is proposed. See
`examples/ArborBasin/ArborBasin_annotations.md` for the surface in use.

---

## Skipped — already described, left untouched (REQ-005)

- **Model description**
- **Objects:** `Cora`, `Roberto`, `Winifred Valley Farms`, `Objectives`
- **Slots (11):** `Cora.Elevation Volume Table`, `Cora.Max Release`,
  `Cora.Shortage Table`, `Lafayette City.Upstream Reservoirs`,
  `Lafayette City.Flood Damage Curve`, `Wildlife Sanctuary.Eco Flow Pattern`,
  `Wildlife Sanctuary.Eco Provided`,
  `Winifred Valley Farms.Water User Groups`,
  `Winifred Valley Farms.Periodic Diversion Request`,
  `Objectives.Cora Supply Reliability`,
  `Objectives.Irrigation Volumetric Reliability`
- **Rules:** `RPL Set/Cora Rules/Find Shortage Level`

Two observations for the modeler, offered rather than acted on:

- The description currently on the **`Winifred Valley Farms`** water user
  describes **Winifred Valley Reach** ("Winifred Valley Reach sits below Roberto
  and directly upstream of Lafayette City…"). It reads like it was entered on
  the wrong object. Proposal 2 adds a description to the Reach itself and leaves
  the Farms text exactly as written — moving it is the modeler's call.
- The **`Irrigation`** rule's own Description field is empty, but its body
  carries a long statement-level description. It is documented; the inventory
  simply cannot see that. No rule description is proposed for it.

---

## Before trusting this

Only RiverWare validates a `.mdl`. Load the annotated model in RiverWare and
confirm the descriptions appear where they should — the open-object dialog, the
slot dialog, and the RPL editor's description tab — before trusting it.
