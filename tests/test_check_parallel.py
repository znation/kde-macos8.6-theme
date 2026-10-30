"""Tests for tools/check_parallel.py -- the parallel module coordinator.

`make check` runs this tool by default: each pattern-matched module becomes
one worker process (`python -m unittest -v <module>` from the tests
directory), a bounded number run concurrently, and the coordinator prints
every module's captured output in discovery order so the run stays diffable.
These tests drive the coordinator against a scratch suite of tiny fixture
modules, so the guarantees -- ordered output, honest exit statuses, a
per-module timeout that kills the worker's whole process group, and
discovery that mirrors `unittest discover`'s package recursion -- are pinned
without running the real suite more than once.

The Makefile wiring (the CHECK_PARALLEL variable and its guard) is pinned in
``test_make_check.py``; the suite's own module inventory in
``test_suite_discovery.py``.
"""

from __future__ import annotations

import os
import contextlib
import io
import signal
import subprocess
import sys
import time
import unittest
from unittest import mock

from support.cli_fixtures import run_main
from support.process_assertions import assert_failed, assert_succeeded
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir

from tools import (
    check_parallel,
    check_parallel_discovery,
    check_parallel_workers,
    process_group,
)

# A passing one-test module and variants the coordinator's outcomes need.
OK_MODULE = (
    "import unittest\n"
    "\n"
    "\n"
    "class TestOk(unittest.TestCase):\n"
    "    def test_ok(self):\n"
    "        self.assertTrue(True)\n"
)
SLOW_MODULE = (
    "import time\n"
    "import unittest\n"
    "\n"
    "\n"
    "class TestSlow(unittest.TestCase):\n"
    "    def test_ok(self):\n"
    "        time.sleep(0.5)\n"
    "        self.assertTrue(True)\n"
)
FAILING_MODULE = (
    "import unittest\n"
    "\n"
    "\n"
    "class TestFails(unittest.TestCase):\n"
    "    def test_fails(self):\n"
    "        self.assertTrue(False)\n"
)
OTHER_MODULE = (
    "import unittest\n"
    "\n"
    "\n"
    "class TestOther(unittest.TestCase):\n"
    "    def test_also(self):\n"
    "        self.assertTrue(True)\n"
)


def _write_module(tests_dir, name, source):
    """Write one fixture module into the scratch suite."""
    with open(os.path.join(tests_dir, name), "w", encoding="utf-8") as handle:
        handle.write(source)


class TestCoordinator(unittest.TestCase):
    """Run the coordinator against scratch suites of fixture modules."""

    def _project(self, files: dict[str, str]) -> str:
        """Write a scratch suite and return its tests directory."""
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        for name, source in files.items():
            _write_module(tests_dir, name, source)
        return tests_dir

    def _run(self, *args):
        return run_main(check_parallel.main, "tools/check_parallel.py", args)

    def test_missing_worker_log_fails_even_when_worker_exited_zero(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel._print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": "/missing/worker.log"}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", output.getvalue())
        self.assertIn("1 module failed", output.getvalue())

    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        with mock.patch("tools.diagnostics.tempfile.mkdtemp", side_effect=OSError("denied")):
            result = self._run("--tests-dir", tests_dir)
        self.assertEqual(2, result.returncode)
        self.assertEqual("check: error: cannot create a scratch directory: denied\n", result.stderr)

    def test_missing_worker_status_reports_did_not_finish_and_keeps_log(self):
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_text("partial worker output\n", encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel._print_results(
                ["test_ok"], {}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("===== test_ok: did not finish =====", output.getvalue())
        self.assertIn("partial worker output", output.getvalue())
        self.assertIn("1 module not finished", output.getvalue())

    def test_invalid_utf8_in_worker_log_is_replaced(self):
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"worker output: \xff\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel._print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        self.assertIn("worker output: \ufffd", output.getvalue())

    def test_every_module_runs_and_output_is_ordered(self):
        # Both modules pass; the coordinator prints one section per module
        # in discovery order even though the alphabetically later module
        # finishes first while both workers overlap.
        tests_dir = self._project(
            {"test_aaa_slow.py": SLOW_MODULE, "test_zzz_fast.py": OK_MODULE}
        )
        started = time.monotonic()
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_succeeded(self, result)
        # Two concurrent workers: the run's wall is the slow module, not the
        # sum of both.
        self.assertLess(time.monotonic() - started, 2.0)
        self.assertIn("check: -p 'test*.py', 2 modules, 2 workers", result.stdout)
        self.assertLess(
            result.stdout.index("===== test_aaa_slow"),
            result.stdout.index("===== test_zzz_fast"),
        )
        self.assertIn("exit 0", result.stdout)
        self.assertIn("Ran 1 test in", result.stdout)

    def test_modules_with_the_same_log_stem_get_distinct_logs(self):
        # A package's `test_a.test_b` module and a top-level
        # `test_a_test_b.py` both match the default pattern, and both dotted
        # names collapse to one _-joined log stem (`test_a_test_b`): two
        # workers opening one log file truncate and interleave each other's
        # output while the result sections print that one file twice, so
        # each module gets a uniquely named log and its own section prints
        # only its own output.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        package = os.path.join(tests_dir, "test_a")
        os.mkdir(package)
        _write_module(package, "__init__.py", "")
        _write_module(package, "test_b.py", OK_MODULE)
        _write_module(tests_dir, "test_a_test_b.py", OTHER_MODULE)
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_succeeded(self, result)
        package_section = result.stdout[
            result.stdout.index("===== test_a.test_b:")
            :result.stdout.index("===== test_a_test_b:")
        ]
        top_section = result.stdout[result.stdout.index("===== test_a_test_b:") :]
        self.assertIn("test_a.test_b.TestOk", package_section)
        self.assertIn("test_a_test_b.TestOther", top_section)
        self.assertNotIn("test_a_test_b.TestOther", package_section)
        self.assertNotIn("test_a.test_b.TestOk", top_section)

    def test_a_module_with_no_tests_does_not_fail_the_run(self):
        # unittest exits 5 (NO TESTS RAN) when a module's run collects no
        # tests, on Python 3.12 and later. The serial discover run gets
        # nothing from such a module and still passes, so the parallel run
        # passes too: the section says `ran no tests` instead of failing
        # with a bare `exit 5` while the other modules' results stand.
        tests_dir = self._project(
            {"test_empty.py": "import unittest\n", "test_ok.py": OK_MODULE}
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_succeeded(self, result)
        self.assertIn(
            "===== test_empty: ran no tests (unittest's NO TESTS RAN, "
            "exit 5) =====",
            result.stdout,
        )
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

    def test_an_unterminated_log_never_merges_with_the_next_section(self):
        # A worker that dies mid-print (an `os._exit(1)` inside a test, with
        # the verbose runner's `... ` partial line the last thing it wrote)
        # leaves a log whose last line never ends. The next section's header
        # printed verbatim after it would glue the two onto one line, and the
        # run's sections stop being diffable, so a log not ending in a break
        # is closed with one.
        tests_dir = self._project(
            {
                "test_boom.py": (
                    "import os, unittest\n"
                    "\n"
                    "\n"
                    "class TestBoom(unittest.TestCase):\n"
                    "    def test_boom(self):\n"
                    "        os._exit(1)\n"
                ),
                "test_ok.py": OK_MODULE,
            }
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_failed(self, result)
        self.assertIn("===== test_boom: exit 1 =====", result.stdout)
        self.assertIn("===== test_ok: exit 0 =====", result.stdout)
        # The later section's header starts a line of its own: the
        # unterminated boom log never runs into it.
        self.assertIn("\n===== test_ok: exit 0 =====", result.stdout)
        self.assertIn("1 module failed", result.stdout)

    def test_a_failing_module_fails_the_run_with_its_output(self):
        tests_dir = self._project(
            {"test_ok_one.py": OK_MODULE, "test_bad_two.py": FAILING_MODULE}
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_failed(self, result)
        self.assertIn("===== test_ok_one: exit 0 =====", result.stdout)
        self.assertIn("===== test_bad_two: exit 1 =====", result.stdout)
        # The failure's traceback reaches the reader through the captured
        # worker output, not just a status.
        self.assertIn("AssertionError", result.stdout)
        self.assertIn("1 module failed", result.stdout)

    def test_mixed_empty_and_failed_modules_report_both_outcomes(self):
        empty_log = make_tmp_dir(self) / "empty.log"
        empty_log.write_text(
            "Ran 0 tests in 0.000s\n\nNO TESTS RAN\n", encoding="utf-8"
        )
        failed_log = make_tmp_dir(self) / "failed.log"
        failed_log.write_text("failure detail\n", encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel._print_results(
                ["test_empty", "test_failed"],
                {"test_empty": 5, "test_failed": 1},
                {"test_empty": str(empty_log), "test_failed": str(failed_log)},
                10,
            )
        self.assertEqual(1, status)
        self.assertIn("test_empty: ran no tests", output.getvalue())
        self.assertIn("test_failed: exit 1", output.getvalue())
        self.assertIn(
            "check: 2 modules, 1 module failed, 1 module ran no tests",
            output.getvalue(),
        )

    def test_summary_combines_failed_timed_out_and_unfinished_modules(self):
        failed_log = make_tmp_dir(self) / "failed.log"
        failed_log.write_text("failure detail\n", encoding="utf-8")
        timeout_log = make_tmp_dir(self) / "timeout.log"
        timeout_log.write_text("partial output\n", encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel._print_results(
                ["test_failed", "test_timeout", "test_unfinished"],
                {"test_failed": 1, "test_timeout": None},
                {"test_failed": str(failed_log), "test_timeout": str(timeout_log)},
                2,
            )
        self.assertEqual(1, status)
        rendered = output.getvalue()
        self.assertIn("test_failed: exit 1", rendered)
        self.assertIn("test_timeout: timed out after 2s (process group killed)", rendered)
        self.assertIn("test_unfinished: did not finish", rendered)
        self.assertIn(
            "check: 3 modules, 1 module failed, 1 module timed out, "
            "1 module not finished",
            rendered,
        )

    def test_summary_counts_multiple_failed_workers_including_a_signal_exit(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel._print_results(
                ["test_failed", "test_signalled"],
                {"test_failed": 1, "test_signalled": -9},
                {},
                10,
            )
        rendered = output.getvalue()
        self.assertEqual(1, status)
        self.assertIn("test_failed: exit 1", rendered)
        self.assertIn("test_signalled: exit -9", rendered)
        self.assertIn("check: 2 modules, 2 modules failed", rendered)

    def test_summary_counts_empty_module_alongside_a_timeout(self):
        empty_log = make_tmp_dir(self) / "empty.log"
        empty_log.write_text(
            "Ran 0 tests in 0.000s\n\nNO TESTS RAN\n", encoding="utf-8"
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel._print_results(
                ["test_empty", "test_timeout"],
                {"test_empty": 5, "test_timeout": None},
                {"test_empty": str(empty_log)},
                3,
            )
        self.assertEqual(1, status)
        rendered = output.getvalue()
        self.assertIn("test_empty: ran no tests", rendered)
        self.assertIn(
            "test_timeout: timed out after 3s (process group killed)", rendered
        )
        self.assertIn(
            "check: 2 modules, 1 module timed out, 1 module ran no tests",
            rendered,
        )

    def test_worker_terminal_controls_are_escaped_before_replay(self):
        tests_dir = self._project(
            {
                "test_output.py": (
                    "import unittest\n"
                    "class TestOutput(unittest.TestCase):\n"
                    "    def test_output(self):\n"
                    "        print('before\\x1b[2Jafter')\n"
                )
            }
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "1")
        assert_succeeded(self, result)
        self.assertNotIn("\x1b", result.stdout)
        self.assertIn(r"before\u001b[2Jafter", result.stdout)

    def test_a_timeout_kills_the_workers_whole_process_group(self):
        # The fixture records its spawned child's pid, sleeps past the
        # timeout, and is killed on the group; the child must be dead too,
        # not left running behind the coordinator.
        tests_dir = self._project({"test_hangs.py": OK_MODULE})
        pid_file = os.path.join(tests_dir, "child.pid")
        _write_module(
            tests_dir,
            "test_hangs.py",
            (
                "import os, subprocess, time, unittest\n"
                "\n"
                "\n"
                "class TestHang(unittest.TestCase):\n"
                "    def test_hangs(self):\n"
                "        child = subprocess.Popen(['sleep', '60'])\n"
                f"        with open({pid_file!r}, 'w') as handle:\n"
                "            handle.write(str(child.pid))\n"
                "        time.sleep(60)\n"
            ),
        )
        started = time.monotonic()
        result = self._run(
            "--tests-dir", tests_dir, "--timeout", "2", "--workers", "1"
        )
        wall = time.monotonic() - started
        assert_failed(self, result)
        # The run ends at the timeout, not when the sleeping fixture ends.
        self.assertLess(wall, 15.0)
        self.assertIn("timed out after 2s (process group killed)", result.stdout)
        # The group kill reached the fixture's own child: reading its pid
        # and finding no live process proves the descendant did not survive.
        with open(pid_file, encoding="utf-8") as handle:
            child_pid = int(handle.read())
        for _ in range(40):
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                break
            else:
                time.sleep(0.05)
        else:
            self.fail(f"the timed-out module's child {child_pid} is still alive")
        self.assertIn("1 module timed out", result.stdout)

    def test_a_pattern_narrows_the_run(self):
        tests_dir = self._project(
            {"test_one.py": OK_MODULE, "test_two.py": OK_MODULE}
        )
        result = self._run(
            "--tests-dir", tests_dir, "-p", "test_one.py", "--workers", "1"
        )
        assert_succeeded(self, result)
        self.assertIn("check: -p 'test_one.py', 1 module, 1 worker", result.stdout)
        self.assertIn("===== test_one: exit 0 =====", result.stdout)
        self.assertNotIn("test_two", result.stdout)

    def test_a_package_subdirectory_module_gets_its_dotted_name(self):
        # Discovery recurses into packages and imports them under their
        # dotted name, exactly as `unittest discover` does; the worker must
        # receive that same dotted name and the section must use it.
        tests_dir = self._project({"test_top.py": OK_MODULE})
        package = os.path.join(tests_dir, "probe_pkg")
        os.mkdir(package)
        _write_module(package, "__init__.py", "")
        _write_module(package, "test_probe.py", OK_MODULE)
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_succeeded(self, result)
        self.assertIn("===== probe_pkg.test_probe: exit 0 =====", result.stdout)
        self.assertIn("===== test_top: exit 0 =====", result.stdout)

    def test_a_pattern_matching_no_module_is_refused(self):
        # The Makefile guard refuses a typo'd glob before the run; the tool
        # itself must refuse it too, for direct callers, with a diagnostic
        # naming the pattern and the directory.
        tests_dir = self._project({"test_one.py": OK_MODULE})
        result = self._run("--tests-dir", tests_dir, "-p", "test_none*.py")
        assert_failed(self, result)
        self.assertIn("matches no test module", result.stderr)
        self.assertIn("test_none*.py", result.stderr)

    def test_pattern_control_characters_are_escaped_in_diagnostic(self):
        tests_dir = self._project({"test_one.py": OK_MODULE})
        pattern = "missing\x1b[31m*.py"
        result = self._run("--tests-dir", tests_dir, "-p", pattern)
        assert_failed(self, result)
        self.assertIn(r"missing\u001b[31m*.py", result.stderr)
        self.assertNotIn("\x1b", result.stderr)

    def test_a_missing_tests_directory_is_refused(self):
        result = self._run("--tests-dir", os.path.join(str(make_tmp_dir(self)), "absent"))
        assert_failed(self, result)
        self.assertIn("--tests-dir must name a directory", result.stderr)
        self.assertIn("absent", result.stderr)
    def test_a_non_positive_worker_count_is_refused(self):
        tests_dir = self._project({"test_one.py": OK_MODULE})
        result = self._run("--tests-dir", tests_dir, "--workers", "0")
        assert_failed(self, result)
        self.assertIn("--workers must be at least 1", result.stderr)

    def test_a_non_positive_timeout_is_refused(self):
        tests_dir = self._project({"test_one.py": OK_MODULE})
        result = self._run("--tests-dir", tests_dir, "--timeout", "0")
        assert_failed(self, result)
        self.assertIn("--timeout must be at least 1", result.stderr)

    def test_a_module_that_cannot_be_imported_fails_only_its_module(self):
        # A fixture module with a syntax error makes its worker's unittest
        # exit non-zero; the module is reported as failed with the error,
        # the other modules still run and report their own results, and the
        # run fails.
        tests_dir = self._project(
            {"test_one.py": OK_MODULE, "test_broken.py": "def broken(:\n"}
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_failed(self, result)
        self.assertIn("===== test_one: exit 0 =====", result.stdout)
        self.assertIn("===== test_broken: exit 1 =====", result.stdout)
        self.assertIn("SyntaxError", result.stdout)


class TestSpawnDefenses(unittest.TestCase):
    """The spawn/kill primitives keep the guarantees test_process_group pins.

    ``tools/process_group.py::run_logged`` defers SIGTERM, SIGHUP and Ctrl-C
    around its child's start and never signals a non-positive pid; _spawn
    and _kill_group are the same primitive for the coordinator's workers, so
    the same behavior is pinned here.
    """

    def test_kill_group_ignores_a_worker_that_never_started(self):
        # A _NeverStarted worker has pid 0, and os.killpg(0, ...) signals the
        # coordinator's own process group -- under `make check`, make's
        # jobserver. The guard must reach no signal at all.
        with mock.patch.object(check_parallel_workers.os, "killpg") as killpg:
            check_parallel_workers._kill_group(
                check_parallel_workers._NeverStarted()
            )
        killpg.assert_not_called()

    def _spawn_while_popen_signals(self, number, raises):
        """Signal the coordinator *number* while Popen returns; spawn a sleeper.

        Returns the started worker's pid -- kill -0 proves whether the
        deferral machinery killed its group on the way out.
        """
        real_popen = subprocess.Popen
        child = {}

        def popen_then_signal(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            child["pid"] = process.pid
            os.kill(os.getpid(), number)
            return process

        def kill_child():
            pid = child.get("pid")
            if pid is not None:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass

        self.addCleanup(kill_child)
        log_path = str(make_tmp_dir(self) / "spawn.log")
        with mock.patch.object(
            check_parallel_workers.subprocess, "Popen", side_effect=popen_then_signal
        ):
            with self.assertRaises(raises) as caught:
                with process_group.exit_on_termination():
                    check_parallel_workers._spawn(
                        "test_probe",
                        [sys.executable, "-c", "import time; time.sleep(60)"],
                        str(ROOT),
                        log_path,
                        30,
                    )
        return child["pid"], caught.exception

    def test_a_sigterm_while_popen_returns_still_kills_the_worker(self):
        # Without the deferral, exit_on_termination's handler raises
        # SystemExit before the worker is appended to the supervised set, so
        # the finally block never saw it: the worker outlived the
        # coordinator. The replay must arrive only after _spawn's own kill
        # and reap have run, and with the shell-convention exit code.
        pid, exception = self._spawn_while_popen_signals(
            signal.SIGTERM, SystemExit
        )
        self.assertEqual(128 + signal.SIGTERM, exception.code)
        self.assertTrue(_gone(pid))

    def test_a_sigint_while_popen_returns_still_kills_the_worker(self):
        # Ctrl-C's default handler raises KeyboardInterrupt at the next
        # bytecode; deferred and replayed inside _spawn's cleanup, it must
        # still take the worker's group down on the way out.
        pid, _ = self._spawn_while_popen_signals(
            signal.SIGINT, KeyboardInterrupt
        )
        self.assertTrue(_gone(pid))


def _gone(pid):
    """Return True once *pid* no longer exists, waiting up to five seconds."""
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.02)
    return False


class TestDiscovery(unittest.TestCase):
    """The module discovery mirrors `unittest discover`'s semantics."""

    def test_names_top_level_modules_in_sorted_order(self):
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        for name in ("test_b.py", "test_a.py", "helper.py"):
            _write_module(tests_dir, name, OK_MODULE)
        self.assertEqual(
            ["test_a", "test_b"],
            check_parallel_discovery.discover_modules(tests_dir, "test*.py"),
        )

    def test_non_package_directories_are_not_recursed(self):
        # discover recurses into a subdirectory only when it is a package;
        # a test*.py file under a plain directory stays invisible, as
        # test_suite_discovery's guard documents for the real suite.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        plain = os.path.join(tests_dir, "plain")
        os.mkdir(plain)
        _write_module(plain, "test_hidden.py", OK_MODULE)
        package = os.path.join(tests_dir, "shown_pkg")
        os.mkdir(package)
        _write_module(package, "__init__.py", "")
        _write_module(package, "test_shown.py", OK_MODULE)
        self.assertEqual(
            ["shown_pkg.test_shown"],
            check_parallel_discovery.discover_modules(tests_dir, "test*.py"),
        )

    def test_symlinked_package_directories_are_not_recursed(self):
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        outside = os.path.join(os.path.dirname(tests_dir), "outside_pkg")
        os.mkdir(outside)
        _write_module(outside, "__init__.py", "")
        _write_module(outside, "test_outside.py", OK_MODULE)
        os.symlink(outside, os.path.join(tests_dir, "linked_pkg"))
        self.assertEqual(
            [], check_parallel_discovery.discover_modules(tests_dir, "test*.py")
        )


    def test_files_unittest_cannot_load_are_skipped(self):
        # unittest discovery gates every file on VALID_MODULE_NAME (a valid
        # Python identifier ending in .py) before the pattern match, so a
        # stray testaux.pyz under a broad pattern is not the module
        # "testaux.", and a hyphenated test-x.py under the default pattern is
        # not the module "test-x": discovery skips both, and a worker fed
        # either name would import nothing or fail the run.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        _write_module(tests_dir, "test_ok.py", OK_MODULE)
        _write_module(tests_dir, "testaux.pyz", "not python\n")
        _write_module(tests_dir, "test-x.py", OK_MODULE)
        self.assertEqual(
            ["test_ok"], check_parallel_discovery.discover_modules(tests_dir, "test*")
        )
        self.assertEqual(
            ["test_ok"],
            check_parallel_discovery.discover_modules(tests_dir, "test*.py"),
        )


    def test_modules_sharing_one_log_stem_get_unique_paths(self):
        # The dotted module name becomes one _-joined log stem, and two
        # distinct modules can share it: the package module `test_a.test_b`
        # and the top-level `test_a_test_b.py` both give `test_a_test_b`,
        # so the coordinator must not derive the log path from the stem
        # alone.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        package = os.path.join(tests_dir, "test_a")
        os.mkdir(package)
        _write_module(package, "__init__.py", "")
        _write_module(package, "test_b.py", OK_MODULE)
        _write_module(tests_dir, "test_a_test_b.py", OTHER_MODULE)
        modules = check_parallel_discovery.discover_modules(tests_dir, "test*.py")
        self.assertEqual(["test_a.test_b", "test_a_test_b"], modules)
        paths = check_parallel_discovery._log_paths(modules, "/scratch")
        self.assertEqual(2, len(set(paths.values())))

    def test_a_disambiguated_log_never_claims_another_modules_name(self):
        # The `_2` suffix must not collide with a third module's own natural
        # stem: `test_a_test_b_2` keeps its natural log, and the later
        # colliding module takes the next free suffix.
        paths = check_parallel_discovery._log_paths(
            ["test_a.test_b", "test_a_test_b_2", "test_a_test_b"],
            "/scratch",
        )
        self.assertEqual(3, len(set(paths.values())))
        self.assertTrue(
            paths["test_a_test_b_2"].endswith("test_a_test_b_2.log")
        )


class TestScriptEntryPoint(unittest.TestCase):
    """The CLI still runs end to end as ``python3 tools/check_parallel.py``."""

    def test_script_entry_point(self):
        # One real narrow run through the script wrapper: it covers the
        # `if __name__ == "__main__": sys.exit(main())` line and the direct
        # run's import path without paying a whole suite run.
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_parallel.py"),
             "-p", "test_byteops.py"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("-p 'test_byteops.py', 1 module, ", result.stdout)
        self.assertIn("===== test_byteops: exit 0 =====", result.stdout)


if __name__ == "__main__":
    unittest.main()
