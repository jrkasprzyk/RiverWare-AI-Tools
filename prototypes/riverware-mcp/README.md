# RiverWare MCP server (prototype)

> **Experimental — requires a licensed local RiverWare installation.**
> This is a working prototype demonstrating live AI ↔ RiverWare control, not a
> supported product. Verified against **RiverWare 9.7** on Windows
> (2026-07-28): two batch runs with different decision-slot values completed
> with exit code 0 and returned different objective values.

An [MCP](https://modelcontextprotocol.io) server that gives an AI agent
read + run + write control of a RiverWare model through batch mode. The loop
it enables:

1. **`set_slots`** — stage decision-slot values as DMI input files
2. **`run_model`** — execute the model headless (RCL script + `RiverWare.exe --batch`)
3. **`read_slots`** — read the exported result slots
4. repeat with different inputs and compare

Plus **`list_objects`** / **`list_slots`**, served from the repository's
`.mdl` parser, so the agent can discover what it is allowed to touch.

See [demo_transcript.md](demo_transcript.md) for a real set → run → read
sequence against the Arbor Basin example model.

## Setup

```bash
pip install -r requirements.txt   # the MCP Python SDK
```

Configure via `config.json` next to `server.py` (all keys optional; shown
with their defaults targeting `examples/ArborBasin/ArborBasin.mdl`):

```json
{
  "riverware_exe": "/path/to/your/RiverWare.exe",
  "model_path": "../../examples/ArborBasin/ArborBasin.mdl",
  "workdir": "./mcp_runs",
  "env_var": "BORG_ARBOR_BASIN_DEMO",
  "input_dmi": "From Borg-RiverWare",
  "output_dmi": "To Borg-RiverWare Single Run",
  "input_control_file": "FromBorgRiverWare.txt",
  "output_control_file": "ToBorgRiverWareSingleRun.txt"
}
```

`riverware_exe` can also come from the `RIVERWARE_EXE` environment variable.
On Windows it is `RiverWare.exe` inside your versioned install folder (by
default under the CADSWES directory on the system drive). `config.json` is
git-ignored, so machine paths stay local.

Register with Claude Code by adding to the project's `.mcp.json`:

```json
{
  "mcpServers": {
    "riverware": {
      "command": "python",
      "args": ["prototypes/riverware-mcp/server.py"]
    }
  }
}
```

## How the exchange works

The contract is defined by the **model's own DMIs**, not by this server:

- The model's input exec DMI reads a control file
  (`Object.Slot: file="..."` lines) resolved against an environment variable;
  the server writes that control file and its bare-number data files into the
  working directory and points the variable there.
- `StartController` runs the model; the output exec DMI then writes one
  export file per slot (`units:` / `scale:` header, then values).
- The driving RCL script is five lines: `OpenWorkspace`, `InvokeDMI` (input),
  `StartController`, `InvokeDMI` (output), `CloseWorkspace`.

To use the server with a different model, configure that model's DMI names,
control filenames, and environment variable. If a model has no DMIs, add an
input and output exec DMI in RiverWare first — that is the integration
surface batch mode offers today.

## Layout and testing

| File | Role |
|------|------|
| `server.py` | MCP tools + the thin executor that launches RiverWare |
| `rw_batch.py` | Pure functions: `build_rcl_script`, `build_dmi_input`, `build_output_control`, `parse_slot_export` — no subprocess, no filesystem |
| `tests/test_pure.py` | Unit tests for the pure functions against fixture files; run without RiverWare: `python -m unittest discover -s tests` |

RiverWare cannot run in CI (licensed desktop application), so CI covers only
the pure functions; the live loop is verified manually as described above.

## Known limitations

- One run at a time per working directory; no run queueing.
- `set_slots` stages inputs for the *next* run only — there is no readback of
  a staged value from the model before running.
- Output slots are fixed by configuration per run (the output control file is
  regenerated from `output_slots` each `run_model`).
- Error reporting is the batch log tail; RiverWare's own diagnostics are the
  authority on why a run failed (including deliberate policy aborts such as
  Arbor Basin's `Cause Sporadic Error` rule when
  `Cedar.Diversion Min Elevation` < 220).
