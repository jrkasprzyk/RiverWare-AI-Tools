"""Applier tests for skills/annotate-riverware-model/annotate.py (TEST-001..004).

Run from the repo root:  python -m unittest discover -s tests

These run against tests/fixtures/mini_model.mdl -- a hand-built miniature that
carries every annotation surface -- rather than the 1.6-1.9 MB example models.
The fixture is small enough to assert on byte-for-byte.

Line endings are the subtlest thing this applier has to get right, so every
test runs twice: once against an LF copy of the fixture and once against a CRLF
copy, both derived here rather than read from disk. Deriving them defeats git's
autocrlf, which would otherwise decide what the "LF variant" actually contains.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANNOTATE = REPO / "skills" / "annotate-riverware-model" / "annotate.py"
FIXTURE = REPO / "tests" / "fixtures" / "mini_model.mdl"

LF = FIXTURE.read_bytes().replace(b"\r\n", b"\n")
CRLF = LF.replace(b"\n", b"\r\n")
VARIANTS = {"lf": LF, "crlf": CRLF}


class AnnotateCase(unittest.TestCase):
    """Base: run the applier over a temp copy of the fixture and hand back the result."""

    def run_annotate(self, source: bytes, entries, *extra):
        """Returns (completed_process, output_bytes_or_None)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            model = tmp / "mini_model.mdl"
            model.write_bytes(source)
            proposals = tmp / "proposals.json"
            proposals.write_text(json.dumps(entries), encoding="utf-8")
            out = tmp / "out.mdl"
            proc = subprocess.run(
                [sys.executable, str(ANNOTATE), str(model), str(proposals),
                 "--output", str(out), *extra],
                capture_output=True, text=True, cwd=str(REPO))
            return proc, (out.read_bytes() if out.exists() else None)

    def apply_ok(self, source: bytes, entries):
        """Apply entries that are all expected to resolve; assert a clean run."""
        proc, result = self.run_annotate(source, entries)
        self.assertEqual(proc.returncode, 0,
                         f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
        self.assertIsNotNone(result)
        return proc.stdout, result.decode("utf-8")


class TestRoundTrip(AnnotateCase):
    """TEST-001: the applier must be a no-op when it has nothing to apply."""

    def test_empty_proposal_is_byte_identical(self):
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                proc, result = self.run_annotate(src, [])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(result, src)

    def test_applied_edits_leave_every_other_byte_alone(self):
        """One inserted line and one replaced line -- and nothing else moves."""
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                _, out = self.apply_ok(src, [
                    {"target_type": "object_description", "target": "Cora",
                     "text": "Upstream storage reservoir."},
                    {"target_type": "model_description", "target": "",
                     "text": "A miniature two-reservoir basin."},
                ])
                before = src.decode("utf-8").splitlines()
                after = out.splitlines()
                self.assertEqual(len(after), len(before) + 1)
                # exactly one line differs in place (the model comment) and one
                # is new (the object description)
                added = [ln for ln in after if ln not in before]
                self.assertEqual(len(added), 2)

    def test_output_newlines_match_input(self):
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                _, result = self.run_annotate(src, [
                    {"target_type": "slot_description", "target": "Cora.Inflow",
                     "text": "Gaged inflow to Cora."}])
                raw = result
                self.assertEqual(raw.count(b"\r\n"),
                                 src.count(b"\r\n") + (1 if name == "crlf" else 0))
                if name == "lf":
                    self.assertNotIn(b"\r", raw)


class TestSurfaces(AnnotateCase):
    """TEST-002: each annotation surface lands in the right place, in the right form."""

    def test_model_description(self):
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                _, out = self.apply_ok(src, [
                    {"target_type": "model_description", "target": "",
                     "text": "A miniature two-reservoir basin."}])
                self.assertIn("$ws.Model.FileInfo comment {A miniature "
                              "two-reservoir basin.}", out)
                self.assertNotIn("$ws.Model.FileInfo comment {}", out)

    def test_object_description_follows_objattributes(self):
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                _, out = self.apply_ok(src, [
                    {"target_type": "object_description", "target": "Cora",
                     "text": "Upstream storage reservoir."}])
                lines = out.splitlines()
                i = lines.index('"$o" objAttributes '
                                '{<SimObjAttributes simObjName="Cora"/>}')
                self.assertEqual(lines[i + 1],
                                 '"$o" userDescript {Upstream storage reservoir.}')

    def test_object_description_clears_a_multiline_objattributes_block(self):
        """An object with custom attributes gets a multi-line objAttributes arg;
        inserting after its opening line would land inside the XML."""
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                _, out = self.apply_ok(src, [
                    {"target_type": "object_description", "target": "Hickory",
                     "text": "East-basin storage reservoir."}])
                lines = out.splitlines()
                i = lines.index("</SimObjAttributes>}")
                self.assertEqual(lines[i + 1],
                                 '"$o" userDescript {East-basin storage reservoir.}')

    def test_slot_description_follows_uuid(self):
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                _, out = self.apply_ok(src, [
                    {"target_type": "slot_description", "target": "Cora.Inflow",
                     "text": "Gaged inflow to Cora."}])
                lines = out.splitlines()
                i = lines.index('"$s" UUID '
                                '{83d9eecd-ca0c-4db0-bf03-95c918d5cd5f}')
                self.assertEqual(lines[i + 1],
                                 '"$s" userDescript {Gaged inflow to Cora.}')

    def test_slot_description_skips_past_computedbyexpr(self):
        """RiverWare emits computedByExpr between UUID and userDescript."""
        _, out = self.apply_ok(LF, [
            {"target_type": "slot_description", "target": "Cora.Supply Reliability",
             "text": "Fraction of timesteps above the target elevation."}])
        lines = out.splitlines()
        i = next(n for n, ln in enumerate(lines) if ln.startswith('"$s" computedByExpr'))
        self.assertEqual(lines[i + 1], '"$s" userDescript {Fraction of timesteps '
                                       'above the target elevation.}')

    def test_slot_without_uuid_still_lands_inside_its_own_block(self):
        """Cora.Dead Pool has no UUID line; the `set s` line is the fallback anchor."""
        _, out = self.apply_ok(LF, [
            {"target_type": "slot_description", "target": "Cora.Dead Pool",
             "text": "Elevation below which nothing can be delivered."}])
        lines = out.splitlines()
        i = lines.index('set s "$o.Dead Pool"')
        self.assertEqual(lines[i + 1], '"$s" userDescript {Elevation below which '
                                       'nothing can be delivered.}')

    def test_rpl_description_preserves_padding_and_continuation(self):
        """The DESCRIPTION line's indentation, padding and trailing `;\\` are load-critical."""
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                _, out = self.apply_ok(src, [
                    {"target_type": "rpl_description", "target": "Mini Set",
                     "text": "Operating policy for the mini basin."},
                    {"target_type": "rpl_description", "target": "Mini Set/Cora Rules",
                     "text": "Rules governing Cora."},
                    {"target_type": "rpl_description",
                     "target": "Mini Set/Cora Rules/Flood Control",
                     "text": "Evacuates Cora ahead of the flood season."},
                ])
                self.assertIn('DESCRIPTION "Operating policy for the mini '
                              'basin.";\\', out)
                self.assertIn('  DESCRIPTION    "Rules governing Cora.";\\', out)
                self.assertIn('    DESCRIPTION          "Evacuates Cora ahead of '
                              'the flood season.";\\', out)
                for ln in out.splitlines():
                    if "DESCRIPTION" in ln:
                        self.assertTrue(ln.endswith(";\\"),
                                        f"lost the continuation on: {ln!r}")

    def test_rpl_comment_attaches_after_the_literal(self):
        for name, src in VARIANTS.items():
            with self.subTest(newlines=name):
                _, out = self.apply_ok(src, [
                    {"target_type": "rpl_comment",
                     "target": "Mini Set/Roberto Rules/Flood Control",
                     "literal": '5.00000000 "cms"',
                     "text": "Fixed release while the flood pool is drawn down."}])
                self.assertIn('$ "Roberto.Outflow" [] := 5.00000000 "cms" '
                              'COMMENTED_BY "Fixed release while the flood pool '
                              'is drawn down.";\\', out)

    def test_rpl_comment_inside_a_call_keeps_the_rest_of_the_line(self):
        _, out = self.apply_ok(LF, [
            {"target_type": "rpl_comment",
             "target": "Mini Set/Cora Rules/Flood Control",
             "literal": '0.00000000 "cms"',
             "text": "Do not let flow be negative."}])
        self.assertIn('"Max"( $ "Cora.Inflow" [], 0.00000000 "cms" COMMENTED_BY '
                      '"Do not let flow be negative." );\\', out)


class TestTargeting(AnnotateCase):
    def test_duplicate_rule_names_are_disambiguated_by_group(self):
        """Both policy groups own a rule called `Flood Control`."""
        _, out = self.apply_ok(LF, [
            {"target_type": "rpl_description",
             "target": "Mini Set/Roberto Rules/Flood Control",
             "text": "Roberto flood control."}])
        self.assertIn('DESCRIPTION          "Roberto flood control.";\\', out)
        # the Cora rule of the same name was left empty
        self.assertEqual(out.count('DESCRIPTION          "";\\'), 1)

    def test_unknown_targets_are_reported_not_dropped(self):
        proc, result = self.run_annotate(LF, [
            {"target_type": "object_description", "target": "Nonexistent",
             "text": "x"},
            {"target_type": "slot_description", "target": "Cora.No Such Slot",
             "text": "x"},
            {"target_type": "rpl_description", "target": "Mini Set/No Group/No Rule",
             "text": "x"},
            {"target_type": "rpl_comment",
             "target": "Mini Set/Cora Rules/Flood Control",
             "literal": '999.00000000 "cms"', "text": "x"},
        ])
        self.assertEqual(proc.returncode, 4, proc.stdout)
        self.assertIn("not found: 4", proc.stdout)
        self.assertIn("no such object", proc.stdout)
        self.assertIn("no such slot", proc.stdout)
        self.assertIn("no such RPL set/group/item path", proc.stdout)
        self.assertIn("not found in the body", proc.stdout)
        self.assertEqual(result, LF, "a run with only bad targets still rewrote bytes")


class TestNeverOverwrite(AnnotateCase):
    """TEST-003 / REQ-005: existing text is reported as skipped and left alone."""

    def test_all_surfaces_skip_existing_text(self):
        proc, result = self.run_annotate(LF, [
            {"target_type": "object_description", "target": "Roberto",
             "text": "REPLACEMENT"},
            {"target_type": "slot_description", "target": "Cora.Max Release",
             "text": "REPLACEMENT"},
            {"target_type": "rpl_description",
             "target": "Mini Set/Cora Rules/Minimum Fish Flow",
             "text": "REPLACEMENT"},
            {"target_type": "rpl_comment",
             "target": "Mini Set/Cora Rules/Minimum Fish Flow",
             "literal": '12.00000000 "cms"', "text": "REPLACEMENT"},
        ])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.count("SKIPPED"), 4, proc.stdout)
        self.assertNotIn("REPLACEMENT", result.decode("utf-8"))
        self.assertEqual(result, LF, "a fully-skipped run must not change a byte")

    def test_model_description_skipped_when_already_set(self):
        described = LF.replace(b"$ws.Model.FileInfo comment {}",
                               b"$ws.Model.FileInfo comment {Already written.}")
        proc, result = self.run_annotate(described, [
            {"target_type": "model_description", "target": "", "text": "REPLACEMENT"}])
        self.assertIn("SKIPPED (existing text)", proc.stdout)
        self.assertEqual(result, described)


class TestTextValidation(AnnotateCase):
    """TEST-004 / CON-004: unsupported characters are refused, never escaped and hoped."""

    def reject(self, entries):
        proc, result = self.run_annotate(LF, entries)
        self.assertEqual(proc.returncode, 3, proc.stdout)
        self.assertIn("nothing was written", proc.stderr)
        self.assertIsNone(result, "a rejected proposal must not produce a file")
        return proc.stderr

    def test_braces_rejected_everywhere(self):
        err = self.reject([{"target_type": "object_description", "target": "Cora",
                            "text": "Holds {a brace}"}])
        self.assertIn("brace", err)

    def test_quotes_rejected_in_rpl_surfaces_only(self):
        err = self.reject([{"target_type": "rpl_description", "target": "Mini Set",
                            "text": 'He said "no"'}])
        self.assertIn("double quote", err)
        # the same text is fine in a Tcl brace string
        _, out = self.apply_ok(LF, [
            {"target_type": "object_description", "target": "Cora",
             "text": 'Known locally as the "upper" reservoir.'}])
        self.assertIn('userDescript {Known locally as the "upper" reservoir.}', out)

    def test_newline_and_backslash_rejected(self):
        self.assertIn("newline", self.reject([
            {"target_type": "object_description", "target": "Cora",
             "text": "line one\nline two"}]))
        self.assertIn("backslash", self.reject([
            {"target_type": "object_description", "target": "Cora",
             "text": "a back\\slash"}]))

    def test_overlong_text_rejected(self):
        self.assertIn("over the 400-character limit", self.reject([
            {"target_type": "object_description", "target": "Cora",
             "text": "x" * 401}]))

    def test_structural_errors_rejected(self):
        self.assertIn("not one of", self.reject([
            {"target_type": "nope", "target": "Cora", "text": "x"}]))
        self.assertIn("non-empty string", self.reject([
            {"target_type": "object_description", "target": "Cora", "text": "  "}]))
        self.assertIn("needs a 'literal'", self.reject([
            {"target_type": "rpl_comment",
             "target": "Mini Set/Cora Rules/Flood Control", "text": "x"}]))


class TestCli(AnnotateCase):
    def test_in_place_rewrites_the_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            model = tmp / "mini_model.mdl"
            model.write_bytes(LF)
            proposals = tmp / "p.json"
            proposals.write_text(json.dumps([
                {"target_type": "object_description", "target": "Cora",
                 "text": "Upstream storage reservoir."}]), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ANNOTATE), str(model), str(proposals),
                 "--in-place"], capture_output=True, text=True, cwd=str(REPO))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("Upstream storage reservoir.",
                          model.read_text(encoding="utf-8"))
            self.assertFalse((tmp / "mini_model_annotated.mdl").exists())

    def test_default_output_is_a_sibling_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            model = tmp / "mini_model.mdl"
            model.write_bytes(LF)
            proposals = tmp / "p.json"
            proposals.write_text("[]", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ANNOTATE), str(model), str(proposals)],
                capture_output=True, text=True, cwd=str(REPO))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue((tmp / "mini_model_annotated.mdl").exists())
            self.assertEqual(model.read_bytes(), LF, "source must be untouched")

    def test_dry_run_writes_nothing(self):
        proc, result = self.run_annotate(LF, [
            {"target_type": "object_description", "target": "Cora", "text": "x"}],
            "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIsNone(result)
        self.assertIn("dry run", proc.stdout)

    def test_stdout_ascii(self):
        proc, _ = self.run_annotate(LF, [])
        proc.stdout.encode("ascii")  # Windows cp1252 consoles


if __name__ == "__main__":
    unittest.main()
