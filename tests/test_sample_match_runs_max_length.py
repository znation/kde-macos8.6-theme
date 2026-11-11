"""Tests for filtering long horizontal color-search match segments."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleMatchRunsMaxLength(CliTestCase):
    """The horizontal match runs' ``--max-match-run-length`` cutoff."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_maximum_and_combined_filters_preserve_full_search(self):
        target = (1, 2, 3)
        matches = ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8})
        _, encoded = rgb_image(13, 4, lambda x, y: target
                               if 1 <= y <= 2 and x - 2 in matches[y - 1]
                               else (0, 0, 0))
        path = self._write(self._tmp_dir(), "segments.png", encoded)
        base = (path, "2", "1", "--width", "9", "--height", "2",
                "--find-color", "010203", "--match-runs", "--longest-match-run",
                "--match-centroid", "--match-rows", "--json")
        full_result = self._run(*base)
        bounded_result = self._run(*base, "--max-match-run-length", "2")
        one_result = self._run(*base, "--max-match-run-length", "1")
        generous_result = self._run(*base, "--max-match-run-length", "9")
        both_result = self._run(*base, "--min-match-run-length", "2",
                                "--max-match-run-length", "2")
        empty_window = self._run(*base, "--min-match-run-length", "5",
                                 "--max-match-run-length", "9")
        for result in (full_result, bounded_result, one_result, generous_result,
                       both_result, empty_window):
            self._assert_success(result)
        full = json.loads(full_result.stdout)["match"]
        bounded = json.loads(bounded_result.stdout)["match"]
        self.assertEqual(bounded["runs"], [
            {"x": 2, "y": 1, "length": 1},
            {"x": 4, "y": 1, "length": 2},
            {"x": 10, "y": 2, "length": 1},
        ])
        self.assertEqual(bounded["longest_run"], {"x": 2, "y": 2, "length": 4})
        self.assertEqual(json.loads(one_result.stdout)["match"]["runs"], [
            {"x": 2, "y": 1, "length": 1}, {"x": 10, "y": 2, "length": 1},
        ])
        self.assertEqual(json.loads(generous_result.stdout)["match"]["runs"], full["runs"])
        for key in ("count", "bounds", "centroid", "rows", "longest_run"):
            self.assertEqual(bounded[key], full[key], key)
        self.assertEqual(json.loads(both_result.stdout)["match"]["runs"],
                         [{"x": 4, "y": 1, "length": 2}])
        self.assertEqual(json.loads(empty_window.stdout)["match"]["runs"], [])
        empty = self._run(path, "2", "1", "--width", "9", "--height", "2",
                          "--find-color", "ffffff", "--match-runs",
                          "--max-match-run-length", "2", "--json")
        self._assert_success(empty)
        self.assertEqual(json.loads(empty.stdout)["match"]["runs"], [])
        text = self._run(*base[:-1], "--max-match-run-length", "2")
        self._assert_success(text)
        self.assertIn('matching runs: [{"x":2,"y":1,"length":1},'
                      '{"x":4,"y":1,"length":2},'
                      '{"x":10,"y":2,"length":1}]', text.stdout)
        direct = self._run_script(*base[:-1], "--max-match-run-length", "2", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["runs"], bounded["runs"])

    def test_validation_and_help(self):
        for value in ("0", "-1", "1.5", "1e2", " 1", "1_0", "１", "nope"):
            with self.subTest(value=value):
                result = self._run("missing.png", "0", "0", "--find-color", "010203",
                                   "--match-runs", "--max-match-run-length", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
        missing = self._run("missing.png", "0", "0", "--find-color", "010203",
                            "--match-runs", "--max-match-run-length")
        self.assertEqual(missing.returncode, 2)
        help_result = self._run("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("--max-match-run-length N", help_result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
