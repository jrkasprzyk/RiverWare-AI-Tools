### name: annotate-riverware-model
description: Propose and apply descriptions and RPL comments to a RiverWare model — objects, slots, rules, functions, and the model itself — reviewed by the modeler before anything is written.

## Annotate a RiverWare model

Deliverable: **proposal + approved application**, never a finished annotated model handed over without review.

**Hard rule:** Never read a `.mdl` raw. Use the parser; read only narrow ranges to verify specific blocks.

### Step 1 — digest, then inventory what is already described
Run twice:

- `SKILL-code-explain_riverware_model.py model.mdl`
- `SKILL-code-explain_riverware_model.py model.mdl --annotations`

The inventory marks `[x]` for taken and `[ ]` for available targets and ends with target-path forms the proposal JSON uses. Anything `[x]` is off the table.

For rule bodies needed to describe a rule honestly (and for expression comments), read targeted narrow line ranges from the `.mdl`.

### Step 2 — decide what deserves an annotation
Apply the tastefulness rubric (objects, policy-meaning slots, rules/functions only when names are not self-explanatory, minimal expression comments, concise model description). Restraint is the deliverable.

### Documentation Profiles (Rules, Functions, and Input Data Slots)

When annotating **policy rules**, **user‑defined functions**, or **input data slots**,
descriptions must follow RiverWare documentation standards used in the Rule Editor,
Function Editor, and Slot Editor. The annotate skill formats proposed descriptions according to the profiles below.
During review, ensure each proposed annotation meets the required structure before approval.

---

## Rule Documentation

Each rule description must contain **three parts**:

### 1. Execution Constraint
Describe the criteria that must be met for the rule to be evaluated.  
Example:  
- “Month is May.”

### 2. Description
Plain English explanation of what the rule does.  
If the rule references model input data:  
- name the input slots,  
- state where the data can be found, and  
- ensure those slots are included in the *Input Data Report Group*.  

Example:  
- “Sets the number of days at power plant capacity based on the spring hydrologic classification. The ranges for each classification are stored in the slot `DaysAtPowerPlantCapacity`.”

### 3. Slots Set
List the slots whose values the rule updates.

### Inline Rule Comments
Rules may include RPL inline comments using `#`.  
Use comments sparingly for contextual clarity above logic blocks.  

Example:  
- `# For August`

---

## User‑Defined Function Documentation

Each user‑defined function or global function description must contain **four parts**:

### 1. Arguments
List arguments in order, including units and timestep context when applicable.  
Not all functions have arguments.  

Example:  
- “Reservoir object, current month, previous storage.”

### 2. Description
Plain English explanation of what the function computes.  

Example:  
- “Calculates the number of days required to down-ramp from power plant capacity to base flow.”

### 3. Returns
Describe the single return value, including units.  
Example:  
- “Returns the outflow of Lake Mead in cfs.”

### 4. Constraints
Describe maximum/minimum bounds or behavior when constraints are exceeded.  
Example:  
- “If the calculated release exceeds the maximum release, the function returns the maximum release.”

### Inline Function Comments
Functions may include RPL inline comments (`#`) when needed for clarity.

---

## Input Data Slot Documentation

Input data slots used by rules or rule‑specific functions must be documented in the Slot Editor and included in the *Input Data Report Group*. Each slot description should contain:

### Purpose
Explain what the slot represents and why it matters.  
Example:  
- “Contains flow values in cfs for the down-ramp rate based on the year’s hydrologic classification.”

### Units, Range, and Source
- Units of the data  
- Typical or allowed range  
- Source of data (e.g., manual entry, DMI, annual update)

### Consumers
Identify which rules or functions read the slot.

---

### Step 3 — write the two proposal artifacts
- `<model>_annotations.md` — human review doc with counts and numbered proposals + rationale.
- `<model>_annotations.json` — machine proposal (schema with target_type/target/text; literals for `rpl_comment`).

### Step 4 — get approval, then apply
After approval, run one of:

- `SKILL-code-annotate.py model.mdl model_annotations.json`
- `SKILL-code-annotate.py model.mdl model_annotations.json --dry-run`
- `SKILL-code-annotate.py model.mdl model_annotations.json --in-place`

Read the applier’s summary back to the user (applied, skipped, not found — fix paths before claiming success).

### Step 5 — end with the review caveat
Only RiverWare validates a `.mdl`. Load in the GUI and confirm the descriptions appear where expected.

### Guardrails
- Never write without a review artifact and approval.
- Never overwrite an existing description/comment.
- Never invent model facts; skip targets you cannot defend.
- Do not describe a rule you have not read.
- Restraint is the deliverable.

### Reference
- `.mdl` serialization grammar (see `SKILL-reference-annotate.md`).
- Relevant skills: explain, draft.

**If example files are not present:** Run the skill against user-supplied `.mdl`/`.rls`. If none are provided, answer using the skill output and REF_ documentation.