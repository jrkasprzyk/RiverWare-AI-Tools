"""Unit tests for the pure batch-exchange functions (no RiverWare needed)."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rw_batch

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestBuildRclScript(unittest.TestCase):
    def test_full_loop(self):
        rcl = rw_batch.build_rcl_script("models/ArborBasin.mdl",
                                        "From Borg-RiverWare",
                                        "To Borg-RiverWare Single Run")
        self.assertEqual(rcl.splitlines(), [
            "OpenWorkspace {models/ArborBasin.mdl}",
            "InvokeDMI {From Borg-RiverWare}",
            "StartController",
            "InvokeDMI {To Borg-RiverWare Single Run}",
            "CloseWorkspace",
        ])

    def test_run_only(self):
        rcl = rw_batch.build_rcl_script("m.mdl", None, None)
        self.assertNotIn("InvokeDMI", rcl)
        self.assertIn("StartController", rcl)


class TestBuildDmiInput(unittest.TestCase):
    def test_scalar_and_table(self):
        control, files = rw_batch.build_dmi_input({
            "Cedar.Diversion Min Elevation": 226.1,
            "Cedar.Pool Elevation Limits.New": [201.0, 212.0],
        })
        self.assertIn('Cedar.Diversion Min Elevation: '
                      'file="BorgToRiverWareData/'
                      'Cedar.Diversion_Min_Elevation.txt"', control)
        self.assertEqual(
            files["BorgToRiverWareData/Cedar.Diversion_Min_Elevation.txt"],
            "226.100000\n")
        self.assertEqual(
            files["BorgToRiverWareData/Cedar.Pool_Elevation_Limits.New.txt"],
            "201.000000\n212.000000\n")

    def test_output_control(self):
        control = rw_batch.build_output_control(["System Data.Total Spill Volume"])
        self.assertEqual(control,
                         'System Data.Total Spill Volume: '
                         'file="RiverWareToBorgData/'
                         'System_Data.Total_Spill_Volume.txt"\n')


class TestParseSlotExport(unittest.TestCase):
    def test_scalar_fixture(self):
        parsed = rw_batch.parse_slot_export(
            (FIXTURES / "scalar_export.txt").read_text())
        self.assertEqual(parsed["units"], "MWH")
        self.assertEqual(parsed["scale"], 1.0)
        self.assertIn("Total Energy Neg", parsed["comment"])
        self.assertEqual(parsed["values"], [-12511616.89])

    def test_series_fixture(self):
        parsed = rw_batch.parse_slot_export(
            (FIXTURES / "series_export.txt").read_text())
        self.assertEqual(parsed["units"], "cms")
        self.assertEqual(len(parsed["values"]), 5)
        self.assertEqual(parsed["values"][0], 120.50)
        self.assertTrue(math.isnan(parsed["values"][2]))

    def test_roundtrip(self):
        # what build_dmi_input writes, parse_slot_export can read back
        _, files = rw_batch.build_dmi_input({"A.B": 42.5})
        parsed = rw_batch.parse_slot_export(files["BorgToRiverWareData/A.B.txt"])
        self.assertEqual(parsed["values"], [42.5])


if __name__ == "__main__":
    unittest.main()
