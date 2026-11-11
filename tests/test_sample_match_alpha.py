"""Tests exact alpha filtering for sampler color location."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleMatchAlpha(CliTestCase):
    """The find-color search's ``--match-alpha`` exact-alpha predicate."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_exact_filter_in_region_text_json_and_tolerance(self):
        row = bytes((9, 8, 7, 0, 9, 8, 7, 128, 9, 8, 7, 255,
                     10, 8, 7, 128, 9, 8, 7, 128))
        path = self._write(self._tmp_dir(), "alpha.png", make_png(5, 1, [row], color_type=6))
        args = (path, "1", "0", "--width", "3", "--find-color", "090807",
                "--match-alpha", "128", "--color-tolerance", "1")
        result = self._run(*args, "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match, {"rgb": [9, 8, 7], "hex": "#090807", "count": 2,
            "bounds": {"x": 1, "y": 0, "width": 3, "height": 1}, "tolerance": 1, "alpha": 128})
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn("tolerance: 1\nalpha: 128", text.stdout)
        all_rgb = self._run(path, "1", "0", "--width", "3", "--find-color", "090807", "--json")
        self._assert_success(all_rgb)
        self.assertEqual(json.loads(all_rgb.stdout)["match"]["count"], 2)
        maximum = self._run(path, "1", "0", "--width", "3", "--find-color", "090807",
                            "--match-alpha", "128", "--color-tolerance", "255", "--json")
        self._assert_success(maximum)
        self.assertEqual(json.loads(maximum.stdout)["match"]["count"], 2)

    def test_opaque_fallback_trns_bounded_decode_and_direct_script(self):
        _, data = rgb_image(2, 1, lambda x, y: (4, 5, 6))
        path = self._write(self._tmp_dir(), "opaque.png", data)
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(path, "1", "0", "--find-color", "040506", "--match-alpha", "255", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["match"]["count"], 1)
        self.assertTrue(read.call_args.kwargs["alpha"])
        self.assertEqual(read.call_args.kwargs["max_rows"], 1)
        trns = self._write(self._tmp_dir(), "trns.png", make_png(1, 1, [bytes((4, 5, 6))],
            color_type=2, trns=b"\x00\x04\x00\x05\x00\x06"))
        transparent = self._run_script(trns, "0", "0", "--find-color", "040506", "--match-alpha", "0", "--json")
        self._assert_success(transparent)
        self.assertEqual(json.loads(transparent.stdout)["match"]["alpha"], 0)

    def test_validation_precedes_reads_and_alpha_flag_conflict(self):
        path = self._write(self._tmp_dir(), "unused.png", make_png(1, 1, [bytes((1, 2, 3, 255))], color_type=6))
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            for value in ("-1", "256", "1.5", "١", "1_0"):
                bad = self._run(path, "0", "0", "--find-color", "010203", "--match-alpha", value)
                self._assert_usage_error(bad)
                self.assertEqual(bad.stdout, "")
            for args in ((path, "0", "0", "--match-alpha", "0"),
                         (path, "0", "0", "--match-alpha", "0", "--histogram"),
                         (path, "0", "0", "--match-alpha", "0", "--runs"),
                         (path, "0", "0", "--alpha", "--find-color", "010203", "--match-alpha", "0")):
                invalid = self._run(*args)
                self._assert_usage_error(invalid)
                self.assertEqual(invalid.stdout, "")


if __name__ == "__main__":
    import unittest

    unittest.main()
