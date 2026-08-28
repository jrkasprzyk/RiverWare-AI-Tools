---
name: comment-cleanup
description: Clean up the comments in AI-written code, so that the file describes what the code is and not how the assistant built it. Delete change-history comments ("added", "now handles", "in this version"). Delete comments that repeat the code. Give each tuning parameter a comment with its range, default, units, and effect. Write every comment in Simplified Technical English. Use this skill when the user asks to clean up comments, remove AI slop comments, fix comment noise, document tuning parameters or magic numbers, or make an AI-written file readable. Also apply these rules when you write or edit any comment in this repository, even if the user does not mention comments.
---

# Comment cleanup

Code written with an AI assistant collects one specific type of bad comment.
The assistant writes notes about its own work: `# Added retry logic`,
`# This now handles the empty case`. Each note is correct at the moment the
assistant writes it, and has no meaning one week later. The reader does not
know what "now" is, or what the code was before. At the same time, nobody
wrote down the facts that matter: why the tolerance is `1e-6`, or what
happens at a window of 90.

This skill removes the change history and the repetition. It also writes the
one type of comment that is worth many lines.

Two modes use the same four tenets:

- **Cleanup pass** — the user names files, a directory, or a diff. Do an
  audit, show a plan, then edit.
- **Standing style** — write every new comment in this repository to these
  tenets. The user does not have to ask.

## Tenet 1 — a comment describes the code, not its history

A person reads a comment while they look at the current file. The comment
must make sense to a reader who never saw an older version. Development
history belongs in commit messages and in the changelog, where it has a date
and an author. In a source file, the same history becomes wrong, and no test
finds the error.

Delete or rewrite each comment that:

- uses a past-tense development verb about the code — *added, removed,
  changed, updated, fixed, refactored, moved, renamed, replaced, switched*
- uses *now*, *no longer*, *previously*, *originally*, *used to*, *in this
  version*, *as of*, *going forward*
- refers to the development process — *per the review*, *as requested*,
  *per the user's feedback*, *see our discussion*, *TODO from last pass*
- announces a new approach — *simplified this*, *cleaner than the old way*,
  *note the new signature*
- repeats the assistant's reasoning — *let's iterate over the slots here*,
  *first we need to...*, *we do this because it is cleaner*

Past tense is correct when it describes the **program** and not the author.
`# the caller validated these rows` and `# rows arrive in sorted order from
the DMI` are statements about run time. Keep them.

Rewrites. Each one keeps the fact that the original tried to give:

| Instead of | Write |
| --- | --- |
| `# Added error handling for missing files` | delete — the `try` block is visible |
| `# Now returns None instead of raising` | delete, or put the return value in the docstring |
| `# Changed to a set for O(1) lookup` | `# set: this lookup runs one time per slot, ~10k times per run` |
| `# Fixed the off-by-one here` | `# the range includes the end date` |
| `# Updated to handle both .mdl and .rls` | delete — the branch on the suffix is visible |
| `# Refactored into a helper for clarity` | delete |
| `# This version uses the parser instead of regex` | delete |

The test: hide the code and read the comment alone. If the comment makes
sense only to a person who saw the older version, delete it.

## Tenet 2 — write few comments

Each comment is a second source of truth, and no test examines it. The
default is no comment. Give things good names, keep functions short, and let
the code show its own meaning. AI-written code usually has one comment for
each group of lines, and most of those comments say the next line again in
English. Readers learn to ignore all the comments, and this includes the
three comments that matter.

Delete a comment when it:

- repeats the code (`# loop over the objects` above `for obj in objects:`)
- labels an obvious block (`# imports`, `# main logic`, `# return the result`)
- is a banner of `#####` in a file that is short enough to read
- documents a parameter that the signature and the type hint document
- explains a language feature instead of this program

Keep a comment, and write one, when it gives a fact that the code does not:

- **why**, when you rejected the obvious approach for a real reason
- a constraint from outside the file: a file-format defect, a bug upstream,
  undocumented vendor behavior, a rounding rule from a regulation
- units, sign conventions, coordinate frames, and time bases (`# acre-feet,
  not cfs`, `# timestep-ending`)
- an invariant that a future editor breaks without a test failure
- a known trap: reentrancy, order of operations, float comparison, encoding
- a pointer to an external source: a specification section, an issue, a help
  page
- a tuning parameter — tenet 3 gives the full format

Never delete these: license and copyright headers, `TODO`, `FIXME` and
`HACK` markers, `ponytail:` markers, tool directives (`# noqa`,
`# type: ignore`, `# pragma: no cover`, `# pylint: disable`,
`@ts-expect-error`, `eslint-disable`), shebangs, encoding declarations, and
the docstrings or JSDoc on a public API. These have legal effect, they change
tool behavior, or they are the interface contract. Make a long docstring
shorter, but do not remove it.

## Tenet 3 — give each tuning parameter a complete comment

A tuning parameter is a constant that changes behavior, quality, or speed,
but does not change correctness. Thresholds, tolerances, window lengths,
weights, retry counts, timeouts, sample sizes, and cutoffs are tuning
parameters. One day, a person changes the value. That person has one
question: which values are safe, and what happens at each value. The comment
answers the question one time, or an afternoon of experiments answers it.

This is the one place where a long comment is correct. Five lines on a tuning
parameter cost very little.

State all of these:

1. **What it controls** — one line, in terms of program behavior
2. **Lower bound** and **upper bound**, and where each bound comes from
   (physics, numerics, the file format, or the tested range)
3. **Default** — the value that ships
4. **Units** — or the word `unitless` for a ratio, a count, or a factor
5. **Effect of a change** — what gets better and what gets worse, because
   almost every one of these values is a trade-off

```python
# Rolling window for the inflow series, before the peak detection step.
#   range:   1 to 90 (the upper bound is a convention: after one season, the
#            smoothed series no longer follows real hydrology)
#   default: 7
#   units:   days
# A large window decreases the effect of gage noise. It also delays the
# response to a real rise and decreases the peak value. A value of 1 stops
# the smoothing.
SMOOTHING_WINDOW_DAYS = 7
```

```typescript
/**
 * Convergence tolerance for the mass-balance solver.
 *   range:   1e-9 to 1e-3 (below 1e-9, float64 round-off on reservoir-scale
 *            volumes hides the result; above 1e-3, storage errors show in
 *            the reported output)
 *   default: 1e-6
 *   units:   acre-feet
 * A tight tolerance increases the number of iterations. With hysteretic
 * outlet curves, a tight tolerance also prevents convergence.
 */
const MASS_BALANCE_TOL = 1e-6;
```

Do not invent a bound. A false range is worse than no range, because the next
reader trusts it. If you do not know a limit, write what you know:
`upper bound: not tested above 50; the loop is O(n^2) in this value`. If one
side has no limit, write `no upper bound`. If you have no justification for
the value, report this to the user. Do not fill the gap with a number that
looks correct.

True constants are different. Unit conversions, physical constants, and
format magic numbers need units and a source (`# 43560 ft^2 per acre`). They
do not need a range, because nobody changes them.

### Too many parameters is also a finding

AI-written code collects parameters. Each threshold that the assistant was
unsure about became a module constant or a keyword argument with a default.
The result is a function with eleven knobs. Nine of them never move from
their default, and the reader does not know which two are important.

During the audit, put each tuning parameter in one of three groups:

- **Real** — a user or a test changes it. Give it the full comment.
- **Fossil** — no code and no test changes it, and no user has a reason to.
  Recommend that the user inlines the default value, or derives the value
  from a real parameter.
- **Coupled** — it has meaning only with another parameter (a low threshold
  and a high threshold, a window and its stride). Recommend one parameter
  plus a derivation, or document the group as one block.

Report these as recommendations, and give the evidence (`the default value at
3 call sites, absent from the tests`). To remove a parameter changes the API.
The user makes that decision. Do not make it inside a comment pass.

## Tenet 4 — write the comments in Simplified Technical English

Comments are read fast, and often by people who do not read English as a
first language. ASD-STE100 Simplified Technical English (STE) removes the
ambiguity from each sentence. Apply these rules to every comment and
docstring you write or rewrite:

- **One idea per sentence.** Maximum 20 words for an instruction, 25 words
  for an explanation.
- **Active voice.** Use the imperative for an instruction: `Set this to 7
  for daily data.`
- **No modal verbs**: *can, could, may, might, should, would*. Write the
  direct statement. Instead of `# this may fail on an empty file`, write
  `# this function fails on an empty file`.
- **No -ing form as a verb.** The -ing form is correct only inside a noun
  (`the opening`, `the smoothing window`). Instead of `# handling the empty
  case here`, write `# this branch handles the empty case`.
- **Keep the subject and the articles.** Instead of `# set to zero if
  unused`, write `# if the slot is unused, set the value to zero`.
- **Put the condition first**: `# if the file has no header, the parser
  stops.`
- **One word for one thing.** Do not alternate between "slot", "field", and
  "attribute" for the same object in one file.
- **Simple words.** Use *start*, not *initiate*. Use *use*, not *utilize*.
  Use *make sure*, not *ensure* or *verify*. Use *about* only to mean
  "concerned with".
- **American spelling.**

Code identifiers, API names, file formats, and domain terms are technical
nouns. Use them without a change: `parse_model`, `.mdl`, `acre-feet`, and
`float64` are all correct.

The STE dictionary is under copyright, and this skill does not contain it.
Apply the rules above and keep the sentences short. Do not claim full STE
compliance, because no tool verifies it and the writer approves the final
text. For a full compliance check, or for a ruling on one word, use the
`asd-ste100` skill or the free standard at asd-ste100.org.

## Do a cleanup pass

1. **Set the scope.** Ask for the files, or use the working diff. If the user
   says "this project", first list the candidate files and their comment
   counts. Get approval before you edit. A repository-wide comment rewrite is
   a large diff.
2. **Read the files.** Do not read the comment lines alone. Judge each
   comment against the code below it. Use `grep` to find candidates. Do not
   delete on a `grep` hit alone.
3. **Sort every comment** into keep, rewrite, or delete, and make an
   inventory of the tuning parameters. This pattern finds most tenet-1
   violations:

   ```bash
   grep -rniE '(#|//|\*)[^"]*\b(added|removed|changed|updated|fixed|refactored|renamed|replaced|now (returns|handles|uses|supports)|no longer|previously|used to|in this version|as requested|per the review)\b' --include='*.py' --include='*.ts' --include='*.js' .
   ```

4. **Show the plan before you edit**, if the pass covers more than one or two
   files. Give the counts for each category, the tuning-parameter inventory
   with the real, fossil, and coupled groups, and every comment that
   contradicts its code. A comment that contradicts its function is a defect
   report. Raise it, and do not delete it quietly.
5. **Edit the comments only.** Do not rename, do not reformat, and do not
   change logic. Do not make a repair that you find on the way. A reviewer
   must read the diff in one pass. Write down the other work, and leave it.
6. **Verify.** Run the tests for the repository
   (`python -m unittest discover -s tests`). At a minimum, import or parse
   every file you edited. Comment edits break code more often than expected:
   an unterminated docstring, a deleted line that held an `else` body, or a
   `# type: ignore` that went out with the noise.
7. **Write the summary.** Give the comments deleted, rewritten, and added for
   each file. Give the tuning parameters that now have documentation, and the
   parameters you recommend for removal. List every comment that describes
   behavior the code no longer has.

## Language notes

**Python.** The docstring is the interface, and the comments are the local
notes. Put the durable facts in the docstring: what the function does, its
parameters, its return value, and the exceptions it raises. Let the `#`
comments cover the local surprises only. A `#` comment directly above a `def`
usually belongs in the docstring. Follow the docstring style of the file.
This repository uses one short paragraph, not numpydoc. Type hints document
the types, and a comment that repeats them is noise.

**JavaScript and TypeScript.** A JSDoc `@param` or `@returns` tag that
repeats the TypeScript signature is duplication. Keep the description line
and delete the tag. `@param {string} name - the name` above a typed parameter
adds nothing. In a `.d.ts` file and on an exported API, the doc comment is
the documentation, so make it shorter instead of deleting it. A tuning
parameter that a config module exports needs the full block comment, even
when its type is `number`.

## Example

Before. Thirteen lines, one useful fact, and the useful fact is absent:

```python
# Updated this function to use the parser instead of regex
# Now handles both .mdl and .rls files
def load_digest(path, tol=0.001, window=5, retries=3):
    # Get the suffix
    suffix = path.suffix.lower()
    # Check if it's a model file
    if suffix == ".mdl":
        # Parse the model
        return parse_model(path, tol=tol, window=window, retries=retries)
    # Otherwise parse as ruleset
    return parse_ruleset(path)
```

After. The history and the repetition are gone, the interface moved into the
docstring, and the audit reports the parameters:

```python
def load_digest(path, tol=0.001, window=5, retries=3):
    """Parse a .mdl or .rls file into a structural digest."""
    suffix = path.suffix.lower()
    if suffix == ".mdl":
        return parse_model(path, tol=tol, window=window, retries=retries)
    return parse_ruleset(path)
```

```
Tuning parameters
  tol      real     needs the full comment at its definition in parse_model
  window   fossil   default only, 4 call sites, absent from the tests -> inline as 5
  retries  fossil   default only, absent from the tests -> inline as 3

Stale comment removed
  "Now handles both .mdl and .rls" - the .rls path is the fallback branch, so
  every suffix that is not .mdl takes it, and this includes .txt. This needs
  a real check.
```

The report matters as much as the edit. The noise hides the stale comments
and the unused parameters, and the pass makes them visible.
