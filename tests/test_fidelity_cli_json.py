"""Structured JSON output for the fidelity comparison CLI."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase

class TestJsonCli(FidelityCliTestCase):
    def test_complete_schema_and_metrics(self):
        candidate, altered = self._write_altered_pair(self._tmp_dir())
        result = self._run(candidate, altered, "--json")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stderr, "")
        data = json.loads(result.stdout)
        self.assertEqual(set(data), {"candidate", "reference", "candidate_crop", "reference_crop", "thresholds", "metrics", "passed"})
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


if __name__ == "__main__":
    import unittest

    unittest.main()

