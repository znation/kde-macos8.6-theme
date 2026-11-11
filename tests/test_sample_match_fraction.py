"""Tests match-color coverage fractions in the reference sampler."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleMatchFraction(CliTestCase):
    """The find-color search's ``--match-fraction`` matching share."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_region_fraction_text_json_and_coordinate_limit(self):
        _, data = rgb_image(5, 3, lambda x, y: (
            (10, 20, 30) if (x, y) == (1, 0) else
            (11, 20, 30) if (x, y) == (3, 1) else (0, 0, 0)
        ))
        path = self._write(self._tmp_dir(), "fraction.png", data)
        args = (path, "1", "0", "--width", "3", "--height", "2", "--find-color", "0a141e",
                "--color-tolerance", "1", "--match-fraction")
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(*args, "--match-pixels", "1", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["count"], 2)
        self.assertEqual(match["fraction"], 1 / 3)
        self.assertEqual(len(match["pixels"]), 1)
        self.assertEqual(match["omitted_pixels"], 1)
        self.assertEqual(read.call_args.kwargs["max_rows"], 2)
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn("count: 2\nfraction: 0.3333333333333333\nbounds:", text.stdout)
        ordinary = self._run(path, "1", "0", "--width", "3", "--height", "2", "--find-color", "0a141e", "--color-tolerance", "1", "--json")
        self._assert_success(ordinary)
        ordinary_match = json.loads(ordinary.stdout)["match"]
        self.assertNotIn("fraction", ordinary_match)
        self.assertEqual((ordinary_match["count"], ordinary_match["bounds"]),
                         (match["count"], match["bounds"]))

    def test_zero_one_alpha_and_opaque_fallback(self):
        _, opaque = rgb_image(2, 1, lambda x, y: (4, 5, 6))
        path = self._write(self._tmp_dir(), "opaque.png", opaque)
        zero = self._run(path, "0", "0", "--width", "2", "--height", "1", "--find-color", "000000", "--match-fraction", "--json")
        self._assert_success(zero)
        self.assertEqual(json.loads(zero.stdout)["match"]["fraction"], 0.0)
        full = self._run(path, "0", "0", "--width", "2", "--height", "1", "--find-color", "040506", "--match-alpha", "255", "--match-fraction", "--json")
        self._assert_success(full)
        self.assertEqual(json.loads(full.stdout)["match"]["fraction"], 1.0)
        transparent = self._write(self._tmp_dir(), "transparent.png", make_png(2, 1,
            [bytes((4, 5, 6, 0, 4, 5, 6, 255))], color_type=6))
        filtered = self._run(transparent, "0", "0", "--width", "2", "--height", "1", "--find-color", "040506",
                             "--match-alpha", "0", "--match-fraction", "--json")
        self._assert_success(filtered)
        self.assertEqual(json.loads(filtered.stdout)["match"]["fraction"], 0.5)

    def test_requires_find_color_before_reads_and_direct_script(self):
        path = self._write(self._tmp_dir(), "unused.png", rgb_image(1, 1, lambda x, y: (1, 2, 3))[1])
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            invalid = self._run(path, "0", "0", "--match-fraction")
        self._assert_usage_error(invalid, "requires --find-color")
        self.assertEqual(invalid.stdout, "")
        direct = self._run_script(path, "0", "0", "--find-color", "010203", "--match-fraction", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["fraction"], 1.0)


if __name__ == "__main__":
    import unittest

    unittest.main()
