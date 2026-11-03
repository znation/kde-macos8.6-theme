"""Direct tests for assembled reference color-search results."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest import TestCase

from support import repo_root  # noqa: F401
from tools.sample_arguments import build_parser
from tools.sample_report_search import _search_match


class TestSampleSearchResult(TestCase):
    def test_empty_match_set_has_no_bounds_centroid_or_runs(self):
        args = build_parser().parse_args([
            "fixture.png", "1", "0", "--width", "3", "--height", "2",
            "--find-color", "0a141e", "--match-centroid", "--match-runs",
            "--match-column-runs",
        ])
        image = SimpleNamespace(width=5, rgb=bytes((0, 0, 0) * 10), alpha=None)

        result = _search_match(args, image)

        self.assertEqual(result["count"], 0)
        self.assertIsNone(result["bounds"])
        self.assertIsNone(result["centroid"])
        self.assertEqual(result["runs"], [])
        self.assertEqual(result["column_runs"], [])

    def test_combined_diagnostics_return_without_printing_or_mutation(self):
        args = build_parser().parse_args([
            "fixture.png", "1", "0", "--width", "3", "--height", "2",
            "--find-color", "0a141e", "--color-tolerance", "1",
            "--match-alpha", "255", "--match-fraction", "--match-centroid",
            "--match-pixels", "1", "--match-runs", "--match-column-runs",
            "--json",
        ])
        before = vars(args).copy()
        pixels = bytes((0, 0, 0) * 1 + (10, 20, 30) + (0, 0, 0) * 3
                       + (0, 0, 0) * 3 + (11, 20, 30) + (0, 0, 0))
        image = SimpleNamespace(width=5, rgb=pixels, alpha=None)
        output = StringIO()
        with redirect_stdout(output):
            result = _search_match(args, image)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(vars(args), before)
        self.assertEqual(result, {
            "rgb": [10, 20, 30], "hex": "#0A141E", "count": 2,
            "bounds": {"x": 1, "y": 0, "width": 3, "height": 2},
            "fraction": 1 / 3, "centroid": {"x": 2.0, "y": 0.5},
            "pixels": [{"x": 1, "y": 0}], "omitted_pixels": 1,
            "runs": [{"x": 1, "y": 0, "length": 1},
                     {"x": 3, "y": 1, "length": 1}],
            "column_runs": [{"x": 1, "y": 0, "length": 1},
                             {"x": 3, "y": 1, "length": 1}],
            "tolerance": 1, "alpha": 255,
        })


if __name__ == "__main__":
    import unittest

    unittest.main()
