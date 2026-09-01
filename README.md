# RiverWare-AI-Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status: Early Development](https://img.shields.io/badge/status-early%20development-orange)

> **An exploratory demonstration of how AI tools can interface with [RiverWare](https://riverware.org/).**

RiverWare-AI-Tools is an experimental repository created by **Joseph Kasprzyk** to demonstrate how AI tools can support RiverWare modeling workflows.

This project is **not included in or officially supported as part of CADSWES software** and is intended for demonstration and experimentation.

## Custom ChatGPT Branch

The [`custom_chatGPT`](https://github.com/jrkasprzyk/RiverWare-AI-Tools/tree/custom_chatGPT)
branch reorganizes the skills file structure from the main branch into flat files 
that is well suited for use as knowledge files in a custom GPT.

The instructions below describe how to use this branch to create a RiverWare-focused custom GPT.

---

# Setting Up a Custom RiverWare GPT

## 1. Download the Required Files

You will need:

* [ ] `Description.md`
* [ ] The entire `skills` folder
* [ ] The entire `RWdocs` folder

You can download these files directly from GitHub, or clone the `custom_chatGPT` branch.

### Clone the Repository

To clone only the `custom_chatGPT` branch:

```bash
git clone --branch custom_chatGPT --single-branch https://github.com/jrkasprzyk/RiverWare-AI-Tools.git
```

Then enter the repository:

```bash
cd RiverWare-AI-Tools
```

Alternatively, browse the branch directly on GitHub:

**[RiverWare-AI-Tools — `custom_chatGPT` branch](https://github.com/jrkasprzyk/RiverWare-AI-Tools/tree/custom_chatGPT)**

---

## 2. Create a Custom GPT

Navigate to **[ChatGPT GPTs](https://chatgpt.com/gpts)** and select **Create**.

> **Note:** Availability of custom GPT creation depends on your ChatGPT plan and your organization's workspace and administrator settings.

---

## 3. Enter a Name and Description

Choose a name that identifies the version of RiverWare documentation included in the GPT's knowledge.

For example:

**Name**

`RiverWare X.X.X Helper Bot`

Replace `X.X.X` with the RiverWare version corresponding to the documentation you upload.

**Description**

`A custom GPT with knowledge of RiverWare documentation and skills for working with RiverWare model and ruleset files.`

---

## 4. Add the GPT Instructions

Open [`INSTRUCTIONS.md`](INSTRUCTIONS.md) and copy its entire contents into the custom GPT's **Instructions** field.

---

## 5. Add Conversation Starters

Suggested conversation starters include:

* **Tell me about the RiverWare skills you have and how to use them.**
* **Help me annotate my model and ruleset.**
* **Help me write RPL for a task I need to accomplish. Ask me for the details you need.**
* **Help me debug a problem in my RiverWare model or ruleset.**
* **Find the major functions and slots that a function depends on.**

---

## 6. Upload Knowledge Files

Upload the following files as knowledge for your custom GPT:

1. All relevant files from the `RWdocs` folder, except `ReadMe.txt`.
2. All files from the `skills` folder.

### Knowledge File Limits

ChatGPT may limit the number or size of files that can be uploaded as knowledge. If you encounter a limit, you can omit documentation that is not relevant to your intended use case.

For example, depending on your needs, you might omit:

* `REF_Optimization.pdf`
* `REF_Accounting.pdf`
* `REF_AutomationTools.pdf`
* `REF_WaterQuality.pdf`
* `REF_RiverWISE_Stakeholder.pdf`
* `REF_RiverWISE_Developer.pdf`

You can also omit skills that are not relevant to your intended workflow.

If your organization permits **Web Search**, another approach is to provide the RiverWare documentation website in the GPT instructions and use uploaded knowledge primarily for repository-specific skills and information.

---

## 7. Enable Capabilities

Under **Capabilities**, enable:

* **Code Interpreter & Data Analysis**

Depending on your organization's settings and your intended use case, you may also enable:

* **Web Search**
* **Apps**

---

## 8. Create the GPT

When configuration is complete, select **Create**.

Your custom RiverWare GPT is now ready to test.

---

## 9. Share Your Custom GPT (Optional)

To share the GPT:

1. Navigate to **[My GPTs](https://chatgpt.com/gpts/mine)**.
2. Open the GPT you created.
3. Open the menu associated with the GPT's name.
4. Select the option to copy or share its link.
5. Follow the displayed sharing options for your workspace.

Sharing options may depend on your ChatGPT plan and your organization's administrator settings.

---

# Using the Skills

Once your custom GPT is configured, try giving it a RiverWare model and asking:

> Explain the model in `examples/ArborBasin/ArborBasin.mdl`

You can also use the individual skills described below.

## Skills

| Skill                                                                               | What it does                                                                                                                                                                              | Status    |
| ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| [explain-riverware-model](skills/SKILL-instructions-explain_riverware_model.md)     | Parses a `.mdl`/`.rls` file and writes a narrative explanation of the model                                                                                                               | Available |
| [visualize-riverware-model](skills/SKILL-instructions-visualize_riverware_model.md) | Renders model structure and key series as a self-contained HTML dashboard                                                                                                                 | Available |
| [draft-riverware-rules](skills/SKILL-instructions-draft_riverware_rules.md)         | Drafts a pasteable RPL rule from a plain-language policy request                                                                                                                          | Available |
| [annotate-riverware-model](skills/SKILL-instructions-annotate.md)                   | Proposes descriptions and RPL comments for a model, then applies the approved set to the `.mdl`                                                                                           | Available |
| [comment-cleanup](skills/SKILL-instructions-comment_cleanup.md)                     | Removes changelog-style and repeated comments from AI-written code, documents tuning parameters with ranges, defaults, and units, and rewrites the result in Simplified Technical English | Available |

---

# Examples

## Example Models

| Model                              | Description                                  | Outputs                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [ArborBasin](examples/ArborBasin/) | The CADSWES RiverWare training model         | [Narrative](examples/ArborBasin/ArborBasin_explained.md) · [Live dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/ArborBasin/ArborBasin_dashboard.html) · [Rule case study](examples/ArborBasin/ArborBasin_rule_case_study.md) · [Annotation review](examples/ArborBasin/ArborBasin_annotations.md)         |
| [TwoResOps](examples/TwoResOps/)   | Saratoga, a two-reservoir operations testbed | [Narrative](examples/TwoResOps/saratoga_v2.4_explained.md) · [Live dashboard](https://jrkasprzyk.github.io/RiverWare-AI-Tools/examples/TwoResOps/saratoga_v2.4_dashboard.html) · [Rule case study](examples/TwoResOps/saratoga_v2.4_rule_case_study.md) · [Annotation review](examples/TwoResOps/saratoga_v2.4_annotations.md) |

## Worked Sessions

Worked sessions in [`examples/sessions/`](examples/sessions/) demonstrate skills that answer questions, draft content, or rewrite material rather than produce a per-model artifact.

| Session                                                                                                                                                                      | Skill                   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| [Elevation lookup in a rule](examples/sessions/riverware-help_elevation-lookup.md) — a cited help answer checked against Saratoga's own objects                              | `riverware-help`        |
| [Why is my rule overwritten?](examples/sessions/riverware-help_rule-overwrite.md) — rule priorities and the R flag, mapped onto a real agenda                                | `riverware-help`        |
| [DMI control-file syntax](examples/sessions/riverware-help_dmi-control-file.md) — line format and `%` directives, plus a model-specific wildcard trap                        | `riverware-help`        |
| [Minimum-flow rule, request to draft](examples/sessions/draft-riverware-rules_roberto-min-flow.md) — a drafting conversation, including the refusal to invent a missing slot | `draft-riverware-rules` |
| [Comment cleanup, before and after](examples/sessions/comment-cleanup_before-after.md) — history comments out, tuning ranges and units in                                    | `comment-cleanup`       |
| [Report cleanup, before and after](examples/sessions/report-cleanup_before-after.md) — one rambling paragraph reorganized into Summary, Repro, Hypothesis, and Asks          | `report-cleanup`        |

### Presenting the Repository?

See [`docs/user-group-demo-script.md`](docs/user-group-demo-script.md) for a reproducible run-of-show demonstrating the four model-facing skills.

All examples are also available through the:

**[RiverWare-AI-Tools GitHub Pages site](https://jrkasprzyk.github.io/RiverWare-AI-Tools/)**

Committed example outputs are produced using these skills and then human-polished into finished documentation.

---

# Live-Model Control: MCP Prototype

The [`prototypes/riverware-mcp/`](prototypes/riverware-mcp/) directory contains an experimental **Model Context Protocol (MCP)** server that wraps RiverWare batch mode.

It currently provides tools for:

* `list_objects` — list model objects
* `list_slots` — list available slots
* `set_slots` — modify slot values
* `run_model` — execute the model
* `read_slots` — retrieve model results

Together, these tools allow an AI agent to:

1. Inspect a RiverWare model.
2. Modify model inputs.
3. Run the model.
4. Retrieve results.
5. Compare outcomes from different scenarios or policies.

Initial verification was completed using **RiverWare 9.7**.

See the [MCP demo transcript](prototypes/riverware-mcp/demo_transcript.md) for an example **set → run → read** policy experiment.

> **Note:** A valid RiverWare license is required to run RiverWare using these tools.

---

# Upcoming Work

* [ ] Create a verified GitHub Copilot walkthrough.
* [ ] Edit example model descriptions and fine-tune skills.
* [ ] Verify that annotated example models load cleanly in RiverWare.
* [ ] Widen `COMMENTED_BY` targeting beyond numeric literals.
* [ ] Encode quotes in RPL description text as `&quot;` rather than rejecting them.

---

# Contributing

Contributions are welcome, including:

* New RiverWare examples
* Improvements to existing skills
* New skills
* Documentation improvements
* New AI/RiverWare integration tools

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

# License

RiverWare-AI-Tools is licensed under the [MIT License](LICENSE).
