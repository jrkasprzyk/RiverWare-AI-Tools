"""Pure functions for the RiverWare batch-mode exchange.

Everything here is side-effect free (no subprocess, no filesystem writes) so it
can be unit-tested without a RiverWare installation. The thin executor that
actually launches RiverWare lives in server.py.

The exchange contract (RiverWare exec DMIs, "control file" style):

- An input DMI reads a control file whose lines map slots to data files:
      Cedar.Diversion Min Elevation: file="BorgToRiverWareData/Cedar.Diversion_Min_Elevation.txt"
  Table columns append the column name: `Cedar.Pool Elevation Limits.New: ...`
- Input data files are bare numbers, one per line (one line for a scalar,
  several for a table column).
- An output DMI writes one file per slot with a small header:
      units: MWH
      scale: 1.000000
      # Scalar Slot: System Data.Total Energy Neg [1 MWH]
      -12511616.89
- The run itself is driven by an RCL script:
      OpenWorkspace {model.mdl}
      InvokeDMI {input DMI name}
      StartController
      InvokeDMI {output DMI name}
      CloseWorkspace
"""
from __future__ import annotations


def slot_filename(slot: str) -> str:
    """Canonical data filename for a slot: spaces become underscores."""
    return slot.replace(" ", "_") + ".txt"


def build_rcl_script(model_path: str, input_dmi: str | None,
                     output_dmi: str | None) -> str:
    """RCL batch script: open, import inputs, run, export outputs, close."""
    lines = [f"OpenWorkspace {{{model_path}}}"]
    if input_dmi:
        lines.append(f"InvokeDMI {{{input_dmi}}}")
    lines.append("StartController")
    if output_dmi:
        lines.append(f"InvokeDMI {{{output_dmi}}}")
    lines.append("CloseWorkspace")
    return "\n".join(lines) + "\n"


def build_dmi_input(assignments: dict[str, float | list[float]],
                    data_dir: str = "BorgToRiverWareData"
                    ) -> tuple[str, dict[str, str]]:
    """Input control file + data files for a set of slot assignments.

    Returns (control_file_text, {relative_path: file_content}). A scalar value
    produces a one-line data file; a list produces one line per value (table
    column rows in order).
    """
    control_lines = []
    files: dict[str, str] = {}
    for slot, value in assignments.items():
        rel = f"{data_dir}/{slot_filename(slot)}"
        control_lines.append(f'{slot}: file="{rel}"')
        values = value if isinstance(value, (list, tuple)) else [value]
        files[rel] = "\n".join(f"{float(v):.6f}" for v in values) + "\n"
    return "\n".join(control_lines) + "\n", files


def build_output_control(slot_names: list[str],
                         data_dir: str = "RiverWareToBorgData") -> str:
    """Output control file mapping each requested slot to its export file."""
    lines = [f'{slot}: file="{data_dir}/{slot_filename(slot)}"'
             for slot in slot_names]
    return "\n".join(lines) + "\n"


def parse_slot_export(text: str) -> dict:
    """Parse a RiverWare data-file export into {units, scale, comment, values}.

    Header lines are `key: value` pairs; `#` lines are comments; everything
    else is one numeric value per line. Non-numeric stray lines are ignored.

    `values` are the numbers exactly as exported. The header's `scale` is
    reported, never applied — callers that care must decide what to do with it.
    Every export observed so far carries `scale: 1.000000`; server.py flags any
    other value rather than guessing which direction it multiplies.
    """
    out: dict = {"units": None, "scale": 1.0, "comment": "", "values": []}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            out["comment"] = (out["comment"] + " " + line.lstrip("# ")).strip()
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key, val = key.strip().lower(), val.strip()
            if key == "units":
                out["units"] = val
                continue
            if key == "scale":
                try:
                    out["scale"] = float(val)
                except ValueError:
                    pass
                continue
            # date headers (start_date etc.) fall through and are ignored
            if not _is_number(val.split()[0] if val else ""):
                continue
        if _is_number(line.split()[0]):
            out["values"].append(float(line.split()[0]))
    return out


def _is_number(tok: str) -> bool:
    try:
        float(tok)
        return True
    except ValueError:
        return False
