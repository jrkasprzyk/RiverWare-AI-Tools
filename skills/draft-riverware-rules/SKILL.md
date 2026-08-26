---
name: draft-riverware-rules
description: Draft a RiverWare RPL policy rule from a plain-language operating-policy request — grounded in the target model's actual objects, slots, and existing ruleset style — and state where it belongs in the agenda. Use when asked to write, draft, add, or modify a RiverWare rule, RPL logic, or operating policy for a model. Can also apply the draft directly to the .mdl file, but only when the user explicitly asks for that.
---

# Draft a RiverWare rule

This skill turns a plain-language policy request ("add a spring flood-control
drawdown for Cedar") into a pasteable RPL rule that fits the target model: it
references only slots that exist, matches the ruleset's existing idioms, and
comes with an explicit statement of where it belongs in the agenda.

The deliverable is a **draft for a modeler to review and load** — never a
validated rule. Only RiverWare loading and running the ruleset validates RPL.

Paths below are relative to the root of this repository. If this skill was
installed as a **plugin**, that root is `${CLAUDE_PLUGIN_ROOT}` and the working
directory is the user's own project — prefix the script and `examples/` paths
with it. The `.mdl` the user asks about is their own file and is not under that
root.

## Stay inside the working directory

Work only with files in the user's project. The plugin's own bundle under
`${CLAUDE_PLUGIN_ROOT}` — its scripts and its `examples/` models — is yours to
read. The rest of the filesystem is not.

- **A named file that is not there is a question, not a search.** If a close
  match sits in the working directory, offer it and stop: asked for
  `saratoga_v2.1.md`, found `saratoga_v2.1.mdl`, say so. Do not scan parent
  directories, sibling projects, or the drive for a matching name.
- **A path found inside a model file is not permission to open it.** A `.mdl`
  records where its ruleset and data lived on the author's machine, often
  outside the project. Report the path and ask.

Widening the search is cheaper to do than asking is, which is why it happens
first. Ask.

## Step 1 — digest the model first, always

Never draft against an unread model. Run the explain skill's parser to get the
ground truth:

```bash
# cloned repository, run from the repo root
python skills/explain-riverware-model/explain.py examples/ArborBasin/ArborBasin.mdl

# installed as a plugin, run from anywhere
python "${CLAUDE_PLUGIN_ROOT}/skills/explain-riverware-model/explain.py" path/to/your/model.mdl
```

From the digest, collect what the draft must respect:

- **The slots involved.** Exact object and slot names for everything the rule
  will read or set. The digest is the source of truth — if the request names a
  quantity and no matching slot exists, stop and say so (see Guardrails).
- **Agenda order and group structure.** Which policy groups exist, what each
  covers, and the agenda order (`ASCENDING` means the bottom rule of the
  listing fires first, so later-firing rules override earlier ones).
- **The ruleset's RPL idioms.** How existing rules are written: do they wrap
  object access in `WITH_STATEMENT`, call shared utility functions
  (e.g. `OutflowForMaxElevationRules`), use `IF` expressions inside
  assignments vs `IF_STATEMENT` blocks, attach units to every literal? Mirror
  what is there; do not import styles from other models.

If the rules are embedded in the `.mdl` (both example models here), the digest
lists the RPL set names; read the specific rule bodies with a targeted grep or
narrow line-range read of the `.mdl` — never the whole file.

Grep recipes that work on embedded RPL (every line in an RPL section ends
with a `\` continuation, so anchors behave oddly — prefer unanchored
patterns):

- Locate the sets and their groups: grep for `NAME "|POLICY_GROUP` with line
  numbers, then Read the line range of the set you need.
- Locate individual rules inside a set: grep for `RULE ` (unanchored;
  `^RULE` misses).

Beware long lines: some `.mdl` regions (run diagnostics such as
`lastDispatchPriority`, `successfulRulesVer2`) pack a whole run into single
enormous lines — a ten-line Read there can blow the token limit. Fall back to
`sed -n 'START,ENDp' file | cut -c1-400` to skim those regions.

## Step 2 — draft the rule

Write the rule in the model's own style, then present it as a fenced code
block the user can paste into the RiverWare RPL editor. With the draft, state:

1. **Agenda placement.** Which policy group it belongs in and where —
   remembering that with `ASCENDING` order, placing a rule *above* an existing
   rule in the listing means it fires *after* it and can override it. Say the
   consequence out loud: "listed above `Cedar Outflow Min`, so it fires after
   the minimum-outflow floor and takes priority over it."
2. **What it reads and sets**, slot by slot.
3. **Assumptions made** — anything the request left open that you resolved
   (thresholds, dates, tie-breaking).

## Step 3 — always end with the review caveat

End every draft with words to this effect:

> This is a draft. Load it in RiverWare's RPL editor, check units and slot
> references, and test-run before trusting it. RPL is only validated by
> RiverWare itself.

## Guardrails

- **Never draft against a ruleset you have not read.** If the digest's
  Embedded RPL sets list has no `Rule Based Simulation` set, the operating
  policy is in a separate `.rls`. Stop. The `.mdl` records that file's path —
  report it and ask the user to supply the file; do not go read it yourself,
  since the recorded path often lies outside the project (a network share, a
  sync folder, someone else's directory). Stay inside the working directory.
  If the file cannot be supplied, say that drafting is blocked and why: with
  no ruleset you cannot match its idioms, cannot reuse its utility functions,
  and cannot place the rule in an agenda you have never seen. A draft written
  blind looks equally authoritative and is far likelier to be wrong.
- **Never invent slot names.** Every `Object.Slot` reference must appear in
  the digest. If the policy needs a slot the model lacks (e.g. a new threshold
  scalar or a custom series), say explicitly: "this needs a new slot
  `X.Y` created on the object first — drafting alone cannot add it," and
  describe the slot rather than pretending it exists.
- **Mirror function-vs-inline conventions.** If the model factors shared logic
  into utility-group functions, extend or call those functions; do not inline
  a competing copy. If it inlines everything, do not introduce a function.
- **Units on every numeric literal** (`220.00 "m"`, `0.00 "cms"`) if that is
  the model's style — it almost always is.
- **One rule, one job.** If the request bundles several behaviors, draft
  separate rules and explain the firing-order relationship between them.
- **Keep companion slots consistent.** Before capping or overriding a slot
  another rule sets, check whether that rule mirrors the same quantity into a
  second slot (e.g. an irrigation rule that sets both `Res.Release` and
  `Farms.Incoming Available Water`). A new rule that changes one but not the
  other leaves the model internally inconsistent — deliveries credited for
  water never released. Update both together, mirroring the existing rule's
  precedent, and say so in the assumptions.
- **Explaining an existing rule** is a supporting move — use it to ground an
  edit ("here is what `Cedar End of Month Guide Curve` currently does, and
  here is the modified draft") — but the deliverable of this skill is the
  draft, not the explanation. For pure model documentation, use the
  explain-riverware-model skill instead.

## Applying the draft to the model file (advanced, opt-in)

The default deliverable of this skill is a **draft** — a fenced code block the
modeler pastes into the RPL editor themselves. Do not edit the `.mdl`. The
exception is when the user explicitly asks for the rule to be written into the
model file ("add it to the model file", "don't just draft", "apply it"). A
placement suggestion or an ambiguous "add a rule to the model" is a request
for a draft, not an edit.

When the user has explicitly asked, follow this sequence:

1. **Back up first.** Copy the `.mdl` to a clearly named sibling (e.g.
   `model_pre-<change>-backup.mdl`) before touching it, and tell the user
   where the backup is.
2. **Generate a fresh UUID for every new item.** Each `RULE`, `FUNCTION`,
   slot, and group in a `.mdl` carries a UUID (introduced in RiverWare 7.5;
   the RPL comparison and copy-property tools match items by UUID, not name).
   Random version-4 UUIDs are correct — `python -c "import uuid;
   print(uuid.uuid4())"` — one per new item, never reused from an existing
   item.
3. **Match the file's serialization exactly.**
   - RPL items end with `UUID "{...}";;` and every line in an RPL section
     ends with a `\` continuation — including blank lines.
   - A new ScalarSlot on an object is a block of the form:

     ```tcl
     "$o" {ScalarSlot} {Slot Name}
     set s "$o.Slot Name"
     "$s" order N
     "$s" UUID {xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}
     "$s" units 1 {%f} 2
     "$s" value 2165 {m}
     ```

     inserted among the object's other slot blocks (before the object's
     `hideSlots` line), copying `units`/format arguments from a sibling slot
     of the same unit type.
   - Insert new rules at the position in the group that encodes the intended
     agenda priority, and new functions inside the appropriate
     `UTILITY_GROUP`.
4. **Leave run diagnostics alone.** Lines like `rulesInformation` and
   `successfulRulesVer2` are last-run bookkeeping; they go stale when rules
   are added and RiverWare rebuilds them on the next run. Do not try to
   renumber them.
5. **Smoke-test by re-running the digest** (`explain.py`) on the edited file
   and confirming the new slot/rule appears. This proves the file still
   parses for the digest tool — it does not validate the RPL.
6. **The Step 3 caveat still applies**, strengthened: the file was edited
   outside RiverWare, so the user must load the model in RiverWare to
   validate it, and can revert via the backup if the load fails.

## RPL syntax reference (worked example)

A predecessor-style rule in the idiom used by the example models — an
`IF`-expression assignment wrapped in `WITH_STATEMENT`, units on literals,
predefined functions in double quotes:

```rpl
RULE "Cedar Spring Drawdown";
DESCRIPTION "Draw Cedar down toward the flood-control elevation in spring.";
ACTIVE TRUE;
BEGIN

  WITH_STATEMENT (OBJECT res = % "Cedar") DO
        res & "Outflow" [] := IF ( "GetMonth"( @"t" ) >= 3.00000000 AND
                                   "GetMonth"( @"t" ) <= 5.00000000 AND
                                   res & "Pool Elevation" [] > 235.00000000 "m" )
   THEN
    "Min"( "SolveOutflow"( res, res & "Inflow" [],
                           "ElevationToStorage"( res, 235.00000000 "m" ),
                           res & "Storage" [@"t - 1"], @"t" ),
           "GetMaxOutflowGivenInflow"( res, res & "Inflow" [], @"t" ) )
   ENDIF;

  END_WITH_STATEMENT;

END
```

Anatomy worth copying:

- `% "Object"` is an object reference; `res & "Slot" []` reads/sets a slot on
  a `WITH_STATEMENT`-bound object; `$ "Object.Slot" []` is the direct form.
- `[]` is the current-timestep index; `[@"t - 1"]` reads the previous
  timestep.
- An `IF` expression with no `ELSE` leaves the slot unset when the condition
  is false — a later (or earlier-fired) rule or the solver fills it. Use
  `IF_STATEMENT ... END_IF_STATEMENT;` for imperative blocks
  (`STOP_RUN_STATEMENT`, `WARNING_STATEMENT`, `FOREACH` loops).
- Predefined and utility functions are always called with quoted names:
  `"Min"`, `"SolveOutflow"`, `"ElevationToStorage"`,
  `"GetMaxOutflowGivenInflow"`.

## Worked example

`examples/ArborBasin/ArborBasin_rule_case_study.md` walks a full
request → draft → placement case study against the Arbor Basin model. Use it
as the target shape for how a delivered draft should read.
