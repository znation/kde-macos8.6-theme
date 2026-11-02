"""Structured JSON output for the fidelity comparison CLI."""

from __future__ import annotations

import json
import os

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase
from support.png_fixtures import make_png

class TestJsonCli(FidelityCliTestCase):
    def test_complete_schema_and_metrics(self):
        candidate, altered = self._write_altered_pair(self._tmp_dir())
        result = self._run(candidate, altered, "--json")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stderr, "")
        data = json.loads(result.stdout)
        self.assertEqual(set(data), {"candidate", "reference", "candidate_crop", "reference_crop", "thresholds", "metrics", "candidate_difference_bounds", "reference_difference_bounds", "passed"})
        self.assertEqual(data["candidate"], candidate)
        self.assertEqual(data["reference"], altered)
        self.assertIsNone(data["candidate_crop"])
        self.assertIsNone(data["reference_crop"])
        self.assertEqual(data["thresholds"], {"tolerance": 0, "max_mae": None, "max_frac": None})
        self.assertEqual(data["metrics"]["width"], 3)
        self.assertEqual(data["metrics"]["height"], 3)
        self.assertAlmostEqual(data["metrics"]["mae"], 50 / 36)
        self.assertAlmostEqual(data["metrics"]["mae_g"], 50 / 9)
        self.assertEqual(data["metrics"]["max_x"], 1)
        self.assertEqual(data["metrics"]["max_y"], 0)
        self.assertAlmostEqual(data["metrics"]["frac_differing"], 1 / 9)
        self.assertFalse(data["passed"])

    def test_script_and_budget_verdict(self):
        path = self._solid_reference()
        result = self._run_script(path, path, "--json", "--max-mae", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["passed"])

    def test_crops_are_reported_and_worst_coordinates_are_crop_relative(self):
        candidate, reference = self._write_altered_pair(self._tmp_dir())
        result = self._run(candidate, reference, "--json", "--candidate-crop", "1,0,2,2", "--crop", "0,0,2,2")
        data = json.loads(result.stdout)
        self.assertEqual(data["candidate_crop"], [1, 0, 2, 2])
        self.assertEqual(data["reference_crop"], [0, 0, 2, 2])
        self.assertEqual((data["metrics"]["width"], data["metrics"]["height"]), (2, 2))
        self.assertEqual((data["metrics"]["max_x"], data["metrics"]["max_y"]), (1, 0))

    def test_alpha_and_threshold_verdicts(self):
        candidate = make_png(1, 1, [bytes((10, 20, 30, 255))], color_type=6)
        reference = make_png(1, 1, [bytes((10, 20, 30, 200))], color_type=6)
        result = self._run_png_pair(candidate, reference, "--json", "--tolerance", "55")
        data = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data["metrics"]["mae_a"], 55)
        self.assertTrue(data["passed"])
        for args, expected in ((["--max-mae", "13"], 1), (["--max-frac", "0"], 1),
                               (["--max-mae", "14", "--max-frac", "1"], 0)):
            with self.subTest(args=args):
                run = self._run_png_pair(candidate, reference, "--json", *args)
                self.assertEqual(run.returncode, expected)
                self.assertEqual(json.loads(run.stdout)["passed"], expected == 0)

    def test_errors_emit_no_json(self):
        result = self._run("missing-candidate.png", "missing-reference.png", "--json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr)

    def test_control_path_round_trips_with_escaped_output(self):
        path = self._solid_reference()
        control_path = path + "\x01"
        os.rename(path, control_path)
        result = self._run_script(control_path, control_path, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("\x01", result.stdout)
        self.assertEqual(json.loads(result.stdout)["candidate"], control_path)


if __name__ == "__main__":
    import unittest

    unittest.main()

