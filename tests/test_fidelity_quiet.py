"""Exit-status-only verdicts for scripted fidelity gates."""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402


class TestFidelityQuiet(FidelityCliTestCase):
    def test_status_verdicts_are_silent_and_tolerance_still_applies(self):
        same = make_png(1, 1, [bytes((0, 0, 0))])
        one_step = make_png(1, 1, [bytes((1, 0, 0))])
        passed = self._run_png_pair(same, same, "--quiet")
        self.assertEqual((passed.returncode, passed.stdout, passed.stderr), (0, "", ""))

        failed = self._run_png_pair(one_step, same, "--quiet")
        tolerated = self._run_png_pair(one_step, same, "--quiet", "--tolerance", "1")
        self.assertEqual((failed.returncode, failed.stdout, failed.stderr), (1, "", ""))
        self.assertEqual((tolerated.returncode, tolerated.stdout, tolerated.stderr), (0, "", ""))

    def test_diagnostics_errors_and_mutually_exclusive_output(self):
        same = make_png(1, 1, [bytes((0, 0, 0))])
        different = make_png(1, 1, [bytes((1, 0, 0))])
        diagnostic = self._run_png_pair(different, same, "--quiet", "--difference-rows")
        self.assertEqual((diagnostic.returncode, diagnostic.stdout, diagnostic.stderr), (1, "", ""))

        tmp = self._tmp_dir()
        good = self._write(tmp, "good.png", same)
        malformed = self._write(tmp, "malformed.png", b"not a png")
        for bad_path in (str(tmp / "missing.png"), malformed):
            with self.subTest(path=bad_path):
                result = self._run(good, bad_path, "--quiet")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotEqual(result.stderr, "")

        for flags in (("--quiet", "--json"), ("--json", "--quiet")):
            with self.subTest(flags=flags):
                result = self._run("missing.png", "missing.png", *flags)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("not allowed with argument", result.stderr)

        invalid_diagnostic = self._run("missing.png", "missing.png", "--quiet",
                                       "--difference-run-offset", "1")
        self.assertEqual(invalid_diagnostic.returncode, 2)
        self.assertEqual(invalid_diagnostic.stdout, "")
        self.assertIn("requires --max-difference-runs", invalid_diagnostic.stderr)

    def test_direct_script_invocation(self):
        tmp = self._tmp_dir()
        candidate, reference = self._write_altered_pair(tmp)
        result = self._run_script(candidate, reference, "--quiet")
        self.assertEqual((result.returncode, result.stdout, result.stderr), (1, "", ""))


if __name__ == "__main__":
    unittest.main()
