# Demo transcript — live set → run → read loop

A real sequence against `examples/ArborBasin/ArborBasin.mdl` with RiverWare
9.7 on Windows (2026-07-28), lightly edited for readability. The agent's goal:
measure how Cedar's transbasin diversion floor trades west-basin water against
east-basin supply.

---

**Agent →** `set_slots`

```json
{"assignments": {"Cedar.Diversion Min Elevation": 226.1}}
```

**Server →** `staged 1 slot file(s) in .../mcp_runs`

**Agent →** `run_model`

**Server →** `exit code 0` *(plus batch log tail)*

**Agent →** `read_slots`

**Server →**

```
System Data.Total Energy Neg: -12508319.96 MWH
System Data.Total Transbasin Diversion: 3096.0 MCM
System Data.Total Spill Volume: 2495.27 MCM
System Data.Total Depletion Shortage: 1286.1 MCM
```

**Agent →** `set_slots`

```json
{"assignments": {"Cedar.Diversion Min Elevation": 238.0}}
```

**Agent →** `run_model`

**Server →** `exit code 0`

**Agent →** `read_slots`

**Server →**

```
System Data.Total Energy Neg: -12601693.99 MWH
System Data.Total Transbasin Diversion: 1838.1 MCM
System Data.Total Spill Volume: 2701.68 MCM
System Data.Total Depletion Shortage: 2318.78 MCM
```

---

## What the numbers say

Raising Cedar's Diversion Min Elevation from 226.1 to 238.0 — keeping nearly
twelve more meters of pool off-limits to the transbasin diversion — cut the
Total Transbasin Diversion from 3096 to 1838 MCM. The east basin paid for it:
Total Depletion Shortage nearly doubled (1286 → 2319 MCM). The west basin
kept the water instead: total energy rose (the negated slot fell from
−12,508,320 to −12,601,694 MWH, i.e. about 93 GWh more generation) and spill
increased (2495 → 2702 MCM).

That is the whole point of the loop: an agent can pose a policy question,
turn it into slot values, run the licensed model, and read a quantified
trade-off back — in four tool calls per experiment.

## Caveats

- Runs A and B each completed in well under a minute for this one-year daily
  model; larger models take longer and `run_model` waits synchronously.
- `Cedar.Diversion Min Elevation` values below 220 trigger the model's own
  `Cause Sporadic Error` rule, which aborts the run by design — a useful
  reminder that the model, not the server, owns run validity.
