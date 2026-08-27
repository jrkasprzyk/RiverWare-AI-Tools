# AI ↔ RiverWare integration: directions

The [README](../README.md) covers what the tools in this repository do
today. This document covers the other half: why the integration works at
all, where it can go next, and the constraints that apply to all of it.

## Why the integration works

RiverWare's `.mdl` and `.rls` files are text — the modelfile uses the same
format as a Tcl script, and RiverWare Policy Language (RPL) rules and
functions are either embedded in it or stored in a separate `.rls` file.
The files are too large for an AI agent to read raw (1.6–1.9 MB for the
models here), but small parsers extract everything an agent needs: objects,
slots, selected simulation methods, lookup tables, link topology, DMIs,
embedded rulesets, and stored results. Once parsed into a digest, a capable
agent reasons about model structure fluently, and every skill in this
repository is grounded in that digest rather than in the agent's
recollection of RiverWare.

Two more surfaces complete the picture:

- **Batch mode.** RCL scripts plus DMIs let automated tools set inputs, run
  the model, and read results — the surface the
  [riverware-mcp prototype](../prototypes/riverware-mcp/) wraps in model
  context protocol (MCP) tools. The same DMI structure is used in
  **Borg-RiverWare** for multi-objective optimization.
- **Documentation.** The public CADSWES online help is fetchable page by
  page, which lets the riverware-help skill quote and cite it instead of
  paraphrasing from memory.

## Prototype directions

1. **Natural-language Q&A over a loaded model.** The parsers answer
   structural questions ("what fires after the flood-control rule?")
   without running anything. The riverware-help skill already does the
   documentation half — cited help answers checked against the model
   digest; a conversational layer over the full structural digest is
   mostly prompt engineering on what already exists.
2. **AI-assisted calibration.** The MCP loop already sets inputs and reads
   outputs; calibration is that loop plus a target dataset and a search
   strategy the agent can reason about between runs (adjust, run, compare
   residuals, explain what it tried).
3. **Automated run-report narration.** After each run, generate a
   plain-language report: what the policy did, which rules fired unusually
   often, where shortages landed. The explain skill's narrative discipline
   applied to results instead of structure.
4. **Round-trip model documentation.** The annotate skill writes reviewed
   descriptions and RPL comments back into the `.mdl`. Extended, this
   becomes a documentation workflow: models that stay explained as they
   change, with the narrative regenerated from the file after each edit.
5. **Deeper RiverWare-native hooks.** Everything above treats RiverWare as
   a black box at the file/batch boundary. The natural next step for the
   platform itself would be a first-class scripting or remote procedure
   call (RPC) surface — the ability to query slots and invoke runs
   in-process, which would replace file-based DMI staging with direct
   calls and make the MCP server's tools near-instant.

## Considerations

- **Licensing.** RiverWare is a licensed desktop application, and a
  license is required to run RiverWare with these tools. Reading and
  drafting from model files requires no license.
- **Validation.** AI-drafted RPL and AI-run experiments are drafts.
  RiverWare's load-time checks and the modeler's review are still needed
  to ensure accuracy and quality.
- **Format drift.** The parsers here are verified against RiverWare
  9.4–9.7 files. New format versions may need parser updates.
