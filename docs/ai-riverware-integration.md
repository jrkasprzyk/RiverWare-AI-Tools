# ChatGPT (custom GPT) ↔ RiverWare integration

This repository provides the instructions and files to create a custom
GPT (https://chatgpt.com/gpts) that integrates with a local installation
of RiverWare (https://www.riverware.org/). Please note that custom GPTs are
not available with personal chatGPT accounts;  Business, Enterprise, or Edu
workspace accounts with the correct workspace permissions are required.

## What works today

### 1. Parsing RiverWare model files and rulesets

RiverWare's `.mdl` and `.rls` files are text. The RiverWare modelfile (`.mdl`) uses the same format as a Tcl
script. The RiverWare Policy Language (RPL) defines rules and functions. A separate `.rls` file is sometimes provided, or the RPL elements are embedded into the model file.

These files are too large for current AI agents to read
directly (1.6–1.9 MB for the models here), but small parsers can extract
everything an agent needs: objects, slots, selected simulation methods,
lookup tables, link topology, DMIs, embedded rulesets, and stored results.

The repository contains two skills for this purpose:

- **[explain-riverware-model](../skills/explain-riverware-model/SKILL.md)**
  turns the parsed digest into a narrative model explanation
  ([example](../examples/ArborBasin/ArborBasin_explained.md)).
- **[visualize-riverware-model](../skills/visualize-riverware-model/SKILL.md)**
  turns it into a self-contained interactive dashboard
  ([live examples](https://jrkasprzyk.github.io/RiverWare-AI-Tools/)).

These skills demonstrate the fact that RiverWare's file formats can be directly used within AI tooling.
The files are parseable with modest scripts, and once parsed, a capable
agent can reason about model structure fluently.

### 2. Drafting rulesets

An agent that digests
a model first can draft rules that fit it. 

The skill
**[draft-riverware-rules](../skills/draft-riverware-rules/SKILL.md)**
produces pasteable RPL grounded in slots that actually exist, with explicit
agenda-placement reasoning
([example case study](../examples/ArborBasin/ArborBasin_rule_case_study.md)).
Note: a drafted rule is unvalidated until RiverWare
loads and runs it.

### 4. Analyzing output data

RiverWare's exports (DMI data files, RDF, CSV) are plain text an agent can
parse, plot, and narrate with ordinary data tooling. The dashboard skill's
time-series panels read results stored in the `.mdl` itself; the same
approach extends to any export a run produces.

## Use instructions

This repository contains the instructions and knowledge files to create
a custom GPT that is skilled at working with RiverWare model file and rulesets.
To create the custom GPT, follow the below steps.

1. **Open a new GPT.** Navigate to https://chatgpt.com/gpts and select 'Create'
   in the upper right corner. Provide a name (eg 'RiverWare 9.7 Helper Bot')
   and description (eg 'a GPT agent with knowledge of RiverWare documentation
   that can write documentation, draft RPL, plot slots, and other tasks'.)
2. **Copy/paste the instructions from instructions.txt** into the 'instructions'
   area of the GPT. 
3. **Upload all files in the knowledge folder to the GPT knowledge** INSTRUCTIONS to come
4. **Create conversation starters.** We suggest using the following conversation
   starters, but feel free to add or substract.
   - (to come)
   - (to come)
   - (to come)
4. **Enable Code Interpreter & Data Analysis.** In the capabilities area, check
   Enable Code Interpreter & Data Analysis.
5. **Create GPT.** Select 'Create' in the top right corner.
6. **Share GPT (optional)** Select 'Share' in the top right corner and enter the
   email addresses you want to share with. For others to access the GPT, the email
   must be associated with an account that has access to GPTs (free accounts do
   not). 
   

## Considerations

- **Licensing.** RiverWare is a licensed desktop application, and a license is required to run RiverWare with these tools.
- **Validation.** AI-drafted RPL and AI-run experiments are drafts. RiverWare's load-time checks and modelers' are still needed to ensure accuracy and quality.
- **Format drift.** The parsers here are verified against RiverWare 9.4–9.7 files. New format versions may need parser updates.

