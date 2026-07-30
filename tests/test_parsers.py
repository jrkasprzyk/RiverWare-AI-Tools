"""Parser regression tests against both committed example models (TEST-001..003).

Run from the repo root:  python -m unittest discover -s tests
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXPLAIN = REPO / "skills" / "explain-riverware-model" / "explain.py"
DIGEST = REPO / "skills" / "visualize-riverware-model" / "digest_to_json.py"
MODELS = {
    "ArborBasin": REPO / "examples" / "ArborBasin" / "ArborBasin.mdl",
    "saratoga": REPO / "examples" / "TwoResOps" / "saratoga_v2.4.mdl",
}


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *map(str, args)],
                          capture_output=True, text=True, cwd=str(REPO))


class TestExplain(unittest.TestCase):
    def test_both_models_digest(self):
        for name, model in MODELS.items():
            with self.subTest(model=name):
                proc = run_script(EXPLAIN, model)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("Simulation objects:", proc.stdout)
                count = int(proc.stdout.split("Simulation objects:")[1]
                            .splitlines()[0])
                self.assertGreater(count, 0)
                self.assertIn("Embedded RPL sets", proc.stdout)

    def test_stdout_ascii(self):
        for name, model in MODELS.items():
            with self.subTest(model=name):
                proc = run_script(EXPLAIN, model)
                proc.stdout.encode("ascii")  # raises on non-ASCII (CON-003)


class TestAnnotationInventory(unittest.TestCase):
    """--annotations feeds the annotate skill's propose step (REQ-005)."""

    def test_inventory_renders_for_both_models(self):
        for name, model in MODELS.items():
            with self.subTest(model=name):
                proc = run_script(EXPLAIN, model, "--annotations")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("# ANNOTATION INVENTORY", proc.stdout)
                self.assertIn("empty (candidates):", proc.stdout)
                proc.stdout.encode("ascii")

    def test_existing_descriptions_are_marked_taken(self):
        """The owner's hand-written saratoga descriptions must show up as [x]."""
        proc = run_script(EXPLAIN, MODELS["saratoga"], "--annotations")
        self.assertIn("[x] object: Cora is the upstream Storage Reservoir",
                      proc.stdout)
        self.assertIn("[x] Cora.Shortage Table: Pool Elevation determines",
                      proc.stdout)
        self.assertIn('[x] RULE "Find Shortage Level": This sets the Shortage '
                      'Fraction[] variable only', proc.stdout)
        self.assertIn("[x] Saratoga is a two-reservoir river basin", proc.stdout)

    def test_embedded_rpl_tree_is_parsed_from_the_mdl(self):
        proc = run_script(EXPLAIN, MODELS["saratoga"], "--json")
        d = json.loads(proc.stdout)["model"]
        names = {s["name"] for s in d["embedded_rpl"]}
        self.assertIn("RPL Set", names)
        rules = [it["name"] for s in d["embedded_rpl"] for g in s["groups"]
                 for it in g["items"]]
        # the same rule name lives in two groups -- the reason targets are paths
        self.assertEqual(rules.count("Prevent Overtopping"), 2)

    def test_annotations_rejected_for_rls(self):
        """A .rls has no object/slot surfaces; annotate it in the RPL editor."""
        with tempfile.TemporaryDirectory() as tmp:
            rls = Path(tmp) / "mini.rls"
            rls.write_text('RULESET\nNAME "Mini";\nDESCRIPTION "";\nBEGIN\nEND\n',
                           encoding="utf-8")
            proc = run_script(EXPLAIN, rls, "--annotations")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("applies to .mdl files", proc.stderr)


class TestDigestToJson(unittest.TestCase):
    def test_json_structure(self):
        for name, model in MODELS.items():
            with self.subTest(model=name):
                proc = run_script(DIGEST, model)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                d = json.loads(proc.stdout)
                self.assertTrue(d["objects"])
                self.assertTrue(d["links"])
                for o in d["objects"]:
                    self.assertIn("name", o)
                    self.assertIn("type", o)

    def test_arborbasin_has_curated_series(self):
        proc = run_script(DIGEST, MODELS["ArborBasin"])
        d = json.loads(proc.stdout)
        self.assertGreaterEqual(len(d["series"]), 1)
        slots = {s["slot"] for s in d["series"]}
        self.assertTrue(slots <= {"Pool Elevation", "Outflow", "Storage"})

    def test_json_ascii(self):
        proc = run_script(DIGEST, MODELS["saratoga"])
        proc.stdout.encode("ascii")


if __name__ == "__main__":
    unittest.main()
