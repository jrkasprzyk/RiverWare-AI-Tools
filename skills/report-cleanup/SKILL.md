---
name: report-cleanup
description: Rewrite a rambling bug report, issue, or ticket into a clear structure — Summary, Repro, Hypothesis, Asks — without silently promoting the user's own guess into a stated fact. Recognizes RiverWare vocabulary (Object.Slot references, RPL rule names, .mdl/.rls, DMI, Rule Log, Diagnostics Output, MRM, accounting method, agenda order) to tell an observed symptom apart from a suspected cause. Use when asked to clean up, rewrite, restructure, or make readable a bug report, issue write-up, or ticket.
---

# Report cleanup

A rambling bug report usually has three things woven into one paragraph: what
happened, why the writer thinks it happened, and what they want done about it.
The reasoning and the observation read the same on the page, so a rewrite that
just tidies the prose can accidentally promote a guess to a fact. This skill
keeps the two apart.

## The four-part structure

Rewrite every report into this order:

1. **Summary** — the error and where it was thrown or observed, in one or two
   sentences. The `RPL Error`, the `Solve Failed` message, the wrong number in
   a slot, the run that would not finish. Fact only, quoted where the original
   text is exact.
2. **Repro context** — the steps or state that produced it: which model,
   which ruleset, which run type, which timestep or date range, what changed
   right before the symptom appeared. Still fact — things the writer directly
   observed or did.
3. **Hypothesis** — the writer's own explanation for *why* it happened,
   carried over from the original text but **relabeled as a hypothesis, not a
   fact**. If the original prose states the cause flatly ("the rule doesn't
   re-read max flow on resume"), rewrite it as "hypothesis: ... (needs a
   ruleset check to confirm)." Never delete this reasoning — it is usually the
   most valuable part of the report — but never let it stand unmarked next to
   the observed facts either.
4. **Asks** — numbered, one item per distinct request. A rambling report often
   blends two or three separable asks into one narrative (a repro fix, a
   feature request, and a documentation gap). Split them into separate numbered
   items even if the original text never separated them.

## Reading RiverWare vocabulary

The domain vocabulary is what makes a RiverWare report readable to a modeler.
Use it to sort content correctly, and use it to keep the rewrite grounded in
terms the reader already knows.

**Usually an observed fact (Summary / Repro):**

- An exact error string: `RPL Error`, `Solve Failed`, `Series has missing
  values`, `Infeasible`, `Could not converge`, a DMI connection error
- A named object, slot, or `Object.Slot` reference (`Cedar.Pool Elevation`)
- A named rule, policy group, or agenda position
- A file identity: `.mdl`, `.rls`, the run type (Rule Based Simulation,
  Optimization, MRM child run), a workspace or plot name
- A timestep, run start/end date, or a specific run configuration

**Usually the writer's inference (Hypothesis — relabel, don't delete):**

- Any claim about *why* a rule fired or did not fire, when the writer read the
  RPL rather than watched the Rule Log
- Any claim about accounting-method behavior, DMI script behavior, or solver
  internals that the writer reasoned out rather than observed in a log
- "I think," "probably," "must be," "seems like" — even when the surrounding
  sentence drops the hedge, the claim underneath is still a guess

**Where a hypothesis gets checked**, so the Ask can point at it precisely:
the Rule Log or Diagnostics Output for a firing-order claim, the ruleset's RPL
for a logic claim, the DMI script or link configuration for a data claim, the
accounting method definition for an accounting claim. Naming the right place
to check is more useful to a modeler than restating the guess.

## Splitting tangled sub-issues

Watch for a second, unrelated observation riding along inside the same
paragraph as the main one — a code-reading aside, a "by the way, this other
slot looks wrong too," a documentation gap noticed in passing. Give each one
its own Summary/Repro/Hypothesis, or at minimum its own numbered Ask, instead
of blending it into the main narrative. A rewrite that keeps two issues tangled
together has not actually made the report more readable, even if the prose is
cleaner.

## Do a cleanup pass

1. **Read the whole report first**, not sentence by sentence. Identify every
   named model, object, slot, rule, run type, and file before sorting anything.
2. **Sort each sentence** into Summary, Repro, Hypothesis, or a separable Ask.
   A sentence that mixes an observation and a guess gets split into two.
3. **Relabel, don't rewrite, the hypothesis.** Keep the writer's own reasoning
   in their own terms; add the "(hypothesis — needs verification)" framing
   rather than replacing their words.
4. **Check what you can.** If the referenced `.mdl` or `.rls` is available,
   a quick grep for the named rule or slot can confirm or weaken the
   hypothesis before the rewrite ships — say what you found, but do not treat
   a quick check as the same thing as the writer testing it themselves.
5. **Number the Asks**, one distinct request per item.
6. **Show the rewrite before finalizing** if it will be posted somewhere
   (an issue tracker, an email) — the writer confirms their intent survived
   the restructuring.

## Example

Before — one paragraph, three things woven together:

> Running ArborBasin with the new spring ruleset and getting RPL Error at
> timestep 4 on the Cedar Spring Drawdown rule, something about SolveOutflow.
> I looked at the rule and I think it's because GetMaxOutflowGivenInflow
> doesn't get re-evaluated after the rule above it changes Inflow, so it's
> using a stale value from the wrong policy group — same thing might be
> happening in the Saratoga ruleset too since it copies this rule. Also
> noticed the guide curve plot is unlabeled on the Y axis, minor but annoying.

After:

> **Summary.** `RPL Error` at timestep 4, thrown from `Cedar Spring Drawdown`,
> inside the `SolveOutflow` call.
>
> **Repro context.** ArborBasin model, new spring ruleset, timestep 4.
>
> **Hypothesis (needs a ruleset check to confirm).** `GetMaxOutflowGivenInflow`
> may be using a stale `Inflow` value if a rule earlier in the agenda changes
> `Inflow` and this rule does not re-read it before calling
> `SolveOutflow`. Check the agenda order and whether `Cedar Spring Drawdown`
> reads `Inflow` before or after the upstream rule fires.
>
> **Asks.**
> 1. Confirm the stale-`Inflow` hypothesis against the actual agenda order and
>    fix `Cedar Spring Drawdown` if confirmed.
> 2. Check whether the Saratoga ruleset's copy of this rule has the same
>    ordering issue.
> 3. Label the Y axis on the guide curve plot.

Three things stayed three things — a confirmed error, a hypothesis pointed at
exactly where to check it, and two separate asks that would otherwise have
been buried in one paragraph.
