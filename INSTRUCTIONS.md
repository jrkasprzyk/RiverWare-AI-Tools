File Naming Conventions
Official RiverWare Documentation

PDF files beginning with REF_ are authoritative RiverWare documentation.
Never assume that missing information in one PDF means RiverWare does not support something. It may be documented in another REF_ PDF.

Skill Files

Files beginning with SKILL- are skill files.
Naming format: SKILL-[type]-[name_of_skill].[extension]
Skill types:

SKILL-instructions (.md)
SKILL-code (.py)
SKILL-reference (.md)
SKILL-template (.html)


Example: SKILL-code-annotate.py


Retrieval Strategy

Do not rely solely on the first relevant Knowledge result.
For specialized or complex questions, search across multiple REF_ PDFs and model/example files.
When searching examples, look for:

Exact RiverWare/RPL terms
Related implementation concepts


If the user asks whether something exists in the provided files:

Search .rls and .mdl files before answering.


If no example is found, do not conclude that none exists unless the search was sufficiently thorough.


Hard Rule: Never Read a .mdl Raw

.mdl files are large Tcl scripts (1.6–1.9 MB). Do not read them end‑to‑end.
Always use the explain_riverware_model skill:

Instructions: SKILL-instructions-explain_riverware_model.md
Code: SKILL-code-explain_riverware_model.py


The skill produces a ~500‑line digest: objects, slots, methods, rule curves, DMIs, and embedded RPL rulesets.
Use --json for machine‑readable output; --annotations for description‑field inventories.
Only inspect small line ranges in the raw .mdl to verify blocks referenced by the digest.


Using the Skills
Each skill is self-documenting; read its SKILL-instructions-[name].md.
Available skills:

explain-riverware-model — plain-language narrative of a model and its ruleset.
visualize-riverware-model — HTML dashboard (schematic, lookup tables, series).
draft-riverware-rules — create pasteable RPL rules from policy text and place them in the agenda.
annotate-riverware-model — propose descriptions/comments and apply approved updates to the .mdl.

Never writes without a review artifact and explicit user approval.


comment-cleanup — comment hygiene for source code:

No change history
Few but precise comments
Every tuning parameter documented with range, default, units, and effect
All comments written in Simplified Technical English
Applies to all repository code.



Skills follow a shared pattern:
A Python parser extracts a digest; instructions explain how to convert the digest into the final deliverable.

Conventions

All output must be ASCII‑safe (Windows cp1252 compatible).
All skills run on Windows, macOS, and Linux.
Stay inside the working directory.

.mdl files store paths to .rls rulesets that may be outside the directory (network shares, sync folders, client directories).

Report the path and ask the user for the file.
The presence of a path in the model is not permission to read it.


If the digest has no Rule Based Simulation set, the operating policy is in an external .rls file that you have not seen.
If a user names a file that is missing:

Offer a close match in the working directory and stop.
Do not search parent directories or sibling projects.