"""Ranked pixel diagnostics for the fidelity comparison tool."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image  # noqa: E402
from tools.fidelity_metrics import Image  # noqa: E402
from tools.fidelity_pixels import worst_pixels  # noqa: E402
from tools import fidelity  # noqa: E402


class TestWorstPixels(unittest.TestCase):
    """Test severity ranking, tie order, and differing-pixel paging."""
    def test_severity_ties_alpha_and_tolerance(self):
        ref = Image(3, 2, bytes(18))
        cand = Image(3, 2, bytes([5, 0, 0, 9, 0, 0, 8, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0]),
                     bytes([255, 255, 255, 255, 250, 255]))
        got = worst_pixels(cand, ref, 5, 2)
        self.assertEqual([(p["x"], p["y"], p["max_delta"]) for p in got],
                         [(1, 0, 9), (2, 0, 8)])
        self.assertEqual(worst_pixels(cand, ref, 9, 10), [])

    def test_offset_pages_clamp_to_area_and_preserve_ranking(self):
        red = [9, 5, 9, 0, 7, 9]
        cand = Image(3, 2, bytes(channel for value in red for channel in (value, 0, 0)))
        ref = Image(3, 2, bytes(18))
        record = lambda offset: [(p["x"], p["y"], p["max_delta"])
                                 for p in worst_pixels(cand, ref, 5, 2, offset=offset)]
        self.assertEqual(record(0), [(0, 0, 9), (2, 0, 9)])
        self.assertEqual(record(1), [(2, 0, 9), (2, 1, 9)])
        self.assertEqual(record(3), [(1, 1, 7)])
        self.assertEqual(record(4), [])
        self.assertEqual(record(100), [])

    def test_none_offset_skips_nothing_like_zero(self):
        # The offset option is None when it was not given; worst_pixels
        # treats None as 0 instead of making every caller coerce.
        red = [9, 5, 9, 0, 7, 9]
        cand = Image(3, 2, bytes(channel for value in red for channel in (value, 0, 0)))
        ref = Image(3, 2, bytes(18))
        record = lambda offset: [(p["x"], p["y"], p["max_delta"])
                                 for p in worst_pixels(cand, ref, 5, 2, offset=offset)]
        self.assertEqual(record(None), [(0, 0, 9), (2, 0, 9)])
        self.assertEqual(record(None), record(0))

    def test_offset_ranks_alpha_and_rgb_under_zero_alpha(self):
        cand = Image(2, 1, bytes((20, 0, 0, 0, 0, 0)), bytes((0, 10)))
        ref = Image(2, 1, bytes(6), bytes((0, 255)))
        got = worst_pixels(cand, ref, 0, 2, offset=1)
        self.assertEqual([(p["x"], p["max_delta"]) for p in got], [(0, 20)])

    def test_alpha_only_row_spanning_ties_and_source_values(self):
        ref = Image(2, 2, bytes(12))  # RGB-only peer: every pixel opaque black
        cand = Image(2, 2, bytes([0, 0, 3, 0, 7, 0, 7, 0, 0, 0, 0, 0]),
                     bytes([255, 255, 255, 200]))
        expected = [
            {"x": 1, "y": 1, "candidate_rgba": [0, 0, 0, 200],
             "reference_rgba": [0, 0, 0, 255], "max_delta": 55},
            {"x": 1, "y": 0, "candidate_rgba": [0, 7, 0, 255],
             "reference_rgba": [0, 0, 0, 255], "max_delta": 7},
            {"x": 0, "y": 1, "candidate_rgba": [7, 0, 0, 255],
             "reference_rgba": [0, 0, 0, 255], "max_delta": 7},
            {"x": 0, "y": 0, "candidate_rgba": [0, 0, 3, 255],
             "reference_rgba": [0, 0, 0, 255], "max_delta": 3},
        ]
        self.assertEqual(worst_pixels(cand, ref, 2, 10), expected)
        self.assertEqual(worst_pixels(cand, ref, 2, 2), expected[:2])
        self.assertEqual(worst_pixels(ref, ref, 0, 10), [])

    def test_deterministic_matrices_match_full_sort(self):
        for width, height in ((1, 1), (3, 2), (4, 2)):
            ref = Image(width, height, bytes(width * height * 3))
            rgb = bytes((i * 17) % 256 for i in range(width * height * 3))
            cand = Image(width, height, rgb)
            ordered = sorted(
                ((-max(rgb[i * 3:i * 3 + 3]), i) for i in range(width * height)
                 if max(rgb[i * 3:i * 3 + 3]) > 0)
            )
            expected = [(i % width, i // width, -delta) for delta, i in ordered[:3]]
            actual = [(p["x"], p["y"], p["max_delta"])
                      for p in worst_pixels(cand, ref, 0, 3)]
            self.assertEqual(actual, expected)


class TestWorstPixelsCli(FidelityCliTestCase):
    """Test worst-pixel reports, crop coordinates, and CLI validation."""
    def test_offset_pages_json_text_and_different_crop_origins(self):
        _, candidate = rgb_image(5, 3, lambda x, y: (
            9 if (x, y) in ((1, 1), (2, 1)) else 7 if (x, y) == (3, 2) else 0, 0, 0))
        reference = make_png(6, 4, [bytes(18) for _ in range(4)])
        args = ("--candidate-crop", "1,1,3,2", "--crop", "2,2,3,2",
                "--max-mae", "2", "--worst-pixels", "2", "--worst-pixel-offset", "1")
        data = json.loads(self._run_png_pair(candidate, reference, *args, "--json").stdout)
        pixels = data["worst_pixels"]
        self.assertEqual([(p["x"], p["y"], p["max_delta"], p["candidate_position"],
                           p["reference_position"]) for p in pixels],
                         [(1, 0, 9, [2, 1], [3, 2]), (2, 1, 7, [3, 2], [4, 3])])
        self.assertEqual(data["metrics"]["mae"], 25 / 24)
        text = self._run_png_pair(candidate, reference, *args)
        self.assertEqual(text.returncode, 0)
        self.assertIn("candidate_position=2,1 reference_position=3,2", text.stdout)
        empty_result = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,3,2",
                                          "--crop", "2,2,3,2", "--max-mae", "2",
                                          "--worst-pixels", "2", "--worst-pixel-offset", "100",
                                          "--json")
        empty = json.loads(empty_result.stdout)
        self.assertEqual(empty["worst_pixels"], [])

    def test_offset_argument_validation_precedes_source_reads(self):
        for invalid in ("-1", "1.2", "", "١"):
            result = self._run_png_pair(b"not a png", b"not a png", "--worst-pixels", "1",
                                        "--worst-pixel-offset", invalid)
            self.assertEqual((result.returncode, result.stdout), (2, ""))
        with mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read")):
            for value in ("0", "1"):
                with self.subTest(value=value):
                    self._assert_value_exits_before_reading(value)

    def _assert_value_exits_before_reading(self, value):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                fidelity.main(["missing.png", "missing.png", "--worst-pixel-offset", value])
        self.assertEqual(raised.exception.code, 2)
        self.assertEqual(stdout.getvalue(), "")

    def test_json_and_text_and_crop_relative_coordinates(self):
        surface, candidate = rgb_image(2, 1, lambda x, y: (10 if x == 1 else 0, 0, 0))
        reference = make_png(4, 1, [bytes(12)])
        result = self._run_png_pair(candidate, reference, "--candidate-crop", "0,0,2,1",
                                    "--crop", "1,0,2,1", "--max-mae", "10",
                                    "--worst-pixels", "1", "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["worst_pixels"], [{"x": 1, "y": 0,
                         "candidate_rgba": [10, 0, 0, 255],
                         "reference_rgba": [0, 0, 0, 255], "max_delta": 10,
                         "candidate_position": [1, 0], "reference_position": [2, 0]}])
        self.assertEqual(result.returncode, 0)

    def test_source_positions_for_ranked_records_and_explanation(self):
        _, candidate = rgb_image(5, 3, lambda x, y: (
            9 if (x, y) in ((1, 1), (2, 1)) else 7 if (x, y) == (3, 2) else 0, 0, 0))
        reference = make_png(6, 4, [bytes(18) for _ in range(4)])
        result = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,3,2",
                                    "--crop", "2,2,3,2", "--max-mae", "2",
                                    "--worst-pixels", "3", "--explain-worst", "--json")
        data = json.loads(result.stdout)
        pixels = data["worst_pixels"]
        self.assertEqual([(p["x"], p["y"], p["candidate_position"],
                           p["reference_position"]) for p in pixels],
                         [(0, 0, [1, 1], [2, 2]), (1, 0, [2, 1], [3, 2]),
                          (2, 1, [3, 2], [4, 3])])
        self.assertEqual(data["worst_pixel"]["candidate_position"], pixels[0]["candidate_position"])
        self.assertEqual(data["worst_pixel"]["reference_position"], pixels[0]["reference_position"])
        self.assertEqual(result.returncode, 0)  # aggregate budget passes despite mismatches
        text_result = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,3,2",
                                         "--crop", "2,2,3,2", "--max-mae", "2",
                                         "--worst-pixels", "3")
        self.assertIn("candidate_position=1,1 reference_position=2,2", text_result.stdout)

    def test_missing_crop_origins_and_empty_ranked_list(self):
        _, candidate = rgb_image(2, 1, lambda x, y: (5 if x == 1 else 0, 0, 0))
        reference = make_png(2, 1, [bytes(6)])
        data = json.loads(self._run_png_pair(candidate, reference, "--worst-pixels", "1",
                                             "--json").stdout)
        self.assertEqual((data["worst_pixels"][0]["candidate_position"],
                          data["worst_pixels"][0]["reference_position"]), ([1, 0], [1, 0]))
        _, wider_candidate = rgb_image(3, 1, lambda x, y: (5 if x == 1 else 0, 0, 0))
        data = json.loads(self._run_png_pair(wider_candidate, reference, "--candidate-crop",
                                             "1,0,2,1", "--worst-pixels", "1", "--json").stdout)
        self.assertEqual(data["worst_pixels"][0]["candidate_position"], [1, 0])
        self.assertEqual(data["worst_pixels"][0]["reference_position"], [0, 0])
        wider_reference = make_png(3, 1, [bytes(9)])
        data = json.loads(self._run_png_pair(candidate, wider_reference, "--crop", "1,0,2,1",
                                             "--worst-pixels", "1", "--json").stdout)
        self.assertEqual(data["worst_pixels"][0]["candidate_position"], [1, 0])
        self.assertEqual(data["worst_pixels"][0]["reference_position"], [2, 0])
        same = json.loads(self._run_png_pair(candidate, candidate, "--worst-pixels", "2",
                                             "--json").stdout)
        self.assertEqual(same["worst_pixels"], [])

    def test_direct_script_emits_source_positions(self):
        _, candidate = rgb_image(1, 1, lambda x, y: (4, 0, 0))
        _, reference = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        tmp = self._tmp_dir()
        candidate_path = self._write(tmp, "candidate.png", candidate)
        reference_path = self._write(tmp, "reference.png", reference)
        result = self._run_script(candidate_path, reference_path, "--worst-pixels", "1",
                                  "--worst-pixel-offset", "0", "--json")
        self.assertEqual(result.returncode, 1)
        pixel = json.loads(result.stdout)["worst_pixels"][0]
        self.assertEqual((pixel["candidate_position"], pixel["reference_position"]),
                         ([0, 0], [0, 0]))

    def test_text_report_lists_records_before_verdict(self):
        _, candidate = rgb_image(2, 1, lambda x, y: (10 if x == 1 else 0, 0, 0))
        _, reference = rgb_image(2, 1, lambda x, y: (0, 0, 0))
        result = self._run_png_pair(candidate, reference, "--worst-pixels", "2")
        lines = result.stdout.splitlines()
        start = lines.index("worst pixels: 1")
        self.assertEqual(lines[start + 1],
                         "pixel (1, 0): candidate=10,0,0,255 reference=0,0,0,255 max_delta=10 "
                         "candidate_position=1,0 reference_position=1,0")
        self.assertTrue(lines[start + 2].startswith("FAIL: "))
        self.assertEqual(result.returncode, 1)

    def test_default_does_not_call_helper_and_invalid_is_early(self):
        _, png = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with mock.patch.object(fidelity, "worst_pixels") as helper:
            result = self._run_png_pair(png, png, "--json")
        self.assertNotIn("worst_pixels", json.loads(result.stdout))
        helper.assert_not_called()
        for invalid in ("0", "-1", "1001", "1.2", "١", ""):
            with self.subTest(invalid=invalid):
                result = self._run_png_pair(png, png, "--worst-pixels", invalid)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
