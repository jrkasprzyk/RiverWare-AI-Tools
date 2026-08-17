# riverware-help — worked session (rule priorities)

Produced with [riverware-help](../../skills/riverware-help/SKILL.md) against
the [TwoResOps](../TwoResOps/) model. The help content below was fetched from
the live CADSWES help (CurrentVersion); the model facts come from the digest
driver and the embedded ruleset, not from reading the `.mdl` raw. The question
is constructed for the example.

---

**Question.** I added a rule at the bottom of the `Roberto Rules` group. The
Rule Log shows it firing and computing a release, but the final
`Roberto.Release` value came from `Flood Control` instead. Why does my rule's
value not stick?

---

**Answer.**

Your rule is working — it is being **overwritten on purpose**, and the
mechanism is rule priority. Per the CurrentVersion help:

- [Slot Priorities and Flags](https://www.riverware.org/HelpSystem/CurrentVersion/SolutionApproaches/Solutions_RulebasedSimulation.3.09.html)
  — "Slots that are set by rules have the priority of the rule that set
  them," and "Slots which are directly set by a rule are displayed with a
  special flag, the R flag." Priority 0 is user input: "These values may
  never be overwritten during a run."
- [Resetting Slot Values](https://www.riverware.org/HelpSystem/CurrentVersion/SolutionApproaches/Solutions_RulebasedSimulation.3.10.html)
  — a proposed R-flagged value overwrites an existing R-flagged value only at
  **higher or equal priority**. The page's example table: existing `6R`
  overwritten by proposed `4R` → successful; existing `4R` and proposed
  `6R` → unsuccessful. (Smaller number = higher priority; rule 1 is the
  highest-priority rule in the set.)

**In your model:** the ruleset uses `ASCENDING` agenda order, so the *bottom*
rule of the listing fires *first* and has the *lowest* priority. The
`Roberto Rules` listing, top to bottom, is:

1. `Prevent Overtopping`
2. `Avoid City Flooding`
3. `Flood Control`
4. `Downstream Ecological Flow`
5. `Pass-Through Flow for Winifred Farms`  ← fires first, lowest priority

A rule added *below* `Pass-Through Flow for Winifred Farms` fires before
everything else in the group and holds the lowest priority in it. Every other
rule — `Flood Control` included — fires later at higher priority, and by the
Resetting Slot Values table its write succeeds over yours. The Rule Log told
the truth: your rule fired and set the slot; the slot then carried a higher
priority value by the end of the timestep. The SCT shows which rule owns the
final value: the R-flagged value's priority number is the owning rule's
position.

**The fix is placement, not logic.** Move the rule *up* the listing past the
rules it should override. Each position up is one priority step stronger; put
it above `Flood Control` and it will overwrite flood-control releases too —
decide whether that is actually the policy you want.

If you want the rule drafted or re-placed concretely, that is the
[draft-riverware-rules](../../skills/draft-riverware-rules/SKILL.md) skill —
[this worked session](draft-riverware-rules_roberto-min-flow.md) walks exactly
that placement decision for this group.

---

## What this demonstrates

| Skill behavior | Where it shows up |
|---|---|
| "Why is my model doing Y" gets reasoning, not a lookup | The answer reconstructs the priority mechanics end to end |
| Cite the page, quote the semantics | Two URLs, exact sentences on R flags and the overwrite table |
| Model evidence beats general knowledge | The actual `Roberto Rules` listing and `ASCENDING` order come from the embedded ruleset |
| Hand off, don't drift | Ends by pointing at draft-riverware-rules instead of rewriting the rule mid-answer |
