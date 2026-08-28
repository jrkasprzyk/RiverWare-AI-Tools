## RiverWare .mdl annotation grammar

How RiverWare serializes the five annotation surfaces this skill writes.

Captured July 30, 2026 (RiverWare 9.7) from observed models. A `.mdl` is a Tcl script; each annotation is a Tcl command argument, so correctness has two halves: the token is right, and surrounding bytes remain untouched.

### 1. File-level byte discipline
Read/write as **bytes**, keep line endings per file, preserve trailing newline.

#### Re-save caveat
A RiverWare save perturbs timestamps, usernames, geometry, and scroll position. Validation diffs must be applier-output vs. applier-input, not RiverWare-save vs. save.

### 2. Object description — `userDescript`
Insert immediately after the object’s `objAttributes` block; absent when unset.

### 3. Slot description — `userDescript`
Insert after the slot’s `UUID` line (skip immediate `computedByExpr`), then `userDescript`. Absent when unset.

### 4. Model description — `$ws.Model.FileInfo comment`
Line is always present (empty braces when unset). Replace contents.

### 5. RPL `DESCRIPTION` fields
Preserve existing indentation/padding at set/group/rule/function levels and the trailing continuation `\\`. Replace only the empty quoted string.

Statement-level `DESCRIPTION` can appear inside a rule body; read bodies before proposing rule descriptions.

Target paths disambiguate duplicates: `<Set>/<Group>/<Rule>`.

### 6. RPL expression comments — `COMMENTED_BY`
Postfix on an expression in the RPL body. v1 scope: numeric literals only; identify by exact serialized text (with units) and occurrence index.

### 7. Escaping and text restrictions
Brace-string vs. double-quoted string rules; use safe text:
- No `{`, `}`, `\`, or literal newline/carriage return.
- No `"` inside RPL strings (brace strings permit `"`).
- ≤ 400 characters.

### 8. Never overwrite (REQ-005)
Eligible only when the target field is empty.

### 9. Only RiverWare validates a `.mdl`
Load the annotated model in RiverWare and confirm annotations in the GUI before trusting it.

**If example files are not present:** Operate on user-supplied files; if none are provided, answer using the skill output and REF_ documentation.