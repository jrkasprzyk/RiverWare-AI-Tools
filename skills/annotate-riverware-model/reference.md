# RiverWare `.mdl` annotation grammar

How RiverWare serializes the five annotation surfaces this skill writes.
Everything below was captured by diffing `examples/TwoResOps/saratoga_v2.4.mdl`
(descriptions set by hand in the RiverWare 9.7 GUI, then re-saved) against its
pre-description copy `saratoga_v2.4.mdl.bak`, plus targeted line-range reads of
`examples/ArborBasin/ArborBasin.mdl`. Captured 2026-07-30, RiverWare 9.7.

A `.mdl` is a Tcl script. Each annotation is an argument to a Tcl command, so
correctness has two halves: the **token** must be right, and the surrounding
bytes must survive untouched.

---

## 1. File-level byte discipline

Read and write the file as **bytes**, split with `splitlines(keepends=True)`,
and rejoin. Do not use text mode with newline translation.

| Property | Value | Why it matters |
|---|---|---|
| Encoding | UTF-8, no BOM | A BOM prepended to line 1 breaks the `# RiverWare_Model` header. |
| Line endings | **Per file, not per repo** — `saratoga_v2.4.mdl` is CRLF, `ArborBasin.mdl` is LF | Normalizing rewrites every line in the file. The round-trip test (TEST-001) catches this. |
| Trailing newline | Present in both models | Preserve it. |

Newly inserted lines use whichever ending the file already uses. Detect it from
the first line's suffix rather than assuming the platform default.

### The re-save caveat

A RiverWare save perturbs bytes that have nothing to do with annotation:

```
-# Created 18:06 July 14, 2026          +# Created 12:26 July 30, 2026
-$ws.Model.FileInfo saveInfo 1 {user} …  +$ws.Model.FileInfo saveInfo 1 {joka0958} …
-WorkspaceSize 6615 6560                 +WorkspaceSize 6630 6570
- <CenterPos x="648.125" y="6101.875"/>  + <CenterPos x="661.875" y="6023.125"/>
-  <AutoSave … saveDir="." …>            +  <AutoSave … saveDir="./" …>
```

Timestamps, username, window geometry, scroll position. So **validation diffs
must be applier-output vs. applier-input**, never RiverWare-save vs.
RiverWare-save. A save-vs-save diff always contains noise and can never prove
the applier clean.

---

## 2. Object description — `userDescript`

```tcl
set obj {Cora}
set o "$ws.Cora"
$ws SimObj $obj {StorageReservoir} 77 568 {} 50 335 50 335
"$o" webMapCoords 173 391
"$o" geospatialCoords 0 0 50 335
"$o" UUID {4ff34611-058c-439d-8519-2318042fbcd6}
"$o" objAttributes {<SimObjAttributes simObjName="Cora"/>}
"$o" userDescript {Cora is the upstream Storage Reservoir. …}      <-- inserted
"$o" objOrd wsList 5032
```

- **Absent entirely when unset.** There is no empty-braces form for objects;
  annotating means *inserting a line*, not filling one.
- **Insertion anchor: immediately after the `"$o" objAttributes {…}` block.**
- An object block runs from its `$ws SimObj $obj {Type}` line to the next one.

**`objAttributes` has two forms.** Most objects get the one-liner shown above.
An object carrying custom attributes gets a multi-line brace argument instead,
with `simObjName` on the *following* line (ArborBasin.mdl:891):

```tcl
"$o" objAttributes { \
<SimObjAttributes simObjName="Aspen"> \
 <SimObjAttribute name="Fed or NonFed" value="Nonfederal"/> \
 <SimObjAttribute name="PUD" value="Douglas"/> \
</SimObjAttributes>}
"$o" userDescript {…}          <-- goes here, after the closing brace
```

So the anchor is the line that *closes* the brace argument (found by counting
braces from the opening line), and the name is whichever `simObjName="…"`
appears anywhere inside it. Anchoring on the opening line would insert the
description into the middle of the XML. Both example models are needed to see
this: saratoga has only the one-line form, ArborBasin only the multi-line one.

## 3. Slot description — `userDescript`

```tcl
"$o" {TableSlot} {Shortage Table}
set s "$o.Shortage Table"
"$s" order 26
"$s" UUID {a7b33c07-7e8a-4e0f-b406-b749990deeae}
"$s" userDescript {Pool Elevation determines shortages imposed …}   <-- inserted
"$s" resize 4 2
```

- Same absent-when-unset rule as objects.
- A slot block starts at `"$o" {<Type>Slot} {<Slot Name>}` and ends at the next
  `"$o" {` line or the next `$ws SimObj` line.
- **Insertion anchor: after the slot's `"$s" UUID {…}` line, skipping past any
  `"$s" computedByExpr …` line that immediately follows it.** RiverWare emits
  `order`, `UUID`, optional `computedByExpr`, then `userDescript`, then the
  value-bearing keys (`units`, `resize`, `setRowLabels`, `value`, `row`):

  ```tcl
  "$s" order 0
  "$s" UUID {79a5e9d5-…}
  "$s" computedByExpr 3 {"TimeBasedReliability"( $ "Cora.Pool Elevation", …)}
  "$s" userDescript {The ratio of timesteps in which Cora's pool elevation …}
  "$s" units 49 {%f} 2
  ```

  Position within the block is cosmetic — these are independent Tcl setter
  calls on the same slot — but matching RiverWare's own order keeps the diff
  legible and keeps a later RiverWare re-save from reordering the file.

## 4. Model description — `$ws.Model.FileInfo comment`

```tcl
$ws.Model.FileInfo saveInfo 1 {joka0958} {07-30-2026 12:26:50} {RiverWare 9.7}
$ws.Model.FileInfo comment {Saratoga is a two-reservoir river basin. …}
```

- **The line is always present**, with empty braces (`comment {}`) when unset.
  Annotating means *replacing the brace contents*, not inserting a line.
- Exactly one such line per model.

## 5. RPL `DESCRIPTION` fields

Embedded RPL lives inside brace-quoted Tcl arguments, so every RPL line carries
a trailing `\` line-continuation. The field is always present and empty:

```tcl
$rsm loadedSet {RULESET\
NAME "RPL Set";\
AGENDA_ORDER ASCENDING;\
DESCRIPTION "";\                        <-- set level
PRECISION   2;\
NOTES "";\
BEGIN\
\
  POLICY_GROUP   "Post Processing";\
  DESCRIPTION    "";\                   <-- group level
  ACTIVE         TRUE;\
  NOTES          "";\
  BEGIN\
\
    RULE                 "Wildlife Sanctuary Calculations";\
    DESCRIPTION          "";\           <-- rule level
    ACTIVE               TRUE;\
    RULE_EXEC_CONSTRAINT TRUE;\
    NOTES                "";\
    BEGIN\
```

- **Indentation and internal padding differ by level** — `DESCRIPTION "";\` at
  set level, `DESCRIPTION    "";\` under a group, `DESCRIPTION          "";\`
  under a rule (the padding aligns the values with `RULE_EXEC_CONSTRAINT`).
  Functions use yet another width. **Never rebuild the line**; replace only the
  `""` between the existing prefix and the existing `;\` suffix.
- The trailing `\` is load-critical. Preserve it exactly.

### A second, statement-level `DESCRIPTION`

A `DESCRIPTION` line can also appear **inside** a `BEGIN`/`END` body, attached
to the statement that follows it. Saratoga's `Irrigation` rule has an empty
header field and a filled one in the body:

```tcl
    RULE                 "Irrigation";\
    DESCRIPTION          "";\                <-- the rule's own field, empty
    ACTIVE               TRUE;\
    RULE_EXEC_CONSTRAINT TRUE;\
    NOTES                "";\
    BEGIN\
\
    DESCRIPTION          "Irrigation water for Winifred Valley Farms is …";\
      IF_STATEMENT ($ "Roberto.Pool Elevation" [@"t - 1"] < …) THEN\
```

Both the applier and `explain.py --annotations` stop scanning at `BEGIN`, so
they read only the header field and never confuse the two. But the consequence
for the *propose* step is real: such a rule is already documented even though
its header field reads empty, and the inventory will show it as available.
Read the body before proposing a rule description.

v1 does not write statement-level descriptions.

### Locating a `DESCRIPTION` target

Rule names are **not unique across groups** — saratoga has a `Prevent
Overtopping` in both `Roberto Rules` and `Cora Rules`. A target must therefore
be a path: `<set>/<group>/<rule>`.

Sets are introduced by distinct Tcl commands, each followed by `NAME "…";\`:

| Command line | Set type |
|---|---|
| `$rsm loadedSet {RULESET\` | Rule Based Simulation |
| `$ws.GlobalRplSetMgr globalFunctionSet {RULESET\` | Global Functions |
| `$ws initRules {RULESET\` | Initialization Rules |
| `$resm resmRplSet {RULESET\` | Expression Slots |

Use the `NAME "…"` value as the set name; the command line only marks where a
set begins.

Groups are `POLICY_GROUP "…";\` or `UTILITY_GROUP "…";\`; items are
`RULE "…";\` or `FUNCTION "Name" ( args );\`. In each case the first
`DESCRIPTION` line at or after the header, before the next header of the same
or higher level, is that item's field.

## 6. RPL expression comments — `COMMENTED_BY`

`COMMENTED_BY "text"` is a **postfix operator on an expression**, emitted inline
in the RPL body:

```rpl
0.00000000 "kcfs" COMMENTED_BY "Do not let flow be negative"\
```

```rpl
"SumFlowsToVolume"( provided_flowrate, @"Start Timestep", @"Finish Timestep" ) COMMENTED_BY "If both the water received and requested are stored in series slots, …<br>" / "SumFlowsToVolume"( requested_flowrate, … );\
```

```rpl
  $ "Wildlife Sanctuary.Gage Inflow" [] COMMENTED_BY "In the case of a non-zero deficit, record how much was provided <br>"\
 ELSE\
  $ "Wildlife Sanctuary.Eco Flow Pattern" COMMENTED_BY "Otherwise, there was no deficit. …<br>" []\
```

Note the third example: the comment sits **between the slot reference and its
`[]` index**. RiverWare's serializer attaches the comment to the subexpression
node the modeler clicked in the GUI, and that node's textual extent is not
recoverable from the flattened line.

**This settles ASSUMPTION-002 in the affirmative** — `COMMENTED_BY` is valid on
arbitrary expressions, not only literals. It does *not* make arbitrary
expressions safe to target: an applier cannot reliably decide where a given
subexpression ends inside a single flattened, continuation-terminated line.

**v1 scope: numeric literals only.** A target is identified by the rule path
plus the literal's exact serialized text (e.g. `0.00000000 "kcfs"`) and its
occurrence index within the rule body. The applier inserts
` COMMENTED_BY "text"` immediately after the literal (including its unit
string, which is part of the literal). Wider targeting waits for a fixture that
shows how the GUI attaches comments to compound nodes.

---

## 7. Escaping and text restrictions (CON-004)

Two different string syntaxes, one shared restriction.

| Surface | Syntax | Terminator |
|---|---|---|
| `userDescript`, `FileInfo comment` | Tcl brace string `{…}` | unbalanced `}` |
| `DESCRIPTION`, `COMMENTED_BY` | RPL double-quoted `"…"` | `"` |

Observed facts:

- **Newlines are serialized as the literal four characters `<br>`**, in both
  syntaxes — never as `\n`. `explain.py:_clean()` reverses this for display.
  Example, saratoga slot `Damage Curve`:
  `"$s" userDescript {Claude advice on Damage Curves overall:<br><br>  Calibrate a damage function…}`
- **Unescaped `"` appears freely inside brace strings** (`…the "preferred flow
  limit" in the city…`), because `"` has no meaning to Tcl inside `{}`.
- **Inside an RPL string, `"` is escaped as the HTML entity `&quot;`.** Saratoga's
  `WinifredFarmsRequestWithShortage` comment reads
  `The decision variable &quot;Shortage Ratio&quot; is a number from 0 to 1.0 …`.
  This is a *v2 opportunity, not v1 behavior*: the applier could encode quotes
  itself, but CON-004 fixes v1 as reject-don't-guess, and one round trip through
  RiverWare has not yet confirmed the entity decodes back to `"` in the GUI.
- **No observed example contains `{` or `}` inside an RPL string.** How
  RiverWare would escape those is still unknown.

v1 accordingly restricts annotation text to what is provably safe:

- No `{` or `}` (would terminate or unbalance a Tcl brace string).
- No `"` in `DESCRIPTION` or `COMMENTED_BY` text (would terminate the RPL
  string). Permitted in `userDescript` and `comment`, which are brace strings.
- No literal newline or carriage return; write single-line text. (`<br>` is
  accepted as an explicit author choice, but the rubric asks for one or two
  sentences, which never need it.)
- No `\` (line-continuation character in the embedded RPL sections).
- At most 400 characters — comfortably above every observed description and
  well inside ASSUMPTION-001.

The applier **rejects** violating text with a message naming the offending
character, rather than escaping it and hoping.

---

## 8. Never overwrite (REQ-005)

Both example models already carry hand-written annotations — saratoga has ten
`userDescript` lines and one filled rule `DESCRIPTION`; ArborBasin has eleven
auto-generated `Subbasin Membership List Slot` slot descriptions. A target is
eligible only when:

- object / slot: **no** `userDescript` line exists in the block;
- `DESCRIPTION`: the field is exactly `""`;
- `FileInfo comment`: the braces are exactly `{}`;
- `COMMENTED_BY`: the chosen literal occurrence is not already followed by one.

Anything else is reported as `SKIPPED (existing text)` and left alone.

---

## 9. Only RiverWare validates a `.mdl`

Every check here is textual. A `.mdl` that this applier considers clean can
still be rejected — or worse, silently misread — by RiverWare. Load the
annotated model in RiverWare and confirm the annotations appear in the GUI
(open-object dialog, slot dialog, RPL editor description tab) before trusting
it.
