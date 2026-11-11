"""Tests matching-pixel centroid reporting."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleMatchCentroid(CliTestCase):
    """The find-color search's ``--match-centroid`` summary."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_asymmetric_cropped_matches_and_limit(self):
        _, data = rgb_image(6, 3, lambda x, y: (1, 2, 3) if (x, y) in {(1, 1), (4, 1), (2, 2), (5, 2)} else (0, 0, 0))
        path = self._write(self._tmp_dir(), "centroid.png", data)
        args = (path, "1", "1", "--width", "4", "--height", "2", "--find-color", "010203", "--match-centroid")
        result = self._run(*args, "--match-pixels", "1", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["count"], 3)
        self.assertEqual(match["bounds"], {"x": 1, "y": 1, "width": 4, "height": 2})
        self.assertEqual(match["centroid"], {"x": 7 / 3, "y": 4 / 3})
        self.assertEqual(len(match["pixels"]), 1)
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn("centroid: 2.3333333333333335,1.3333333333333333\n", text.stdout)

    def test_none_singleton_and_omitted_by_default(self):
        _, data = rgb_image(2, 1, lambda x, y: (1, 2, 3) if x == 1 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "centroid-cases.png", data)
        none = self._run(path, "0", "0", "--width", "2", "--find-color", "ffffff", "--match-centroid", "--json")
        self._assert_success(none)
        self.assertIsNone(json.loads(none.stdout)["match"]["centroid"])
        none_text = self._run(path, "0", "0", "--width", "2", "--find-color", "ffffff", "--match-centroid")
        self._assert_success(none_text)
        self.assertIn("count: 0\n", none_text.stdout)
        self.assertIn("bounds: none\ncentroid: none\n", none_text.stdout)
        one = self._run(path, "0", "0", "--width", "2", "--find-color", "010203", "--match-centroid", "--json")
        self._assert_success(one)
        self.assertEqual(json.loads(one.stdout)["match"]["centroid"], {"x": 1.0, "y": 0.0})
        one_text = self._run(path, "0", "0", "--width", "2", "--find-color", "010203", "--match-centroid")
        self._assert_success(one_text)
        self.assertIn("bounds: 1,0,1,1\ncentroid: 1.0,0.0\n", one_text.stdout)
        ordinary = self._run(path, "0", "0", "--width", "2", "--find-color", "010203", "--json")
        self._assert_success(ordinary)
        self.assertNotIn("centroid", json.loads(ordinary.stdout)["match"])
        ordinary_text = self._run(path, "0", "0", "--width", "2", "--find-color", "010203")
        self._assert_success(ordinary_text)
        self.assertNotIn("centroid:", ordinary_text.stdout)

    def test_direct_script_matches_package_cli(self):
        _, data = rgb_image(2, 1, lambda x, y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "centroid-script.png", data)
        args = (path, "0", "0", "--width", "2", "--find-color", "010203", "--match-centroid", "--json")
        self.assertEqual(self._run(*args).stdout, self._run_script(*args).stdout)

    def test_alpha_filter_and_other_match_diagnostics_share_predicate(self):
        data = make_png(3, 1, [bytes((1, 2, 3, 0, 1, 2, 3, 255, 2, 2, 3, 255))], color_type=6)
        path = self._write(self._tmp_dir(), "centroid-alpha.png", data)
        result = self._run(path, "0", "0", "--width", "3", "--find-color", "010203",
                           "--color-tolerance", "1", "--match-alpha", "255", "--match-centroid",
                           "--match-fraction", "--match-runs", "--match-column-runs", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["count"], 2)
        self.assertEqual(match["centroid"], {"x": 1.5, "y": 0.0})
        self.assertEqual(match["fraction"], 2 / 3)
        self.assertEqual(match["runs"], [{"x": 1, "y": 0, "length": 2}])
        self.assertEqual(match["column_runs"], [{"x": 1, "y": 0, "length": 1},
                                                {"x": 2, "y": 0, "length": 1}])


if __name__ == "__main__":
    import unittest

    unittest.main()
