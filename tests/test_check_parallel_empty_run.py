"""Tests for tools/check_parallel.py's exit-5 empty-run verdicts.

unittest exits 5 (NO TESTS RAN) for a module whose run collects no tests, and
a worker that dies of its own ``os._exit(5)`` can look the same. These tests
pin when the coordinator trusts that exit status and when it fails the run: an
empty module passes, while a forged or partial summary fails. The per-byte
started-test marker scan is pinned in ``test_check_parallel_marker.py``.
"""

from __future__ import annotations

import sys
import unittest

from support.check_parallel_coordinator import CoordinatorTestCase
from support.check_parallel_fixtures import OK_MODULE
from support.process_assertions import assert_failed, assert_succeeded


class TestEmptyRunVerdicts(CoordinatorTestCase):
    """The coordinator's exit-5 / NO TESTS RAN verdicts."""


    def test_a_module_with_no_tests_does_not_fail_the_run(self):
        # unittest exits 5 (NO TESTS RAN) when a module's run collects no
        # tests, on Python 3.12 and later; interpreters before 3.12 exit 0
        # for the same empty run (the Makefile's CHECK_PATTERN guard relies
        # on that same version split). The serial discover run gets nothing
        # from such a module and still passes either way, so the parallel
        # run must pass too, with the section naming the outcome instead of
        # failing while the other modules' results stand.
        tests_dir = self._project(
            {"test_empty.py": "import unittest\n", "test_ok.py": OK_MODULE}
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_succeeded(self, result)
        if sys.version_info >= (3, 12):
            self.assertIn(
                "===== test_empty: ran no tests (unittest's NO TESTS RAN, "
                "exit 5) =====",
                result.stdout,
            )
        else:
            self.assertIn("===== test_empty: exit 0 =====", result.stdout)
        self.assertIn("===== test_ok: exit 0 =====", result.stdout)
        self.assertIn("Ran 1 test in", result.stdout)

    def test_an_exit_5_without_the_no_tests_ran_summary_fails_the_run(self):
        # The exit-5 status alone is not evidence of an empty run: a
        # module whose test dies of its own `os._exit(5)` leaves a log
        # with no unittest result block. Serial `unittest discover` fails
        # such a run (the whole process exits 5); the parallel run must
        # fail too, not pass on a fake `ran no tests` verdict.
        tests_dir = self._project(
            {
                "test_boom.py": (
                    "import os, unittest\n"
                    "\n"
                    "\n"
                    "class TestBoom(unittest.TestCase):\n"
                    "    def test_boom(self):\n"
                    "        os._exit(5)\n"
                ),
                "test_ok.py": OK_MODULE,
            }
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_failed(self, result)
        self.assertIn(
            "===== test_boom: exit 5 but the log shows no unittest "
            "NO TESTS RAN summary =====",
            result.stdout,
        )
        self.assertIn("===== test_ok: exit 0 =====", result.stdout)
        self.assertIn("1 module failed", result.stdout)

    def test_a_forged_no_tests_ran_summary_fails_the_run(self):
        self._assert_forged_summary_fails("")

    def test_an_exit_5_with_only_one_empty_run_marker_fails(self):
        # An import can terminate before unittest prints a verbose test
        # line. Even then, either summary marker alone is insufficient
        # evidence that unittest completed an empty run.
        for marker in ("Ran 0 tests in 0.000s", "NO TESTS RAN"):
            with self.subTest(marker=marker):
                tests_dir = self._project(
                    {
                        "test_partial.py": (
                            "import os\n"
                            f"print({marker!r}, flush=True)\n"
                            "os._exit(5)\n"
                        ),
                        "test_ok.py": OK_MODULE,
                    }
                )
                result = self._run("--tests-dir", tests_dir, "--workers", "2")
                assert_failed(self, result)
                self.assertIn(
                    "===== test_partial: exit 5 but the log shows no unittest "
                    "NO TESTS RAN summary =====",
                    result.stdout,
                )
                self.assertIn("===== test_ok: exit 0 =====", result.stdout)
                self.assertIn("1 module failed", result.stdout)

    def test_a_forged_summary_with_a_test_docstring_fails_the_run(self):
        self._assert_forged_summary_fails('        """An ordinary test description."""\n')

    def test_a_started_test_hidden_before_the_bounded_log_tail_fails(self):
        tests_dir = self._project(
            {
                "test_forge.py": (
                    "import os, sys, unittest\n"
                    "\n\n"
                    "class TestForge(unittest.TestCase):\n"
                    "    def test_forge(self):\n"
                    "        print('x' * 70000, flush=True)\n"
                    "        print('Ran 0 tests in 0.000s\\n\\nNO TESTS RAN', flush=True)\n"
                    "        os._exit(5)\n"
                ),
                "test_ok.py": OK_MODULE,
            }
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_failed(self, result)
        self.assertIn(
            "===== test_forge: exit 5 but the log shows a started test "
            "beside unittest's NO TESTS RAN summary =====",
            result.stdout,
        )

    def _assert_forged_summary_fails(self, docstring):
        # The printed summary is only proof when nothing ran: unittest's
        # verbose runner writes one `test ... (...) ... ` line per test
        # before running it and flushes it, so a log that carries both NO
        # TESTS RAN markers beside such a line shows a test that started --
        # a module whose test prints the markers itself and then dies of
        # its own `os._exit(5)`. Serial `unittest discover` fails that run
        # (the whole process exits 5); the parallel run must fail too, not
        # pass on the forged `ran no tests` verdict.
        tests_dir = self._project(
            {
                "test_forge.py": (
                    "import os, sys, unittest\n"
                    "\n"
                    "\n"
                    "class TestForge(unittest.TestCase):\n"
                    "    def test_forge(self):\n"
                    + docstring +
                    "        print(\n"
                    "            \"\\n\"\n"
                    "            \"-----------------------------------------"
                    "-----------------------------\\n\"\n"
                    "            \"Ran 0 tests in 0.000s\\n\"\n"
                    "            \"\\n\"\n"
                    "            \"NO TESTS RAN\\n\"\n"
                    "        )\n"
                    "        sys.stdout.flush()\n"
                    "        os._exit(5)\n"
                ),
                "test_ok.py": OK_MODULE,
            }
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_failed(self, result)
        self.assertIn(
            "===== test_forge: exit 5 but the log shows a started test "
            "beside unittest's NO TESTS RAN summary =====",
            result.stdout,
        )
        self.assertIn("===== test_ok: exit 0 =====", result.stdout)
        self.assertIn("1 module failed", result.stdout)


if __name__ == "__main__":
    unittest.main()
