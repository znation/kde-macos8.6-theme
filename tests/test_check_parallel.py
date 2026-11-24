"""Tests for tools/check_parallel.py -- the parallel module coordinator.

`make check` runs this tool by default: each pattern-matched module becomes
one worker process (`python -m unittest -v <module>` from the tests
directory), a bounded number run concurrently, and the coordinator prints
every passing module's captured output in discovery order so the run stays
diffable; failed, timed-out and unfinished modules print after those, with
one ``check:`` line each above the summary.
These tests drive the coordinator against a scratch suite of tiny fixture
modules, so the guarantees -- ordered output, honest exit statuses, a
per-module timeout that kills the worker's whole process group, and
discovery that mirrors `unittest discover`'s package recursion -- are pinned
without running the real suite more than once.

The checks split by the module they cover: ``test_check_parallel_order.py``
pins the durations cache and queue, ``test_check_parallel_results.py`` the
results report, ``test_check_parallel_marker.py`` the started-test marker
scan, ``test_check_parallel_empty_run.py`` the exit-5 empty-run verdicts,
``test_check_parallel_discovery.py`` the module discovery,
and ``test_check_parallel_workers.py`` the worker spawn and clean-up
defenses. The shared scratch module sources live in
``support/check_parallel_fixtures.py``; the coordinator test base class in
``support/check_parallel_coordinator.py``.

The Makefile wiring (the CHECK_PARALLEL variable and its guard) is pinned in
``test_make_check.py``; the suite's own module inventory in
``test_suite_discovery.py``.
"""

from __future__ import annotations

import os
import contextlib
import io
import json
import subprocess
import sys
import time
import unittest
from unittest import mock

from support.check_parallel_fixtures import (
    OK_MODULE,
    SLOW_MODULE,
    FAILING_MODULE,
    OTHER_MODULE,
    _write_module,
    make_package,
    make_suite_dir,
)
from support.check_parallel_coordinator import CoordinatorTestCase
from support.process_assertions import assert_failed, assert_succeeded
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir
from tools import check_parallel
from tools.check import parallel_workers


class TestCoordinator(CoordinatorTestCase):
    """Run the coordinator against scratch suites of fixture modules."""

    def test_a_sandbox_run_saves_under_the_addressed_cache_home(self):
        # Each run resolves its durations cache through the environment's
        # XDG_CACHE_HOME, so a test run over the scratch --tests-dir above
        # cannot reach the real user cache: its save is observed at the
        # addressed home only.
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        result = self._run("--tests-dir", tests_dir)
        assert_succeeded(self, result)
        cache = (
            self.cache_home / "kde-macos8.6-theme" / "check-durations.json"
        )
        self.assertTrue(cache.is_file())
        record = json.loads(cache.read_text(encoding="utf-8"))
        self.assertEqual(["test_ok"], list(record["durations"]))

    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        with mock.patch("tools.diagnostics.tempfile.mkdtemp", side_effect=OSError("denied")):
            result = self._run("--tests-dir", tests_dir)
        self.assertEqual(2, result.returncode)
        self.assertEqual("check: error: cannot create a scratch directory: denied\n", result.stderr)

    def test_scratch_cleanup_failure_names_the_leaked_directory(self):
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        scratch = make_tmp_dir(self) / "worker-scratch"
        scratch.mkdir()
        with (
            mock.patch(
                "tools.check_parallel.create_scratch_directory",
                return_value=scratch,
            ),
            mock.patch(
                "tools.check_parallel.shutil.rmtree",
                side_effect=PermissionError("cleanup denied"),
            ),
        ):
            result = self._run("--tests-dir", tests_dir)
        assert_succeeded(self, result)
        self.assertIn(
            f"check: note: could not remove worker scratch directory {scratch}: "
            "cleanup denied\n",
            result.stderr,
        )

    def test_default_worker_count_falls_back_when_cpu_count_is_unknown(self):
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        with (
            mock.patch("tools.check_parallel.os.cpu_count", return_value=None),
            mock.patch("tools.check_parallel.supervise", return_value={}) as supervise,
            mock.patch("tools.check_parallel.print_results", return_value=0),
        ):
            result = self._run("--tests-dir", tests_dir)

        self.assertEqual(0, result.returncode)
        self.assertIn("1 module, 1 worker", result.stdout)
        self.assertEqual(1, supervise.call_args.args[5])

    def test_duration_cache_write_failure_does_not_fail_the_run(self):
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        with (
            mock.patch("tools.check_parallel.supervise", return_value={"test_ok": 0}),
            mock.patch("tools.check_parallel.save_durations", side_effect=OSError("read-only")),
            mock.patch("tools.check_parallel.print_results", return_value=0),
        ):
            result = self._run("--tests-dir", tests_dir)

        self.assertEqual(0, result.returncode)
        self.assertIn("could not record module durations for the next run: read-only", result.stderr)

    def test_duration_cache_error_escapes_terminal_controls(self):
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        with (
            mock.patch("tools.check_parallel.supervise", return_value={"test_ok": 0}),
            mock.patch(
                "tools.check_parallel.save_durations",
                side_effect=OSError("denied\x1b[2J"),
            ),
            mock.patch("tools.check_parallel.print_results", return_value=0),
        ):
            result = self._run("--tests-dir", tests_dir)

        self.assertEqual(0, result.returncode)
        self.assertNotIn("\x1b", result.stderr)
        self.assertIn(r"could not record module durations for the next run: denied\u001b[2J", result.stderr)

    def test_an_unlistable_test_directory_exits_2_without_a_traceback(self):
        # Discovery reads a directory the coordinator does not control: a
        # subdirectory swept away or permission-locked between the isdir
        # check and the walk, or one hidden by a foreign owner, raises
        # OSError (PermissionError) from os.listdir. A bare traceback would
        # abort the run naming neither the directory nor the error; the
        # shared exit-2 diagnostic names both, and nothing has run, so
        # neither the module list nor the tree has been touched.
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        unreadable = make_package(tests_dir, "gone")
        real_scandir = os.scandir

        def guarded_scandir(directory):
            if os.path.samefile(directory, unreadable):
                raise PermissionError(13, "Permission denied")
            return real_scandir(directory)

        with mock.patch(
            "tools.check.parallel_discovery.os.scandir",
            side_effect=guarded_scandir,
        ):
            result = self._run("--tests-dir", tests_dir)
        self.assertEqual(2, result.returncode)
        self.assertEqual(
            f"check: error: cannot list {unreadable}: [Errno 13] Permission denied\n",
            result.stderr,
        )
        self.assertEqual("", result.stdout)

    def test_finished_worker_hands_off_within_ten_milliseconds(self):
        # Virtual time excludes scheduler/spawn noise. Instant workers make
        # the coordinator's own sleep the only source of hand-off delay.
        now = 0.0
        starts = []

        def sleep(seconds):
            nonlocal now
            now += seconds

        def spawn(module, argv, cwd, log_path, timeout):
            starts.append(now)
            process = mock.Mock()
            process.poll.return_value = 0
            return parallel_workers._Worker(
                module, log_path, process, now + timeout, now
            )

        with mock.patch.object(parallel_workers, "_spawn", side_effect=spawn), \
                mock.patch.object(parallel_workers.time, "sleep", side_effect=sleep), \
                mock.patch.object(parallel_workers.time, "monotonic", side_effect=lambda: now):
            statuses = parallel_workers.supervise(
                ["first", "second"], [], ".",
                {"first": "first.log", "second": "second.log"}, 60, 1,
            )

        self.assertEqual({"first": 0, "second": 0}, statuses)
        self.assertEqual(2, len(starts))
        self.assertLessEqual(starts[1] - starts[0], 0.010)

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

    def test_an_unopenable_log_records_its_module_and_keeps_the_run(self):
        # _spawn opens the worker's log before the worker starts; an open
        # that fails (a scratch volume that filled mid-run, or a log path a
        # concurrent sweep removed) used to unwind supervise as a bare
        # traceback, losing the report of every module that had already
        # finished. Now the module is recorded as never started, one stderr
        # diagnostic names it and the OS error, and the other workers still
        # run and report.
        tests_dir = self._project({"test_ok.py": OK_MODULE, "test_two.py": OK_MODULE})
        missing = make_tmp_dir(self) / "missing-dir"
        log_paths = {
            "test_ok": str(missing / "worker.log"),
            "test_two": str(make_tmp_dir(self) / "worker.log"),
        }
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            statuses = parallel_workers.supervise(
                ["test_ok", "test_two"],
                [sys.executable, "-m", "unittest", "-v"],
                tests_dir,
                log_paths,
                60,
                2,
            )
        self.assertEqual(1, statuses["test_ok"])
        self.assertEqual(0, statuses["test_two"])
        stderr_text = stderr.getvalue()
        self.assertIn("cannot open the worker log for test_ok", stderr_text)
        self.assertIn(str(missing), stderr_text)

    def test_an_unopenable_log_reports_its_module_as_a_failure(self):
        # End to end through main: the poisoned log path is recorded as the
        # module's unreadable-log failure and the run exits 1 with the
        # diagnostic on stderr, never as a traceback killing the run.
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        missing = make_tmp_dir(self) / "missing-dir"
        with mock.patch.object(
            check_parallel,
            "assign_log_paths",
            side_effect=lambda modules, scratch: {
                module: str(missing / f"{module}.log") for module in modules
            },
        ):
            result = self._run("--tests-dir", tests_dir)
        assert_failed(self, result)
        self.assertIn(
            "cannot open the worker log for test_ok", result.stderr
        )
        self.assertIn(
            "===== test_ok: worker log could not be read =====", result.stdout
        )
        self.assertNotIn("Traceback", result.stderr)

    def test_fifo_worker_log_fails_without_blocking(self):
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        fifo = make_tmp_dir(self) / "worker.log"
        os.mkfifo(fifo)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            statuses = parallel_workers.supervise(
                ["test_ok"], [sys.executable, "-m", "unittest", "-v"],
                tests_dir, {"test_ok": str(fifo)}, 60, 1,
            )
        self.assertEqual({"test_ok": 1}, statuses)
        self.assertTrue(stderr.getvalue().startswith(
            "check: error: cannot open the worker log for test_ok: "
        ))

    def test_modules_with_the_same_log_stem_get_distinct_logs(self):
        # A package's `test_a.test_b` module and a top-level
        # `test_a_test_b.py` both match the default pattern, and both dotted
        # names collapse to one _-joined log stem (`test_a_test_b`): two
        # workers opening one log file truncate and interleave each other's
        # output while the result sections print that one file twice, so
        # each module gets a uniquely named log and its own section prints
        # only its own output.
        tests_dir = make_suite_dir(self)
        package = make_package(tests_dir, "test_a")
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
                # Sorts after test_boom, so its header follows the
                # unterminated boom log in the failed group.
                "test_zz_bad.py": FAILING_MODULE,
            }
        )
        result = self._run("--tests-dir", tests_dir, "--workers", "2")
        assert_failed(self, result)
        self.assertIn("===== test_boom: exit 1 =====", result.stdout)
        self.assertIn("===== test_ok: exit 0 =====", result.stdout)
        # The later section's header starts a line of its own: the
        # unterminated boom log never runs into it.
        self.assertIn("\n===== test_zz_bad: exit 1 =====", result.stdout)
        self.assertIn("2 modules failed", result.stdout)

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
        # The worker's output spans several lines that stay lines: a log
        # escaped without its real line breaks would fold the section into
        # one blob of `\u000a` escapes instead of a readable traceback.
        self.assertNotIn(r"\u000a", result.stdout)
        self.assertIn("Ran 1 test in", result.stdout)

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
        with mock.patch.object(
            check_parallel, "discover_modules", wraps=check_parallel.discover_modules
        ) as discover:
            result = self._run(
                "--tests-dir", tests_dir, "-p", "test_one.py", "--workers", "1"
            )
        assert_succeeded(self, result)
        discover.assert_called_once_with(tests_dir)
        self.assertIn("check: -p 'test_one.py', 1 module, 1 worker", result.stdout)
        self.assertIn("===== test_one: exit 0 =====", result.stdout)
        self.assertNotIn("test_two", result.stdout)

    def test_a_package_subdirectory_module_gets_its_dotted_name(self):
        # Discovery recurses into packages and imports them under their
        # dotted name, exactly as `unittest discover` does; the worker must
        # receive that same dotted name and the section must use it.
        tests_dir = self._project({"test_top.py": OK_MODULE})
        package = make_package(tests_dir, "probe_pkg")
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
        # The refusal rides the shared exit-2 diagnostic contract, like the
        # coordinator's other usage errors, so its line carries ``error:``.
        self.assertIn("check: error: -p 'test_none*.py' matches no test module",
                      result.stderr)
        self.assertIn(tests_dir, result.stderr)

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
        # The refusal rides the shared exit-2 diagnostic contract, like the
        # coordinator's other usage errors, so its line carries ``error:``.
        self.assertIn("check: error: --tests-dir must name a directory",
                      result.stderr)
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
