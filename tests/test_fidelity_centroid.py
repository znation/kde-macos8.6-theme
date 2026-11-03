"""Centroid of mismatching fidelity pixels."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase
from support.png_fixtures import make_png
from tools import fidelity
from tools.fidelity_spatial import difference_centroid
from tools.png import Image


class TestDifferenceCentroid(unittest.TestCase):
    def test_equal_pixel_centroid_and_threshold(self):
        # Differing pixels (0,0), (3,0), and (1,2): unequal deltas do not
        # weight the result, and the empty row remains irrelevant.
        rgb = bytearray(4 * 3 * 3)
        rgb[0] = 1
        rgb[9] = 100
        rgb[(2 * 4 + 1) * 3] = 2
        candidate = Image(4, 3, bytes(rgb))
        reference = Image(4, 3, bytes(36))
        self.assertEqual(difference_centroid(candidate, reference, 0),
                         {"x": 4 / 3, "y": 2 / 3})
        self.assertEqual(difference_centroid(candidate, reference, 100), None)
        self.assertEqual(difference_centroid(reference, reference, 0), None)

    def test_alpha_fallback_and_hidden_rgb(self):
        changed = Image(2, 1, bytes([0, 0, 0, 8, 0, 0]))
        opaque = Image(2, 1, bytes(6))
        self.assertEqual(difference_centroid(changed, opaque, 0), {"x": 1.0, "y": 0.0})
        hidden = Image(1, 1, bytes([9, 0, 0]), bytes([0]))
        clear = Image(1, 1, bytes(3), bytes([0]))
        self.assertEqual(difference_centroid(hidden, clear, 8), {"x": 0.0, "y": 0.0})


class TestDifferenceCentroidCli(FidelityCliTestCase):
    def test_crops_verdict_and_default_omission(self):
        candidate = make_png(5, 3, [bytes(15), bytes([0, 0, 0, 10, 0, 0] + [0] * 9), bytes(15)])
        reference = make_png(5, 3, [bytes(15)] * 3)
        args = ("--difference-centroid", "--candidate-crop", "1,0,3,3", "--crop", "0,0,3,3")
        failed = self._run_png_pair(candidate, reference, *args, "--json")
        data = json.loads(failed.stdout)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(data["difference_centroid"], {"x": 0.0, "y": 1.0})
        passed = self._run_png_pair(candidate, reference, *args, "--max-mae", "255")
        self.assertEqual(passed.returncode, 0)
        self.assertIn('difference centroid: {"x": 0.0, "y": 1.0}', passed.stdout)
        with mock.patch.object(fidelity, "difference_centroid") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_centroid", json.loads(ordinary.stdout))
        helper.assert_not_called()

    def test_requested_empty_centroid_is_null_in_json_and_text(self):
        same = make_png(2, 1, [bytes(6)])
        report = self._run_png_pair(same, same, "--difference-centroid", "--json")
        self.assertIsNone(json.loads(report.stdout)["difference_centroid"])
        text = self._run_png_pair(same, same, "--difference-centroid")
        self.assertIn("difference centroid: null", text.stdout)


if __name__ == "__main__":
    unittest.main()
