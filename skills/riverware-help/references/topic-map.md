# Learned topic map

Verified topic-page URLs, accumulated across help sessions so common lookups
skip the section-index hop. All URLs relative to
`https://www.riverware.org/HelpSystem/CurrentVersion/`.

Rules for adding entries (see SKILL.md):

- Only URLs actually fetched and confirmed to contain the topic.
- Entries are **generic help pointers**: topic name + what the page covers.
  Never record who asked, why, or any model/project/tool context from the
  conversation that surfaced the topic.
- One line per page. If an anchor was verified, include it; otherwise page URL
  alone is fine.

| Topic | Page | Covers |
|---|---|---|
| MRM configuration — Input tab | `SolutionApproaches/Solutions_MRM.4.06.html` | Input modes (None, Traces, Index Sequential incl. Pairs mode, Select Years), Initialization/Input DMIs; anchors: Index Sequential `#ww518170`, Pairs `#ww573164` |
| About Multiple Runs | `SolutionApproaches/Solutions_MRM.4.02.html` | MRM concepts overview |
| Control File Executable DMI — control file syntax | `DMI/DMI_ControlExecutable.3.3.html` | Line format `object.slot: file=... keyword=value`, object/slot/wildcard specs `#ww1031294`, file-name %-directives (%o %s %t %tempdir) `#ww999973`, keyword reference |
| About the Trace Directory DMI | `DMI/DMI_TraceDirectory.4.2.html` | Trace-numbered subdirectory layout (`trace1/`, ...), auto-generated per-slot filenames, no executable |
| Trace Directory DMI Editor dialog | `DMI/DMI_TraceDirectory.4.3.html` | Dialog reference |
| RPL Palette — slot subscript forms | `RPL/RPLTypesPalette.4.3.html` | Valid bracket indices per slot type: series `[datetime]` or `[]`; table `[row, col]` zero-based numeric or label string; aggregate/periodic `[date, col]` |
| Types of Slots | `UI/UI_SlotDialogs.08.05.html` | All slot types w/ anchors: Table Series Slot `#ww1072573` (method-internal only — cannot be created as custom slot), Periodic `#ww1072580`, Table `#ww1071921`, Series `#ww1070932` |
| Slot Priorities and Flags (RBS) | `SolutionApproaches/Solutions_RulebasedSimulation.3.09.html` | Rule-set values carry the rule's priority; R flag; priority 0 = user input, never overwritten; rules get integers > 0 (smaller = higher priority) |
| Resetting Slot Values (RBS) | `SolutionApproaches/Solutions_RulebasedSimulation.3.10.html` | When a new value may overwrite an existing one, with example table (e.g. 6R←4R successful, 4R←6R unsuccessful); equal priority needs R flag on both; subsections on multi-slot and link behavior |
