# AI ↔ RiverWare integration

This repository demonstrates integration between AI coding agents and
RiverWare. This document briefly explains what an agent can already do
with the tools here, and the directions that look most promising next. 

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

### 3. Live batch-mode control

RiverWare's batch mode (RCL scripts) plus DMIs allow workflows where automated tools can interface directly with the model. 

The **[riverware-mcp prototype](../prototypes/riverware-mcp/)**
wraps that surface in model context protocol (MCP) tools (`list_objects`, `list_slots`, `set_slots`,
`run_model`, `read_slots`) so any MCP-capable agent can run policy
experiments against a licensed local RiverWare install. 

An initial verification was completed using  RiverWare
9.7: a four-tool-call loop measured the transbasin trade-off in the Arbor
Basin model ([transcript](../prototypes/riverware-mcp/demo_transcript.md)).

MCP servers like this can enable optimization, sensitivity study, calibration, and what-if conversations. A similar DMI structure is used in **Borg-RiverWare** to facilitate multi-objective optimization.

### 4. Analyzing output data

RiverWare's exports (DMI data files, RDF, CSV) are plain text an agent can
parse, plot, and narrate with ordinary data tooling. The dashboard skill's
time-series panels read results stored in the `.mdl` itself; the same
approach extends to any export a run produces.

## Prototype directions

Future directions for the AI-RiverWare integration are discussed briefly below.

1. **Natural-language Q&A over a loaded model.** The parsers answer
   structural questions ("what fires after the flood-control rule?")
   without running anything. A conversational layer over the digest — the
   explain skill made interactive — is mostly prompt engineering on what
   already exists.
2. **AI-assisted calibration.** The MCP loop already sets inputs and reads
   outputs; calibration is that loop plus a target dataset and a search
   strategy the agent can reason about between runs (adjust, run, compare
   residuals, explain what it tried).
3. **Automated run-report narration.** After each run, generate a
   plain-language report: what the policy did, which rules fired unusually
   often, where shortages landed. The explain skill's narrative discipline
   applied to results instead of structure.
4. **Deeper RiverWare-native hooks.** Everything above treats RiverWare as
   a black box at the file/batch boundary. The natural next step for the
   platform itself would be a first-class scripting or remote procedure call (RPC) surface — the
   ability to query slots and invoke runs in-process, which would replace
   file-based DMI staging with direct calls and make the MCP server's tools
   near-instant.

## Considerations

- **Licensing.** RiverWare is a licensed desktop application, and a license is required to run RiverWare with these tools.
- **Validation.** AI-drafted RPL and AI-run experiments are drafts. RiverWare's load-time checks and modelers' are still needed to ensure accuracy and quality.
- **Format drift.** The parsers here are verified against RiverWare 9.4–9.7 files. New format versions may need parser updates.
