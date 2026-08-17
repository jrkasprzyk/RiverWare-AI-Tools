# riverware-help — worked session (DMI control file)

Produced with [riverware-help](../../skills/riverware-help/SKILL.md) against
the [TwoResOps](../TwoResOps/) model. The help content below was fetched from
the live CADSWES help (CurrentVersion); the model facts come from the digest
driver. The question is constructed for the example.

---

**Question.** My model has an input DMI called `to_rw` that is supposed to
load the gage inflows before a run. What does each line of its control file
need to look like, and can I avoid writing one line per slot?

---

**Answer.**

Per the
[Control File Executable DMI reference](https://www.riverware.org/HelpSystem/CurrentVersion/DMI/DMI_ControlExecutable.3.3.html)
(CurrentVersion help), each control file line is:

```
object.slot: file=name keyword=value keyword=value ...
```

The `file=` keyword "indicates from which data files the object.slots will be
imported or to which data files the objects.slots will be exported." The
filename may embed replacement directives, expanded per slot at DMI time:

| Directive | Replaced with |
|---|---|
| `%o` | the object name |
| `%s` | the slot name |
| `%t` | the current MRM trace number |
| `%tempdir` | a guaranteed unique temporary directory |

Names containing spaces must be "enclosed in double quotation marks" — that
applies on both sides of the line, the `object.slot` and a `file="file name"`.

**In your model** (from
`python skills/explain-riverware-model/explain.py examples/TwoResOps/saratoga_v2.4.mdl`):
`to_rw` is an input exec DMI, and the inflow gages are `Sara.Gage Inflow` and
`Toga.Gage Inflow` — both names are short, but `Gage Inflow` has a space, so
the slot side needs quotes. One line per gage:

```
Sara."Gage Inflow": file=data/%o_inflow.txt
Toga."Gage Inflow": file=data/%o_inflow.txt
```

Note the two lines are identical except the object — which is the answer to
your second question. The help defines wildcard object specifications: `*`
"matches all objects of all types," and forms like `*.<slot type>` are "the
least exact specification," with a specific `object.slot` line taking
precedence over a wildcard line that matches the same slot. So a single

```
*."Gage Inflow": file=data/%o_inflow.txt
```

covers Sara and Toga — **but in this model it also matches the
`Wildlife Sanctuary` stream gage**, whose `Gage Inflow` is computed by the
simulation, not imported. Either keep the two explicit lines, or use the
wildcard plus the precedence rule to pin the exception. For a 12-object model
the explicit lines are easier to audit; wildcards earn their keep on models
with dozens of gages.

If you next want the run automated around this DMI (batch mode, MRM traces
via `%t`), that is in the help's Automation Tools section — ask and it can be
walked through the same way.

---

## What this demonstrates

| Skill behavior | Where it shows up |
|---|---|
| Learned topic map skips the section hop | `references/topic-map.md` already held the verified control-file page URL |
| Cite the page, quote the semantics | Line format, `file=` sentence, and %-directives quoted from one URL |
| Model evidence beats general knowledge | The wildcard trap — `Wildlife Sanctuary` also matching `*."Gage Inflow"` — is a model fact from the digest |
| Match the depth of the question | A syntax question gets syntax plus the one model-specific hazard, not a DMI treatise |
