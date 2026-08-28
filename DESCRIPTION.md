## Documentation Profiles (Rules, Functions, and Input Data Slots)

When annotating **policy rules**, **user‑defined functions**, or **input data slots**, descriptions must follow RiverWare documentation standards used in the Rule Editor, Function Editor, and Slot Editor. The annotate skill formats proposed descriptions according to the profiles below. During review, ensure each proposed annotation meets the required structure before approval.

---

### Rule Documentation

Each rule description must contain **three parts**:

#### 1. Execution Constraint
Describe the criteria that must be met for the rule to be evaluated.  
Example:  
- “Month is May.”

#### 2. Description
Plain English explanation of what the rule does.  
If the rule references model input data:  
- Name the input slots  
- Specify where the referenced data can be found  
- Include those slots in the *Input Data Report Group*  

Example:  
- “Sets the number of days at power plant capacity based on the spring hydrologic classification. The ranges for each classification are stored in the slot `DaysAtPowerPlantCapacity`.”

#### 3. Slots Set
List the slots whose values the rule updates.

#### Inline Rule Comments
Rules may include RPL inline comments using `#`.  
Use comments sparingly for contextual clarity above logic blocks.  

Example:  
- `# For August`

---

### User‑Defined Function Documentation

Each user‑defined function or global function description must contain **four parts**:

#### 1. Arguments
List arguments in order, including units and timestep context when applicable.  
Not all functions have arguments.  

Example:  
- “Reservoir object, current month, previous storage.”

#### 2. Description
Plain English explanation of what the function computes.  

Example:  
- “Calculates the number of days required to down-ramp from power plant capacity to base flow.”

#### 3. Returns
Describe the single return value, including units.  
Example:  
- “Returns the outflow of Lake Mead in cfs.”

#### 4. Constraints
Describe maximum/minimum bounds or behavior when constraints are exceeded.  
Example:  
- “If the calculated release exceeds the maximum release, the function returns the maximum release.”

#### Inline Function Comments
Functions may include RPL inline comments (`#`) when needed for clarity.

---

### Input Data Slot Documentation

Input data slots used by rules or rule‑specific functions must be documented in the Slot Editor and included in the *Input Data Report Group*. Each slot description should contain:

#### Purpose
Explain what the slot represents and why it matters.  
Example:  
- “Contains flow values in cfs for the down-ramp rate based on the year’s hydrologic classification.”

#### Units, Range, and Source
- Units of the data  
- Typical or allowed range  
- Source of data (e.g., manual entry, DMI, annual update)

#### Consumers
Identify which rules or functions read the slot.

---