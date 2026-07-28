"""RiverWare MCP server prototype.

Gives an AI agent read + run + write control of a local RiverWare
installation through batch mode:

    list_objects / list_slots  -- structural digest of the configured model
    set_slots                  -- stage decision-slot values as DMI input files
    run_model                  -- execute a batch run (RCL script + RiverWare)
    read_slots                 -- read exported slot values after a run

Configuration (config.json next to this file, overridable by environment
variables of the same name in upper case):

    riverware_exe        path to RiverWare.exe (env: RIVERWARE_EXE)
    model_path           the .mdl to operate on
    workdir              directory for staged inputs, outputs, RCL, and logs
    env_var              environment variable the model's DMI control files
                         resolve against (set to workdir for each run)
    input_dmi            name of the model's input exec DMI
    output_dmi           name of the model's output exec DMI
    input_control_file   control filename the input DMI reads
    output_control_file  control filename the output DMI reads
    output_slots         slots the output DMI exports (informational; the
                         control file is regenerated from this list each run)

The defaults target examples/ArborBasin/ArborBasin.mdl and its
`From Borg-RiverWare` / `To Borg-RiverWare Single Run` DMIs.

Experimental: requires a licensed local RiverWare installation. The exchange
contract (DMI names, control filenames, env var) is defined by the model —
point the config at your own model's DMIs to use it elsewhere.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

import rw_batch

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "skills" / "explain-riverware-model"))
from explain import parse_mdl  # noqa: E402

DEFAULTS = {
    "riverware_exe": "",
    "model_path": str(REPO / "examples" / "ArborBasin" / "ArborBasin.mdl"),
    "workdir": str(HERE / "mcp_runs"),
    "env_var": "BORG_ARBOR_BASIN_DEMO",
    "input_dmi": "From Borg-RiverWare",
    "output_dmi": "To Borg-RiverWare Single Run",
    "input_control_file": "FromBorgRiverWare.txt",
    "output_control_file": "ToBorgRiverWareSingleRun.txt",
    "output_slots": [
        "System Data.Total Energy Neg",
        "System Data.Total W Basin Irrig Neg",
        "System Data.Total E Basin Irrig Neg",
        "System Data.Total Depletion Shortage",
        "System Data.Total Spill Volume",
        "System Data.Total Transbasin Diversion",
    ],
}


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    cfg_file = HERE / "config.json"
    if cfg_file.exists():
        cfg.update(json.loads(cfg_file.read_text(encoding="utf-8")))
    for key in cfg:
        env = os.environ.get(key.upper())
        if env:
            cfg[key] = env
    return cfg


CFG = load_config()
mcp = FastMCP("riverware")
_digest_cache: dict | None = None


def _digest() -> dict:
    global _digest_cache
    if _digest_cache is None:
        text = Path(CFG["model_path"]).read_text(encoding="utf-8", errors="replace")
        _digest_cache = parse_mdl(text)
    return _digest_cache


@mcp.tool()
def list_objects() -> str:
    """List every simulation object in the configured model (name and type)."""
    rows = [f"{o['name']}  [{o['type']}]" for o in _digest()["objects"]]
    return "\n".join(rows)


@mcp.tool()
def list_slots(object_name: str) -> str:
    """List the slots of one simulation object (slot name and slot type)."""
    for o in _digest()["objects"]:
        if o["name"] == object_name:
            return "\n".join(f"{s['name']}  [{s['type']}]" for s in o["slots"])
    return f"error: no object named {object_name!r} in the model"


@mcp.tool()
def set_slots(assignments: dict[str, float | list[float]]) -> str:
    """Stage slot values for the next run as DMI input files.

    Keys are slot references exactly as the model's input DMI expects them
    (e.g. "Cedar.Diversion Min Elevation", table column
    "Cedar.Pool Elevation Limits.New"). A scalar takes one number; a table
    column takes a list of row values. Values take effect on the next
    run_model call.
    """
    workdir = Path(CFG["workdir"])
    control, files = rw_batch.build_dmi_input(assignments)
    for rel, content in files.items():
        target = workdir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="ascii")
    (workdir / CFG["input_control_file"]).write_text(control, encoding="ascii")
    return f"staged {len(files)} slot file(s) in {workdir}"


@mcp.tool()
def run_model() -> str:
    """Run the model in RiverWare batch mode with the staged inputs.

    Builds the RCL script, regenerates the output control file, points the
    model's DMI environment variable at the working directory, and executes
    RiverWare. Returns the exit code and the tail of the batch log.
    """
    exe = CFG["riverware_exe"]
    if not exe or not Path(exe).exists():
        return ("error: riverware_exe is not configured or does not exist. "
                "Set RIVERWARE_EXE or config.json.")
    workdir = Path(CFG["workdir"])
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "RiverWareToBorgData").mkdir(exist_ok=True)
    (workdir / CFG["output_control_file"]).write_text(
        rw_batch.build_output_control(CFG["output_slots"]), encoding="ascii")
    if not (workdir / CFG["input_control_file"]).exists():
        (workdir / CFG["input_control_file"]).write_text("", encoding="ascii")
    rcl = workdir / "run.rcl"
    rcl.write_text(rw_batch.build_rcl_script(
        str(Path(CFG["model_path"]).resolve()).replace("\\", "/"),
        CFG["input_dmi"], CFG["output_dmi"]), encoding="ascii")
    log = workdir / "batch.log"
    env = dict(os.environ)
    env[CFG["env_var"]] = str(workdir)
    proc = subprocess.run(
        [exe, "--batch", str(rcl), "--log", str(log)],
        cwd=str(workdir), env=env, capture_output=True, text=True,
        timeout=1800)
    tail = ""
    if log.exists():
        tail = "\n".join(log.read_text(encoding="utf-8",
                                       errors="replace").splitlines()[-15:])
    return f"exit code {proc.returncode}\n--- log tail ---\n{tail}"


@mcp.tool()
def read_slots(slot_names: list[str] | None = None) -> str:
    """Read exported slot values from the last run.

    With no argument, reads every configured output slot. Returns one line
    per slot: name, value(s), units.
    """
    workdir = Path(CFG["workdir"]) / "RiverWareToBorgData"
    names = slot_names or CFG["output_slots"]
    lines = []
    for slot in names:
        f = workdir / rw_batch.slot_filename(slot)
        if not f.exists():
            lines.append(f"{slot}: (no export file — has run_model succeeded?)")
            continue
        parsed = rw_batch.parse_slot_export(f.read_text(encoding="utf-8",
                                                        errors="replace"))
        vals = parsed["values"]
        shown = vals[0] if len(vals) == 1 else vals
        unit = f" {parsed['units']}" if parsed["units"] else ""
        lines.append(f"{slot}: {shown}{unit}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
