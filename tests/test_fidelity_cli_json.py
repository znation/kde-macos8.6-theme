"""Structured JSON output for the fidelity comparison CLI."""

from __future__ import annotations

import json
import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase
from support.png_fixtures import control_named_png, make_png, rgb_image, solid_rgb
from support.symlink_fixtures import symlinked_repo
from tools import fidelity_sources

KEYS = {"candidate", "reference", "candidate_crop", "reference_crop", "thresholds", "metrics",
        "candidate_difference_bounds", "reference_difference_bounds", "passed"}


class TestJsonCli(FidelityCliTestCase):
    def _json(self, *args, status):
        result = self._run(*args, "--json")
        self.assertEqual(result.returncode, status, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        data = json.loads(result.stdout)
        self.assertEqual(set(data), KEYS)
        return data

    def test_complete_schema_and_metrics(self):
        candidate, altered = self._write_altered_pair(self._tmp_dir())
        data = self._json(candidate, altered, status=1)
        self.assertEqual(data["candidate"], candidate)
        self.assertEqual(data["reference"], altered)
        self.assertIsNone(data["candidate_crop"])
        self.assertIsNone(data["reference_crop"])
        self.assertEqual(data["thresholds"], {"tolerance": 0, "max_mae": None, "max_frac": None})
        m = data["metrics"]
        self.assertEqual((m["width"], m["height"], m["pixels"]), (3, 3, 9))
        self.assertAlmostEqual(m["mae"], 50 / 36)
        self.assertEqual((m["mae_r"], m["mae_b"]), (0, 0))
        self.assertAlmostEqual(m["mae_g"], 50 / 9)
        self.assertAlmostEqual(m["rmse"], (2500 / 36) ** 0.5)
        self.assertEqual((m["max_delta"], m["max_x"], m["max_y"]), (50, 1, 0))
        self.assertEqual(m["differing"], 1)
        self.assertAlmostEqual(m["frac_differing"], 1 / 9)
        for key in ("width", "height", "pixels", "max_delta", "max_x", "max_y", "differing"):
            self.assertIs(type(m[key]), int, key)
        for key in ("mae", "mae_g", "rmse", "frac_differing"):
            self.assertIs(type(m[key]), float, key)
        self.assertIs(data["passed"], False)

    def test_identical_images_pass(self):
        path = self._solid_reference()
        data = self._json(path, path, status=0)
        self.assertEqual(data["metrics"]["mae"], 0)
        self.assertEqual(data["metrics"]["differing"], 0)
        self.assertIs(data["passed"], True)

    def test_alpha_only_difference(self):
        clear = make_png(2, 1, [bytes([10, 20, 30, 0] * 2)], color_type=6)
        opaque = make_png(2, 1, [bytes([10, 20, 30, 255] * 2)], color_type=6)
        tmp = self._tmp_dir()
        data = self._json(self._write(tmp, "c.png", clear), self._write(tmp, "r.png", opaque), status=1)
        m = data["metrics"]
        self.assertEqual((m["mae_r"], m["mae_g"], m["mae_b"], m["mae_a"]), (0, 0, 0, 255))
        self.assertAlmostEqual(m["mae"], 255 / 4)
        self.assertEqual((m["differing"], m["max_delta"]), (2, 255))

    def test_both_crops_report_crop_relative_coordinates(self):
        # Candidate surface at (1, 1) in a 4x4, reference surface at (2, 2) in
        # a 5x5; the reference's surface pixel (1, 0) is raised by 40 in red,
        # so the worst delta sits at crop-relative (1, 0), not a source offset.
        def surface(ox, oy, bump):
            def pixel(x, y):
                if ox <= x < ox + 2 and oy <= y < oy + 2:
                    red = (x - ox) * 9 + (40 if bump and (x - ox, y - oy) == (1, 0) else 0)
                    return (red, (y - oy) * 9, 5)
                return (0, 0, 0)
            return pixel
        tmp = self._tmp_dir()
        candidate = self._write(tmp, "c.png", rgb_image(4, 4, surface(1, 1, False))[1])
        reference = self._write(tmp, "r.png", rgb_image(5, 5, surface(2, 2, True))[1])
        data = self._json(candidate, reference, "--candidate-crop", "1,1,2,2", "--crop", "2,2,2,2", status=1)
        self.assertEqual(data["candidate_crop"], [1, 1, 2, 2])
        self.assertEqual(data["reference_crop"], [2, 2, 2, 2])
        m = data["metrics"]
        self.assertEqual((m["width"], m["height"], m["max_delta"], m["max_x"], m["max_y"]), (2, 2, 40, 1, 0))

    def test_tolerance_and_budgets_match_the_gate(self):
        candidate, altered = self._write_altered_pair(self._tmp_dir())
        cases = [
            (("--tolerance", "50"), 0, {"tolerance": 50, "max_mae": None, "max_frac": None}),
            (("--tolerance", "49"), 1, {"tolerance": 49, "max_mae": None, "max_frac": None}),
            (("--max-mae", "2"), 0, {"tolerance": 0, "max_mae": 2.0, "max_frac": None}),
            (("--max-mae", "1"), 1, {"tolerance": 0, "max_mae": 1.0, "max_frac": None}),
            (("--max-frac", "0.12"), 0, {"tolerance": 0, "max_mae": None, "max_frac": 0.12}),
            (("--max-frac", "0.10"), 1, {"tolerance": 0, "max_mae": None, "max_frac": 0.1}),
            (("--max-mae", "2", "--max-frac", "0.12"), 0, {"tolerance": 0, "max_mae": 2.0, "max_frac": 0.12}),
            (("--max-mae", "2", "--max-frac", "0.10"), 1, {"tolerance": 0, "max_mae": 2.0, "max_frac": 0.1}),
            (("--max-mae", "1", "--max-frac", "0.12"), 1, {"tolerance": 0, "max_mae": 1.0, "max_frac": 0.12}),
        ]
        for extra, status, thresholds in cases:
            with self.subTest(extra=extra):
                data = self._json(candidate, altered, *extra, status=status)
                self.assertEqual(data["thresholds"], thresholds)
                self.assertIs(data["passed"], status == 0)

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

    def test_control_character_path_round_trips_escaped(self):
        with control_named_png() as path:
            result = self._run(path, path, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("\x1b", result.stdout)
        self.assertNotIn("\x07", result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual((data["candidate"], data["reference"]), (path, path))

    def _assert_error_without_json(self, result):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("fidelity", result.stderr)

    def test_errors_exit_2_without_json(self):
        tmp = self._tmp_dir()
        reference = self._solid_reference()
        broken = self._write(tmp, "broken.png", b"not a png")
        small = self._write(tmp, "small.png", solid_rgb(2, 2)[1])
        large = self._write(tmp, "large.png", solid_rgb(4, 4)[1])
        for args in (
            (reference, reference, "--tolerance", "-1"),
            ("/nonexistent.png", reference),
            (broken, reference),
            (small, large),
            (small, small, "--crop", "1,1,2,2"),
        ):
            with self.subTest(args=args):
                self._assert_error_without_json(self._run(*args, "--json"))

    def test_escaping_symlink_exits_2_without_json(self):
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(self._tmp_dir(), "reference.png", data)
        candidate = self._write(self._tmp_dir(), "candidate.png", data)
        with mock.patch.object(fidelity_sources, "ROOT", str(root)):
            result = self._run(candidate, str(link), "--json")
        self._assert_error_without_json(result)
        self.assertIn("resolves outside", result.stderr)


if __name__ == "__main__":
    unittest.main()
