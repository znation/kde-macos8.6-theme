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

The checks split by the module they cover: ``test_check_parallel_order.py``
pins the durations cache and queue, ``test_check_parallel_results.py`` the
results report, ``test_check_parallel_discovery.py`` the module discovery,
and ``test_check_parallel_workers.py`` the worker spawn and clean-up
defenses. The shared scratch module sources live in
``support/check_parallel_fixtures.py``.

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
)
from support.cli_fixtures import run_main
from support.process_assertions import assert_failed, assert_succeeded
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir
from tools import check_parallel, check_parallel_workers


class TestCoordinator(unittest.TestCase):
    """Run the coordinator against scratch suites of fixture modules."""

    def setUp(self):
        # Address every run's durations cache at a scratch home: a sandbox
        # suite's save must not rewrite the developer's real user cache,
        # whose recorded durations the next full run's queue orders by (the
        # coordinator prunes entries whose modules are absent from
        # --tests-dir, so a one-module sandbox tree's save used to leave
        # that real cache holding one module of 317).
        self.cache_home = make_tmp_dir(self) / "cache"
        cache = mock.patch.dict(
            os.environ, {"XDG_CACHE_HOME": str(self.cache_home)}
        )
        cache.start()
        self.addCleanup(cache.stop)

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
            status = check_parallel.print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": "/missing/worker.log"}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", output.getvalue())
        self.assertIn("1 module failed", output.getvalue())

    def test_fifo_worker_log_read_fails_without_blocking(self):
        fifo = make_tmp_dir(self) / "worker.log"
        os.mkfifo(fifo)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel.print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(fifo)}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", output.getvalue())
        self.assertIn("1 module failed", output.getvalue())

    def test_a_fifo_started_test_scan_fails_without_blocking(self):
        fifo = make_tmp_dir(self) / "worker.log"
        os.mkfifo(fifo)
        # An exit-5 log with a complete NO TESTS RAN summary reaches the
        # started-test scan, so the bounded tail read must see a regular file
        # and a FIFO substituted before that scan still fails the module: the
        # scan's plain open() used to block on the pipe with no writer.
        with mock.patch(
            "tools.check_parallel_results._bounded_log_text",
            return_value="Ran 0 tests\nNO TESTS RAN\n",
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = check_parallel.print_results(
                    ["test_ok"], {"test_ok": 5}, {"test_ok": str(fifo)}, 10
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
        unreadable = os.path.join(tests_dir, "gone")
        os.mkdir(unreadable)
        _write_module(unreadable, "__init__.py", "")
        real_listdir = os.listdir

        def guarded_listdir(directory):
            if os.path.samefile(directory, unreadable):
                raise PermissionError(13, "Permission denied")
            return real_listdir(directory)

        with mock.patch(
            "tools.check_parallel_discovery.os.listdir",
            side_effect=guarded_listdir,
        ):
            result = self._run("--tests-dir", tests_dir)
        self.assertEqual(2, result.returncode)
        self.assertEqual(
            f"check: error: cannot list {unreadable}: [Errno 13] Permission denied\n",
            result.stderr,
        )
        self.assertEqual("", result.stdout)

    def test_missing_worker_status_reports_did_not_finish_and_keeps_log(self):
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_text("partial worker output\n", encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel.print_results(
                ["test_ok"], {}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("===== test_ok: did not finish =====", output.getvalue())
        self.assertIn("partial worker output", output.getvalue())
        self.assertIn("1 module not finished", output.getvalue())

    def test_a_flooded_log_prints_a_bounded_tail_with_a_hidden_byte_note(self):
        """A log past the printed section's cap keeps only its tail.

        A worker killed at its timeout while flooding its log can leave a
        file far larger than the tail worth reading: the section reads only
        the last window, opens it on a line break, and names the hidden
        bytes on a leading note line instead of loading and echoing the
        whole flood (whose MemoryError would never be the OSError the
        unreadable-log case catches, killing the whole results report).
        """
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"x" * 100_000 + b"\n" + b"tail line\n" + b"Ran 1 test in 0.001s\n\nOK\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel.print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        text = output.getvalue()
        self.assertEqual(0, status)
        # The flood is gone from the printout: a window cut at 64 KiB falls
        # inside the x-run, and everything through the flood line's break
        # (the partial line the window opens on) is dropped with it.
        self.assertNotIn("x" * 65_536, text)
        self.assertNotIn("x" * 55_000, text)
        self.assertLess(len(text), 100_000)
        # The truncation is named, not silent, and the log's own tail survives.
        self.assertIn(
            "===== test_ok: exit 0 =====\ncheck: ",
            text,
        )
        self.assertIn("earlier log bytes hidden; showing the last ", text)
        self.assertIn("tail line\n", text)
        self.assertIn("Ran 1 test in 0.001s", text)
        self.assertIn("\nOK\n", text)

    def test_a_flooded_log_keeps_its_end_of_log_summary_verdict(self):
        """The exit-5 summary check still sees unittest's end-of-log summary.

        unittest prints its ``Ran 0 tests``/``NO TESTS RAN`` summary at the
        very end of the worker log, so the bounded tail window always holds
        both markers: a flooded log must not misreport a genuinely empty run
        as one without an exit-5 verdict.
        """
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(
            # A realistic flood: the summary follows the flood's own line
            # break, as unittest's summary always ends a line it started.
            b"x" * 100_000
            + b"\n"
            + b"Ran 0 tests in 0.000s\n\nNO TESTS RAN\n"
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel.print_results(
                ["test_ok"], {"test_ok": 5}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        self.assertIn(
            "===== test_ok: ran no tests (unittest's NO TESTS RAN, exit 5) =====",
            output.getvalue(),
        )

    def test_invalid_utf8_in_worker_log_is_replaced(self):
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"worker output: \xff\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel.print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        self.assertIn("worker output: \ufffd", output.getvalue())

    def test_a_window_without_any_line_break_is_shown_whole(self):
        # A worker killed while writing one continuous line can leave a log
        # whose whole tail window carries no newline at all: there is no
        # break to open on, so the note must still account every byte
        # exactly -- the window is shown whole (65536) and the difference
        # from the file's size is named -- instead of dropping the tail.
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"x" * 100_000)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel.print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        self.assertIn(
            "check: 34464 earlier log bytes hidden; showing the last 65536",
            output.getvalue(),
        )
        self.assertIn("x" * 65_536, output.getvalue())

    def test_crlf_worker_log_lines_end_before_the_line_breaks(self):
        # The bounded read replaced a text-mode whole-file read, whose
        # universal newlines folded CRLF and bare CR into LF. A CRLF
        # worker log must still read as one line per record after the
        # switch to the binary bounded read -- not as one line carrying
        # literal carriage returns.
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"line one\r\nline two\r\nRan 1 test in 0.001s\n\nOK\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_parallel.print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        text = output.getvalue()
        self.assertIn("line one\nline two\n", text)
        self.assertNotIn("line one\r", text)
        self.assertNotIn("\u000d", text)

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
            return check_parallel_workers._Worker(
                module, log_path, process, now + timeout, now
            )

        with mock.patch.object(check_parallel_workers, "_spawn", side_effect=spawn), \
                mock.patch.object(check_parallel_workers.time, "sleep", side_effect=sleep), \
                mock.patch.object(check_parallel_workers.time, "monotonic", side_effect=lambda: now):
            statuses = check_parallel_workers.supervise(
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
            statuses = check_parallel_workers.supervise(
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
            statuses = check_parallel_workers.supervise(
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
            status = check_parallel.print_results(
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
            status = check_parallel.print_results(
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
            status = check_parallel.print_results(
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
            status = check_parallel.print_results(
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
