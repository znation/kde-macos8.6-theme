"""Tests for limiting vertical color-search match intervals."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleMatchColumnRunsLimit(CliTestCase):
    """The vertical match runs' ``--max-match-column-runs`` page cap."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_cap_follows_length_filters_and_keeps_full_summaries(self):
        target = (10, 20, 30)
        positions = {(0, 0), (0, 2), (0, 3), (0, 5), (0, 6), (0, 7), (1, 8)}
        _, encoded = rgb_image(6, 12, lambda x, y: target
                               if (x - 2, y - 1) in positions else (0, 0, 0))
        path = self._write(self._tmp_dir(), "columns.png", encoded)
        base = (path, "2", "1", "--width", "2", "--height", "9", "--find-color",
                "0a141e", "--match-column-runs", "--match-column-run-count",
                "--longest-match-column-run", "--match-runs", "--match-run-count",
                "--longest-match-run", "--match-pixels", "1", "--match-fraction",
                "--match-centroid", "--match-rows", "--match-columns",
                "--match-row-bounds", "--match-column-bounds", "--json")
        expected_prefix = [
            {"x": 2, "y": 1, "length": 1},
            {"x": 2, "y": 3, "length": 2},
        ]
        capped = self._run(*base, "--max-match-column-runs", "2")
        self._assert_success(capped)
        match = json.loads(capped.stdout)["match"]
        self.assertEqual(match["column_runs"], expected_prefix)
        self.assertEqual(match["omitted_column_runs"], 2)
        self.assertEqual((match["count"], match["column_run_count"]), (7, 4))
        self.assertEqual(match["longest_column_run"], {"x": 2, "y": 6, "length": 3})

        cap_three = self._run(*base, "--max-match-column-runs", "3")
        self._assert_success(cap_three)
        match_three = json.loads(cap_three.stdout)["match"]
        self.assertEqual(match_three["column_runs"], expected_prefix +
                         [{"x": 2, "y": 6, "length": 3}])
        self.assertEqual(match_three["omitted_column_runs"], 1)

        cases = [
            (("--max-match-column-run-length", "2", "--max-match-column-runs", "2"),
             expected_prefix, 1),
            (("--min-match-column-run-length", "2", "--max-match-column-runs", "1"),
             [{"x": 2, "y": 3, "length": 2}], 1),
            (("--min-match-column-run-length", "4", "--max-match-column-run-length", "9",
              "--max-match-column-runs", "1"), [], 0),
            (("--max-match-column-runs", "4"), expected_prefix +
             [{"x": 2, "y": 6, "length": 3}, {"x": 3, "y": 9, "length": 1}], 0),
        ]
        for options, runs, omitted in cases:
            with self.subTest(options=options):
                result = self._run(*base, *options)
                self._assert_success(result)
                output_match = json.loads(result.stdout)["match"]
                self.assertEqual(output_match["column_runs"], runs)
                self.assertEqual(output_match["omitted_column_runs"], omitted)

        uncapped = self._run(*base)
        self._assert_success(uncapped)
        uncapped_match = json.loads(uncapped.stdout)["match"]
        self.assertNotIn("omitted_column_runs", uncapped_match)
        self.assertEqual(match["runs"], uncapped_match["runs"])
        self.assertEqual(match["rows"], uncapped_match["rows"])
        self.assertEqual(match["columns"], uncapped_match["columns"])
        self.assertEqual(match["pixels"], uncapped_match["pixels"])
        for key in ("bounds", "fraction", "centroid", "run_count", "column_run_count",
                    "longest_run", "longest_column_run", "row_bounds", "column_bounds"):
            self.assertEqual(match[key], uncapped_match[key])

        text = self._run(path, "2", "1", "--width", "2", "--height", "9",
                         "--find-color", "0a141e", "--match-column-runs",
                         "--max-match-column-runs", "2")
        self._assert_success(text)
        self.assertIn("matching column runs: [{\"x\":2,\"y\":1,\"length\":1},"
                      "{\"x\":2,\"y\":3,\"length\":2}]", text.stdout)
        self.assertIn("omitted matching column runs: 2", text.stdout)
        direct = self._run_script(path, "2", "1", "--width", "2", "--height", "9",
                                  "--find-color", "0a141e", "--match-column-runs",
                                  "--max-match-column-runs", "2", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["column_runs"], expected_prefix)

    def test_empty_results_and_option_validation(self):
        _, encoded = rgb_image(3, 4, lambda x, y: (0, 0, 0))
        path = self._write(self._tmp_dir(), "empty.png", encoded)
        args = (path, "0", "0", "--width", "3", "--height", "4", "--find-color",
                "010203", "--match-column-runs", "--max-match-column-runs", "2", "--json")
        result = self._run(*args)
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["match"]["column_runs"], [])
        self.assertEqual(json.loads(result.stdout)["match"]["omitted_column_runs"], 0)
        self.assertIsNone(build_parser().parse_args(
            ("image.png", "0", "0", "--find-color", "010203")
        ).max_match_column_runs)

        for value in ("0", "-1", "1.5", "bad", "１"):
            invalid = self._run("missing.png", "0", "0", "--find-color", "010203",
                                "--match-column-runs", "--max-match-column-runs", value)
            self.assertEqual((invalid.returncode, invalid.stdout), (2, ""))
        missing_value = self._run("missing.png", "0", "0", "--find-color", "010203",
                                  "--match-column-runs", "--max-match-column-runs")
        self.assertEqual((missing_value.returncode, missing_value.stdout), (2, ""))
        misplaced = self._run("missing.png", "0", "0", "--find-color", "010203",
                              "--max-match-column-runs", "1")
        self._assert_usage_error(misplaced, "--max-match-column-runs requires --match-column-runs")
        help_result = self._run("--help")
        self.assertIn("--max-match-column-runs N", help_result.stdout)

    def test_tolerance_and_exact_alpha_define_runs_before_capping(self):
        rows = [bytes(pixel) for pixel in (
            (10, 20, 30, 255), (10, 20, 30, 255),
            (10, 20, 30, 0), (10, 20, 30, 255),
        )]
        path = self._write(self._tmp_dir(), "rgba.png",
                           make_png(1, 4, rows, color_type=6))
        base = (path, "0", "0", "--height", "4", "--find-color", "0a141e", "--color-tolerance", "1",
                "--match-column-runs", "--max-match-column-runs", "1", "--json")
        alpha_filtered = self._run(*base, "--match-alpha", "255")
        self._assert_success(alpha_filtered)
        match = json.loads(alpha_filtered.stdout)["match"]
        self.assertEqual(match["column_runs"], [{"x": 0, "y": 0, "length": 2}])
        self.assertEqual(match["omitted_column_runs"], 1)
        transparent_rgb = self._run(*base)
        self._assert_success(transparent_rgb)
        transparent_match = json.loads(transparent_rgb.stdout)["match"]
        self.assertEqual(transparent_match["column_runs"], [{"x": 0, "y": 0, "length": 4}])
        self.assertEqual(transparent_match["omitted_column_runs"], 0)

        unequal_rows = [bytes(pixel) for pixel in (
            (10, 20, 30, 255), (11, 20, 30, 255),
        )]
        unequal_path = self._write(self._tmp_dir(), "tolerance.png",
                                   make_png(1, 2, unequal_rows, color_type=6))
        tolerant = self._run(unequal_path, "0", "0", "--height", "2", "--find-color", "0a141e",
                             "--color-tolerance", "1", "--match-column-runs", "--json")
        self._assert_success(tolerant)
        self.assertEqual(json.loads(tolerant.stdout)["match"]["column_runs"],
                         [{"x": 0, "y": 0, "length": 2}])

    def test_cap_follows_length_filters_and_preserves_summaries(self):
        target = (1, 2, 3)
        matches = ({0, 2, 3, 5, 6, 7}, {8})
        _, encoded = rgb_image(4, 11, lambda x, y: target
                               if 2 <= x < 4 and y - 1 in matches[x - 2]
                               else (0, 0, 0))
        path = self._write(self._tmp_dir(), "columns.png", encoded)
        base = (path, "2", "1", "--width", "2", "--height", "9",
                "--find-color", "010203", "--match-column-runs",
                "--longest-match-column-run", "--match-column-run-count", "--json")
        capped = self._run(*base, "--max-match-column-runs", "2")
        three = self._run(*base, "--max-match-column-runs", "3")
        filtered = self._run(*base, "--max-match-column-run-length", "2",
                             "--max-match-column-runs", "2")
        minimum = self._run(*base, "--min-match-column-run-length", "2",
                            "--max-match-column-runs", "1")
        for result in (capped, three, filtered, minimum):
            self._assert_success(result)
        match = json.loads(capped.stdout)["match"]
        self.assertEqual(match["column_runs"], [
            {"x": 2, "y": 1, "length": 1}, {"x": 2, "y": 3, "length": 2},
        ])
        self.assertEqual(match["omitted_column_runs"], 2)
        three_match = json.loads(three.stdout)["match"]
        self.assertEqual(three_match["column_runs"][-1],
                         {"x": 2, "y": 6, "length": 3})
        self.assertEqual(three_match["omitted_column_runs"], 1)
        self.assertEqual(json.loads(filtered.stdout)["match"]["column_runs"],
                         match["column_runs"])
        self.assertEqual(json.loads(filtered.stdout)["match"]["omitted_column_runs"], 1)
        self.assertEqual(json.loads(minimum.stdout)["match"]["column_runs"],
                         [{"x": 2, "y": 3, "length": 2}])
        for key in ("count", "column_run_count", "longest_column_run"):
            self.assertEqual(match[key], json.loads(three.stdout)["match"][key])

    def test_empty_unlimited_and_text_reports(self):
        _, encoded = rgb_image(4, 11, lambda x, y: (1, 2, 3)
                               if x == 2 and y in (1, 3) else (0, 0, 0))
        path = self._write(self._tmp_dir(), "sparse.png", encoded)
        args = (path, "2", "1", "--width", "2", "--height", "9",
                "--find-color", "010203", "--match-column-runs")
        full = self._run(*args, "--max-match-column-runs", "4", "--json")
        empty = self._run(*args, "--find-color", "ffffff", "--max-match-column-runs", "2", "--json")
        text = self._run(*args, "--max-match-column-runs", "2")
        for result in (full, empty, text):
            self._assert_success(result)
        self.assertEqual(json.loads(full.stdout)["match"]["omitted_column_runs"], 0)
        self.assertEqual(json.loads(empty.stdout)["match"]["column_runs"], [])
        self.assertEqual(json.loads(empty.stdout)["match"]["omitted_column_runs"], 0)
        self.assertIn('matching column runs: [{"x":2,"y":1,"length":1},'
                      '{"x":2,"y":3,"length":1}]', text.stdout)
        self.assertIn("omitted matching column runs: 0", text.stdout)
        uncapped = self._run(*args, "--json")
        self.assertNotIn("omitted_column_runs", json.loads(uncapped.stdout)["match"])
        self.assertNotIn("omitted matching column runs:", self._run(*args).stdout)

    def test_validation_help_and_direct_script(self):
        dependency = self._run("missing.png", "0", "0", "--find-color", "010203",
                               "--max-match-column-runs", "1")
        self.assertEqual(dependency.returncode, 2)
        self.assertEqual(dependency.stdout, "")
        self.assertIn("--max-match-column-runs requires --match-column-runs",
                      dependency.stderr)
        for value in ("0", "-1", "1.5", "1e2", " 1", "1_0", "１", "nope"):
            result = self._run("missing.png", "0", "0", "--find-color", "010203",
                               "--match-column-runs", "--max-match-column-runs", value)
            self.assertEqual((result.returncode, result.stdout), (2, ""))
        missing = self._run("missing.png", "0", "0", "--find-color", "010203",
                            "--match-column-runs", "--max-match-column-runs")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))
        help_result = self._run("--help")
        self.assertIn("--max-match-column-runs N", help_result.stdout)
        _, encoded = rgb_image(1, 2, lambda x, y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "direct.png", encoded)
        args = (path, "0", "0", "--height", "2", "--find-color", "010203",
                "--match-column-runs", "--max-match-column-runs", "1", "--json")
        package = self._run(*args)
        direct = self._run_script(*args)
        self.assertEqual(json.loads(package.stdout), json.loads(direct.stdout))


if __name__ == "__main__":
    import unittest

    unittest.main()
