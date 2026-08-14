# riverware-help — worked session

Produced with [riverware-help](../../skills/riverware-help/SKILL.md) against
the [TwoResOps](../TwoResOps/) model. The help content below was fetched from
the live CADSWES help; the model facts come from the digest driver, not from
reading the `.mdl`.

---

**Question.** In a rule I want to convert Cora's pool elevation to a storage
volume. Which RPL function does that, and what does it do when the elevation
falls between two rows of the table?

---

**Answer.**

`ElevationToStorage` — per the
[RPL predefined functions reference](https://www.riverware.org/HelpSystem/CurrentVersion/RPL/RPLPredefinedFunctions.6.3.html)
(CurrentVersion help):

```
ElevationToStorage
  Type:      NUMERIC
  Arguments: OBJECT (reservoir), NUMERIC (pool elevation)
```

It reads the **Pool Elevation column of the Elevation Volume Table** on the
object you pass. Between rows it does "linear interpolation between the two
nearest bounding elevations and their corresponding storage values."

Three documented error cases, all of which abort the run rather than return a
bad number:

- the object argument is not a reservoir;
- the reservoir has the **Time Varying Elevation Volume** method selected;
- (for the companion `ElevationToArea`) the reservoir has no Elevation Area
  Table.

For a Slope Power Reservoir the help adds that "the calculation is based only
on level storage and does not include any wedge storage effects" — not
relevant here, Cora is a StorageReservoir.

**In your model** (from
`python skills/explain-riverware-model/explain.py examples/TwoResOps/saratoga_v2.4.mdl`):

- `Cora` is a `StorageReservoir` with a 50-row `Elevation Volume Table`
  (Pool Elevation, Storage), so `ElevationToStorage(%Cora, <elevation>)`
  resolves against that table.
- Cora's selected-method list does not include Time Varying Elevation Volume,
  so the second error case does not apply.
- Cora has **no Elevation Area Table** slot. If you reach for the sibling
  function `ElevationToArea` on this object, it aborts the run. Its surface
  area comes from the Surface Area interpolation methods
  (`Surface Area MTLE=Tangent`, `MTGE=Tangent`) instead.
- `Roberto`'s Elevation Volume Table has 20,800 rows — same function, same
  behavior, just a much finer curve.

Cora's table starts near elevation 2124.47 at the low end, so an elevation
below the first row is outside the tabulated range. The help text quoted above
describes interpolation *between* bounding rows only; it does not state an
extrapolation rule, so do not assume one — clamp the argument in the rule, or
confirm the out-of-range behavior in your RiverWare version before relying on
it.

If you want this turned into an actual rule expression against Cora's slots,
that is the [draft-riverware-rules](../../skills/draft-riverware-rules/SKILL.md)
skill — say the word and it can be drafted.

---

## What this demonstrates

| Skill behavior | Where it shows up |
|---|---|
| Fast path for RPL functions | `references/rpl-functions.md` gave the function's help page directly, with no section-index hop |
| Cite the page, quote the semantics | Signature and interpolation sentence quoted, one URL, not a bibliography |
| Model evidence beats general knowledge | The missing Elevation Area Table on Cora is a model fact, found in the digest |
| Do not synthesize what the help omits | Out-of-range behavior is flagged as uncovered rather than invented |
| Hand off, don't drift | Ends by offering `draft-riverware-rules` instead of silently writing a rule |
