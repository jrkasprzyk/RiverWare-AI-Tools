# report-cleanup — before and after

Produced with [report-cleanup](../../skills/report-cleanup/SKILL.md). The
input is a constructed bug report, written the way modelers actually write
them — one paragraph, observation and guesswork woven together. The model it
refers to is the real [TwoResOps](../TwoResOps/) model, so the hypothesis check
in step 4 below is a real check against the digest, not a made-up one.

## Before — one paragraph, four things in it

> Ran saratoga_v2.4 over 2007-2012 and Winifred Valley Farms gets basically
> nothing in July of most years, diversion sits at zero for weeks at a time
> even though Cora is nowhere near dead pool and the Shortage Table says the
> shortage fraction should only be 0.15 at that elevation. I'm pretty sure
> what's happening is Roberto is holding back because its Delivery Threshold
> is set too high, so the release never gets past it and the farms are starved
> — it's the same reason the Eco Deficit at Wildlife Sanctuary spikes in the
> same months I bet. Also the from_rw DMI wrote the July numbers out fine so
> it's not an export problem, and while I was in there the Flood Damage Curve
> on Lafayette City still has that unlabeled column header which makes the
> plot legend useless. Can someone look?

## After

> **Summary.** `Winifred Valley Farms` receives zero diversion for multi-week
> stretches in July across most years of the 2007–2012 run of
> `saratoga_v2.4.mdl`. `Cora` is above dead pool in those timesteps, and
> `Cora.Shortage Table` gives a shortage fraction of 0.15 at that pool
> elevation — so the observed zero is deeper than the shortage policy alone
> accounts for.
>
> **Repro context.** Model `saratoga_v2.4.mdl`, Rule Based Simulation,
> run 01-01-2007 to 12-31-2012, 1 DAY timestep. Symptom appears in July of
> most years. `from_rw` (output DMI) exported the July values correctly, so
> the zeros are in the model results, not an export artifact.
>
> **Hypothesis (needs a Rule Log check to confirm).** `Roberto.Delivery
> Threshold` may be set high enough that Roberto's pool elevation sits below
> it during July, blocking the pass-through release that Cora made for the
> farms. Where to check: the Rule Log for the timesteps with zero diversion —
> whether the delivery rule fired and what it evaluated `Delivery Threshold`
> against — and `Winifred Valley Reach.Available For Diversion`, which shows
> whether water reached the diversion point at all.
>
> **Related, same hypothesis, listed separately.** The reporter also expects
> `Wildlife Sanctuary.Eco Deficit` to spike in the same months for the same
> reason. This is a second inference, not a second observation — the eco
> deficit spike itself was not stated as confirmed. It is worth checking
> together with the main hypothesis, because a common cause would show up as
> the two series moving in the same timesteps.
>
> **Separate issue.** `Lafayette City.Flood Damage Curve` has an unlabeled
> column header, which leaves the plot legend blank. Unrelated to the
> diversion symptom.
>
> **Asks.**
> 1. Confirm or reject the `Roberto.Delivery Threshold` hypothesis against
>    the Rule Log for a July timestep with zero diversion.
> 2. If confirmed, decide whether `Delivery Threshold` is miscalibrated or
>    whether the delivery rule should release below the threshold.
> 3. Check whether `Wildlife Sanctuary.Eco Deficit` spikes in the same
>    timesteps, to test the common-cause theory.
> 4. Label the `Flood Damage Curve` column header on `Lafayette City`.

## The check that ran before this shipped

Step 4 of the skill says to check what you can against the model. From the
digest (`python skills/explain-riverware-model/explain.py
examples/TwoResOps/saratoga_v2.4.mdl`):

- `Roberto` does have a `Delivery Threshold` scalar slot, and its description
  states that releases to the irrigators cannot happen while pool elevation is
  below it. **The hypothesis is at least structurally possible** — the
  mechanism the reporter describes exists in the model.
- `Winifred Valley Reach` uses `Diversion from Reach = Available Flow Based
  Diversion`, so the farms can only take flow that already passed the reach.
  A second, independent mechanism can produce the same zero, so confirming the
  threshold hypothesis still requires the Rule Log.
- `Lafayette City.Flood Damage Curve` does have empty column names in the
  digest, so ask 4 is confirmed as an observation, not a hypothesis.

Structural possibility is not confirmation. The rewrite says "needs a Rule Log
check" even though the model check went the reporter's way.

---

## What this demonstrates

| Skill behavior | Where it shows up |
|---|---|
| Fact and guess stay separate | Zero diversion and the 0.15 table value are Summary; the `Delivery Threshold` explanation is labeled a hypothesis |
| Never delete the reasoning | The reporter's theory survives verbatim in intent — only its status changes |
| Name where to check it | Rule Log timestep, plus `Available For Diversion` as the discriminating slot |
| Split tangled sub-issues | The eco-deficit inference and the column-header defect each get their own block |
| One ask per number | Four asks that the original paragraph buried in one "can someone look?" |
| Check what you can | The digest confirmed the mechanism exists and surfaced a competing one |
