# comment-cleanup — before and after

Produced with [comment-cleanup](../../skills/comment-cleanup/SKILL.md). The
input is a constructed example, not a file from this repository: a short
post-processing script of the kind an AI assistant writes over a few sessions
to summarize RiverWare output. The comment patterns are the ones the skill
targets — development history, restated code, and undocumented tuning
constants.

## Before — 14 comments, 1 real fact, and the real fact is missing

```python
# Updated to read the exported CSV instead of the old fixed-width dump
# Now handles the shortage columns too, per the review
import csv
from statistics import mean

SMOOTH = 7
THRESH = 0.05
MIN_EVENTS = 3
GAP = 2

def shortage_events(path, smooth=SMOOTH, thresh=THRESH, gap=GAP):
    # Open the file
    with open(path, newline="") as fh:
        # Read the rows
        rows = list(csv.DictReader(fh))
    # Get the shortage fractions
    frac = [float(r["Shortage Fraction"]) for r in rows]
    # Smooth the series - changed to a rolling mean, cleaner than the old way
    sm = [mean(frac[max(0, i - smooth + 1): i + 1]) for i in range(len(frac))]
    events = []
    # Loop over the smoothed values
    for i, v in enumerate(sm):
        # Check if it's over the threshold
        if v > thresh:
            # Extend the last event if we're still within the gap
            if events and i - events[-1][1] <= gap:
                events[-1][1] = i
            else:
                # Otherwise start a new event
                events.append([i, i])
    # Return the result
    return events
```

## After — the history is gone, the constants are documented

```python
import csv
from statistics import mean

# Rolling window for the shortage-fraction series, before event detection.
#   range:   1 to 30 (above 30 the smoothed series spans more than one
#            irrigation demand cycle and hides a real short event)
#   default: 7
#   units:   timesteps (days, at this model's 1 DAY timestep)
# A large window removes single-timestep noise from the export. It also
# lowers the peak shortage fraction and delays the start of each event. A
# value of 1 stops the smoothing.
SMOOTH = 7

# Shortage fraction above which a timestep counts as a shortage.
#   range:   0.0 to 1.0 (the slot is a fraction, so these are the physical
#            bounds; not tested below 0.01, where export round-off dominates)
#   default: 0.05
#   units:   unitless fraction of the requested diversion
# A low threshold reports more, shorter events. A high threshold reports only
# deep shortages and merges the shoulders into the gaps between them.
THRESH = 0.05

# Number of below-threshold timesteps allowed inside one event.
#   range:   0 to 14 (0 splits an event at every recovery timestep; above 14
#            two separate seasonal shortages merge into one event)
#   default: 2
#   units:   timesteps
# A large gap reports fewer, longer events. A small gap fragments one
# shortage into several.
GAP = 2

def shortage_events(path, smooth=SMOOTH, thresh=THRESH, gap=GAP):
    """Find shortage events in an exported Shortage Fraction series.

    Returns a list of [start_index, end_index] pairs into the exported rows.
    """
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    frac = [float(r["Shortage Fraction"]) for r in rows]
    sm = [mean(frac[max(0, i - smooth + 1): i + 1]) for i in range(len(frac))]
    events = []
    for i, v in enumerate(sm):
        if v > thresh:
            if events and i - events[-1][1] <= gap:
                events[-1][1] = i
            else:
                events.append([i, i])
    return events
```

## The report

The report is half the deliverable. Two of the findings below are defects, not
style:

```
Comments
  deleted    11  restated code ("Open the file", "Loop over the smoothed
                 values") or development history ("Updated to...", "Now
                 handles...", "cleaner than the old way", "per the review")
  added       3  full tuning-parameter blocks
  added       1  docstring, carrying the return-value contract that no
                 comment stated

Tuning parameters
  SMOOTH      real     documented above
  THRESH      real     documented above
  GAP         real     documented above
  MIN_EVENTS  fossil   defined at module level, read by no code and no test
                       -> remove it, or wire it up if a minimum event count
                       was intended

Defects found, not fixed in this pass
  1. The rolling window is trailing, not centered: sm[i] averages the 7 values
     ending at i. Event starts are therefore reported late by up to 6
     timesteps. The deleted comment ("Smooth the series") never said which.
  2. The gap test compares against the previous event's end index, so a gap of
     2 merges events separated by 2 *below-threshold* timesteps only when no
     above-threshold timestep intervened. This matches the docstring now, but
     confirm it is the intended definition of an event.
```

Per the skill, the pass edits comments only. The trailing-window behavior and
the unused `MIN_EVENTS` are reported for the author to decide on — a comment
pass that also changes logic cannot be reviewed in one read of the diff.

---

## What this demonstrates

| Tenet | Where it shows up |
|---|---|
| 1 — describe the code, not its history | "Updated to read...", "Now handles...", "per the review", "cleaner than the old way" all deleted |
| 2 — write few comments | 11 restated-code comments deleted; the interface moved into a docstring |
| 3 — document every tuning parameter | Range, default, units, and trade-off for `SMOOTH`, `THRESH`, `GAP`; `MIN_EVENTS` reported as fossil |
| 4 — Simplified Technical English | Short sentences, active voice, no modals, no -ing verbs, units named exactly |
| Report the defects, don't fix them silently | Trailing-window and gap-semantics findings raised, code left alone |
