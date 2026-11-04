"""Tests for paging horizontal color-search match intervals."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleMatchRunsOffset(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def setUp(self):
        super().setUp()
        target = (1, 2, 3)
        matches = ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8})
        _, encoded = rgb_image(13, 4, lambda x, y: target
                               if 1 <= y <= 2 and x - 2 in matches[y - 1]
                               else (0, 0, 0))
        path = self._write(self._tmp_dir(), "segments.png", encoded)
        self.base = (path, "2", "1", "--width", "9", "--height", "2",
                     "--find-color", "010203", "--match-runs", "--match-run-count",
                     "--longest-match-run", "--match-fraction", "--match-centroid", "--json")

    def test_offset_pages_globally_after_filters_and_preserves_summaries(self):
        result = self._run(*self.base, "--max-match-runs", "2", "--match-run-offset", "2")
        zero = self._run(*self.base, "--max-match-runs", "2", "--match-run-offset", "0")
        past_end = self._run(*self.base, "--max-match-runs", "2", "--match-run-offset", "5")
        minimum = self._run(*self.base, "--min-match-run-length", "2", "--max-match-runs", "1",
                            "--match-run-offset", "1")
        maximum = self._run(*self.base, "--max-match-run-length", "2", "--max-match-runs", "1",
                            "--match-run-offset", "1")
        contradictory = self._run(*self.base, "--min-match-run-length", "3",
                                  "--max-match-run-length", "2", "--max-match-runs", "2",
                                  "--match-run-offset", "0")
        absent = self._run(*self.base[:-1], "--find-color", "FFFFFF", "--match-runs",
                           "--max-match-runs", "2", "--match-run-offset", "0", "--json")
        for item in (result, zero, past_end, minimum, maximum, contradictory, absent):
            self._assert_success(item)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["runs"], [{"x": 7, "y": 1, "length": 3},
                                         {"x": 2, "y": 2, "length": 4}])
        self.assertEqual((match["omitted_runs"], match["run_offset"]), (3, 2))
        self.assertEqual(match["count"], 11)
        self.assertEqual(match["run_count"], 5)
        self.assertEqual(match["longest_run"], {"x": 2, "y": 2, "length": 4})
        zero_match = json.loads(zero.stdout)["match"]
        self.assertEqual(zero_match["runs"], [{"x": 2, "y": 1, "length": 1},
                                              {"x": 4, "y": 1, "length": 2}])
        self.assertEqual(zero_match["run_offset"], 0)
        end_match = json.loads(past_end.stdout)["match"]
        self.assertEqual((end_match["runs"], end_match["omitted_runs"]), ([], 5))
        self.assertEqual(json.loads(minimum.stdout)["match"]["runs"],
                         [{"x": 7, "y": 1, "length": 3}])
        self.assertEqual(json.loads(minimum.stdout)["match"]["omitted_runs"], 2)
        self.assertEqual(json.loads(maximum.stdout)["match"]["runs"],
                         [{"x": 4, "y": 1, "length": 2}])
        self.assertEqual(json.loads(maximum.stdout)["match"]["omitted_runs"], 2)
        for empty in (contradictory, absent):
            empty_match = json.loads(empty.stdout)["match"]
            self.assertEqual((empty_match["runs"], empty_match["omitted_runs"]), ([], 0))

    def test_text_defaults_script_and_invalid_offsets(self):
        base = self.base[:-1]
        text = self._run(*base, "--max-match-runs", "2", "--match-run-offset", "2")
        direct = self._run_script(*base, "--max-match-runs", "2", "--match-run-offset", "2", "--json")
        default = self._run(*base, "--max-match-runs", "2", "--json")
        for item in (text, direct, default):
            self._assert_success(item)
        self.assertIn("matching run offset: 2\nmatching runs: [{\"x\":7,\"y\":1,\"length\":3}", text.stdout)
        self.assertNotIn("run_offset", json.loads(default.stdout)["match"])
        self.assertEqual(json.loads(direct.stdout)["match"]["runs"],
                         json.loads(self._run(*self.base, "--max-match-runs", "2",
                                               "--match-run-offset", "2").stdout)["match"]["runs"])
        for value in ("-1", "1.5", "bad", "１"):
            invalid = self._run("missing.png", "0", "0", "--match-runs", "--max-match-runs", "1",
                                "--match-run-offset", value)
            self.assertEqual((invalid.returncode, invalid.stdout), (2, ""))
        missing = self._run("missing.png", "0", "0", "--match-runs", "--max-match-runs", "1",
                            "--match-run-offset")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))
        dependency = self._run("missing.png", "0", "0", "--match-run-offset", "0")
        self.assertEqual(dependency.returncode, 2)
        self.assertIn("--match-run-offset requires --max-match-runs", dependency.stderr)
        self.assertIn("--match-run-offset K", self._run("--help").stdout)


if __name__ == "__main__":
    import unittest
    unittest.main()
