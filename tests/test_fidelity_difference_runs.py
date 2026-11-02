"""Disjoint horizontal mismatch runs for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_pixels import difference_runs  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceRuns(unittest.TestCase):
    def test_runs_split_at_gaps_and_row_boundaries(self):
        width, height = 5, 2
        rgb = bytearray(width * height * 3)
        for x, y, value in ((0, 0, 11), (1, 0, 12), (3, 0, 30), (4, 1, 11)):
            rgb[(y * width + x) * 3] = value
        candidate = Image(width, height, bytes(rgb))
        reference = Image(width, height, bytes(width * height * 3))
        self.assertEqual(difference_runs(candidate, reference, 10),
                         [{"x": 0, "y": 0, "length": 2},
                          {"x": 3, "y": 0, "length": 1},
                          {"x": 4, "y": 1, "length": 1}])
        self.assertEqual(difference_runs(candidate, reference, 255), [])

    def test_raw_alpha_and_hidden_rgb(self):
        candidate = Image(2, 1, bytes([20, 0, 0, 0, 0, 0]), bytes([255, 0]))
        reference = Image(2, 1, bytes(6), bytes([255, 255]))
        self.assertEqual(difference_runs(candidate, reference, 254),
                         [{"x": 1, "y": 0, "length": 1}])


class TestDifferenceRunsCli(FidelityCliTestCase):
    def test_opt_in_crops_text_json_and_direct_script(self):
        candidate = make_png(4, 2, [bytes([0, 0, 0, 20, 0, 0, 0, 0, 0, 30, 0, 0]), bytes(12)])
        reference = make_png(4, 2, [bytes(12), bytes(12)])
        args = ("--difference-runs", "--candidate-crop", "1,0,3,2", "--crop", "0,0,3,2")
        result = self._run_png_pair(candidate, reference, *args, "--json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["difference_runs"],
                         [{"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 1}])
        text = self._run_png_pair(candidate, reference, *args)
        self.assertIn('difference runs: [{"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 1}]', text.stdout)
        with mock.patch.object(fidelity, "difference_runs") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_runs", json.loads(ordinary.stdout))
        helper.assert_not_called()
        tmp = self._tmp_dir()
        a = self._write(tmp, "a.png", candidate)
        b = self._write(tmp, "b.png", reference)
        direct = self._run_script(a, b, "--difference-runs", "--json")
        self.assertIn("difference_runs", json.loads(direct.stdout))


if __name__ == "__main__":
    unittest.main()
