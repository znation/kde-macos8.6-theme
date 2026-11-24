"""Pin the render batch's bookkeeping in ``support.render.renders.Renders``.

The real capture gates run ``Renders``' batch only on a host with the Plasma
tools present, and there the observable failure is a wrong capture, not a
failing unit test: a swapped kind order, a hostile environment dropped from
the calendar-locale render, a shared default timeout that SIGKILLs the
desktop's documented 180 s first start, or a result recorded under the wrong
kind would all pass every unit in the tree. These tests stub
``process_runner.start`` and ``process_runner.finish``, so no render session
is ever started and the batch's own decisions -- which kinds start, in which
order, with which environment and timeout, and what each gate receives -- are
pinned deterministically.
"""

from __future__ import annotations

import atexit
import contextlib
import os
import subprocess
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render import renders as render_renders
from support.render.capture_diagnostics import DiagnosticsRootSteering
from support.render.renders import FreshRendersState, Renders


@contextlib.contextmanager
def _stubbed_runner(finish_raises=None):
    """Stub ``process_runner.start``/``finish`` around a batch run.

    Yields the ``(argv, kwargs)`` list ``start`` received in call order
    and the ``(process, timeout)`` list ``finish`` received. When
    *finish_raises* is given, every ``finish`` call raises it instead of
    answering, so the batch's failure attribution can be probed.
    """
    started = []

    def fake_start(argv, **kwargs):
        started.append((argv, kwargs))
        return mock.Mock(returncode=None, argv=argv)

    finished = []

    def fake_finish(process, timeout=None):
        finished.append((process, timeout))
        if finish_raises is not None:
            raise finish_raises
        # Each session answers with its own capture path and a distinct
        # exit status, so a result filed under the wrong kind shows.
        process.returncode = len(finished)
        return (f"out {process.argv[2]}", f"err {process.argv[2]}")

    with (
        mock.patch.object(
            render_renders.process_runner, "start", side_effect=fake_start
        ),
        mock.patch.object(
            render_renders.process_runner, "finish", side_effect=fake_finish
        ),
    ):
        yield started, finished


class TestRenderBatch(FreshRendersState, unittest.TestCase):
    def setUp(self):
        # The class state is shared with the real gates; swap in a fresh
        # table so the pinned assertions are true whatever ran before this
        # module in the same process, and restore it afterwards.
        self.swap_renders_state_in()

    def tearDown(self):
        self.swap_renders_state_back()

    def _run_with_stubbed_runner(self, *kinds):
        """Request *kinds* and run the batch with a stubbed process runner.

        Returns the ``(argv, kwargs)`` list ``start`` received in call
        order and the ``(process, timeout)`` list ``finish`` received.
        """
        Renders.request(*kinds)
        with _stubbed_runner() as (started, finished):
            Renders._run_all()
        return started, finished

    def test_only_the_requested_kinds_start_and_in_kinds_order(self):
        # The kinds table's order is the start order, not the request order:
        # a worker that requests a late kind must not start its render
        # before the earlier kinds it also waits on.
        started, _ = self._run_with_stubbed_runner("checkbox", "applet")
        self.assertEqual(2, len(started))
        applet, checkbox = started
        self.assertIn("/render.png", applet[0][2])
        self.assertEqual((), tuple(applet[0][3:]))
        self.assertIn("/dialog.png", checkbox[0][2])
        self.assertEqual(("--checkbox-dialog",), tuple(checkbox[0][3:]))

    def test_every_kind_starts_the_render_script_with_captured_output(self):
        started, _ = self._run_with_stubbed_runner("splash")
        argv, kwargs = started[0]
        # The render CLI is started with its capture path and the kind's
        # own flags, and the batch captures what it prints: a failed
        # render's diagnostic is the gate's failure message.
        self.assertEqual(render_renders.SCRIPT, argv[1])
        self.assertTrue(argv[2].endswith("splash.png"))
        self.assertEqual(("--splash",), tuple(argv[3:]))
        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])

    def test_the_calendar_locale_render_starts_from_its_hostile_caller(self):
        # The calendar-locale gate pins a Monday-first day grid, so its
        # render must start under the hostile locale; every other kind
        # inherits this process's environment unchanged (env=None).
        started, _ = self._run_with_stubbed_runner("applet", "calendar_locale")
        by_capture = {
            os.path.basename(argv[2]): kwargs for argv, kwargs in started
        }
        self.assertEqual(
            dict(
                os.environ,
                LANG="de_DE.UTF-8",
                LC_ALL="de_DE.UTF-8",
                LANGUAGE="de",
            ),
            by_capture["dialog.png"]["env"],
        )
        self.assertIsNone(by_capture["render.png"]["env"])

    def test_each_kind_finishes_within_its_own_timeout(self):
        # The desktop render's documented internal timeout is 180 s, so its
        # finish wait is 240 s; the shared dialog wait stays 150 s. A batch
        # that finished every kind at the default would SIGKILL a legitimate
        # slow first plasmashell start.
        _, finished = self._run_with_stubbed_runner("desktop", "splash")
        self.assertEqual(2, len(finished))
        self.assertEqual(240, finished[0][1])
        self.assertEqual(150, finished[1][1])

    def test_each_requested_kind_receives_its_recorded_result(self):
        started, _ = self._run_with_stubbed_runner("checkbox", "splash")
        self.assertEqual({"checkbox", "splash"}, set(Renders.results))
        # KINDS order finishes checkbox first (exit 1), then splash (exit 2).
        for kind, capture, status in (
            ("checkbox", "dialog.png", 1),
            ("splash", "splash.png", 2),
        ):
            stdout, stderr, returncode, directory = Renders.results[kind]
            path = os.path.join(directory, capture)
            self.assertEqual(f"out {path}", stdout)
            self.assertEqual(f"err {path}", stderr)
            self.assertEqual(status, returncode)
            # The directory recorded is the scratch tree the render's
            # capture path was placed in, so a gate reading its output
            # finds it under the same tree the batch cleaned up.
            self.assertTrue(
                os.path.basename(directory).startswith(f"{kind}-render-test-"),
                f"{kind}'s scratch tree lost the batch's prefix: {directory}",
            )

    def test_the_sweep_removes_every_scratch_directory(self):
        self._run_with_stubbed_runner("checkbox", "splash")
        directories = list(Renders.directories.values())
        self.assertEqual(2, len(directories))
        for directory in directories:
            self.assertTrue(os.path.isdir(directory))
        Renders._remove_directories()
        for directory in directories:
            self.assertFalse(
                os.path.exists(directory),
                f"{directory} was not removed by the sweep",
            )

    def test_the_desktop_render_writes_desktop_png(self):
        started, _ = self._run_with_stubbed_runner("desktop")
        argv, _ = started[0]
        self.assertEqual(
            os.path.join(Renders.directories["desktop"], "desktop.png"), argv[2]
        )
        self.assertEqual(("--desktop",), tuple(argv[3:]))

    def test_first_ensure_runs_the_batch_once_and_later_calls_reuse_it(self):
        Renders.request("applet", "checkbox")
        fakes = iter([mock.Mock(returncode=0), mock.Mock(returncode=3)])
        with (
            mock.patch.object(
                render_renders.process_runner,
                "start",
                side_effect=lambda argv, **kwargs: next(fakes),
            ) as started,
            mock.patch.object(
                render_renders.process_runner,
                "finish",
                side_effect=lambda process, timeout=None: ("", ""),
            ),
            mock.patch.object(atexit, "register"),
        ):
            first = Renders.ensure("checkbox")
            second = Renders.ensure("applet")
        self.assertEqual(2, started.call_count)
        self.assertEqual(3, first[2])
        self.assertEqual(0, second[2])

    def test_a_failed_batch_reraises_the_same_error_to_every_later_gate(self):
        Renders.request("applet", "checkbox")
        error = RuntimeError("render batch broke")
        with (
            mock.patch.object(
                render_renders.process_runner, "start", side_effect=error
            ),
            mock.patch.object(render_renders.process_runner, "finish"),
            mock.patch.object(atexit, "register"),
        ):
            with self.assertRaises(RuntimeError) as first:
                Renders.ensure("applet")
            with self.assertRaises(RuntimeError) as second:
                Renders.ensure("checkbox")
        self.assertIs(error, first.exception)
        self.assertIs(error, second.exception)

    def test_a_timed_out_finish_names_the_kind_and_quotes_its_output(self):
        # A hung render dies as a subprocess.TimeoutExpired from finish,
        # carrying whatever output it had printed when it was killed; the
        # batch's failure must name the kind and quote that partial output,
        # not surface a bare timeout to every sibling gate.
        error = subprocess.TimeoutExpired(
            [render_renders.SCRIPT, "capture.png"],
            150,
            output="partial session log\n",
            stderr="partial diagnostic\n",
        )
        Renders.request("checkbox")
        with (
            _stubbed_runner(finish_raises=error),
            mock.patch.object(atexit, "register"),
        ):
            with self.assertRaises(RuntimeError) as raised:
                Renders.ensure("checkbox")
            # A later ensure re-raises the batch's attributable error.
            with self.assertRaises(RuntimeError) as sibling:
                Renders.ensure("checkbox")
        self.assertIs(Renders.failure, raised.exception)
        self.assertIs(Renders.failure, sibling.exception)
        message = str(raised.exception)
        self.assertIn("checkbox", message)
        self.assertIn("dialog.png", message)
        self.assertIn("partial session log", message)
        self.assertIn("partial diagnostic", message)
        self.assertEqual(message, str(sibling.exception))

    def test_a_finish_failure_with_no_output_still_names_the_kind_and_capture(self):
        # A finish failure that carries no partial output (the re-raised
        # timeout when even the reap bound yields no EOF) still names the
        # kind and its capture path, so a failure is attributable.
        error = subprocess.TimeoutExpired([render_renders.SCRIPT, "capture.png"], 150)
        Renders.request("checkbox")
        with (
            _stubbed_runner(finish_raises=error),
            mock.patch.object(atexit, "register"),
        ):
            with self.assertRaises(RuntimeError) as raised:
                Renders.ensure("checkbox")
        message = str(raised.exception)
        self.assertIn("checkbox", message)
        self.assertIn("dialog.png", message)
        self.assertNotIn("render output:", message)

    def test_a_bytes_partial_output_is_decoded_with_replacements(self):
        # A finish exception whose drained pipes are bytes (a non-text
        # exception's output) stays quotable: the message holds the
        # decoded text with an invalid byte spelled as the replacement
        # character, not the bytes' Python repr and not a decode crash.
        error = subprocess.TimeoutExpired(
            [render_renders.SCRIPT, "capture.png"],
            150,
            output=b"broken \xff seed\n",
            stderr=b"partial diagnostic\n",
        )
        Renders.request("checkbox")
        with (
            _stubbed_runner(finish_raises=error),
            mock.patch.object(atexit, "register"),
        ):
            with self.assertRaises(RuntimeError) as raised:
                Renders.ensure("checkbox")
        message = str(raised.exception)
        self.assertIn("checkbox", message)
        self.assertIn("broken \ufffd seed", message)
        self.assertIn("partial diagnostic", message)
        self.assertNotIn("b'broken", message)

    def test_the_attributable_failure_chains_the_original_finish_error(self):
        # The wrapper RuntimeError replaces the finish exception as
        # Renders.failure, so a caller matching the original type must
        # reach it through __cause__; dropping the `from error` chain
        # would strand the underlying exception behind the wrapper.
        error = subprocess.TimeoutExpired([render_renders.SCRIPT, "capture.png"], 150)
        Renders.request("checkbox")
        with (
            _stubbed_runner(finish_raises=error),
            mock.patch.object(atexit, "register"),
        ):
            with self.assertRaises(RuntimeError) as raised:
                Renders.ensure("checkbox")
        self.assertIs(error, raised.exception.__cause__)


class TestFinishFailurePreservesTheCapture(
    DiagnosticsRootSteering, FreshRendersState, unittest.TestCase
):
    """A batch-finish failure preserves the kind's capture, or says there is none.

    The scratch tree is swept at interpreter exit, so the attributable finish
    failure must copy the capture the kind already wrote into the diagnostics
    root and name the copy; a kind that wrote no capture says so instead.
    The diagnostics root is steered into this test's own scratch tree with
    ``TMPDIR``.
    """

    def test_a_finish_failure_names_the_preserved_copys_path(self):
        self.swap_renders_state_in()
        payload = b"\x89PNG capture bytes"
        error = RuntimeError("render batch broke")

        def raising_finish(process, timeout=None):
            # The capture lands in the kind's scratch directory before the
            # failure propagates, exactly as a finished render would leave it.
            with open(
                os.path.join(Renders.directories["checkbox"], "dialog.png"), "wb"
            ) as handle:
                handle.write(payload)
            raise error

        try:
            Renders.request("checkbox")
            with (
                mock.patch.object(
                    render_renders.process_runner,
                    "start",
                    side_effect=lambda argv, **kwargs: mock.Mock(
                        returncode=None, argv=argv
                    ),
                ),
                mock.patch.object(
                    render_renders.process_runner, "finish", side_effect=raising_finish
                ),
            ):
                with self.assertRaises(RuntimeError) as raised:
                    Renders._run_all()
        finally:
            self.swap_renders_state_back()
        message = str(raised.exception)
        self.assertIn("checkbox", message)
        self.assertIn("capture preserved at", message)
        preserved = next(
            line[len("capture preserved at "):]
            for line in message.splitlines()
            if line.startswith("capture preserved at ")
        )
        self.assertTrue(preserved.startswith(self.root))
        with open(preserved, "rb") as handle:
            self.assertEqual(payload, handle.read())

    def test_a_finish_failure_without_a_capture_says_so(self):
        self.swap_renders_state_in()
        error = subprocess.TimeoutExpired([render_renders.SCRIPT, "capture.png"], 150)
        try:
            Renders.request("checkbox")
            with _stubbed_runner(finish_raises=error):
                with self.assertRaises(RuntimeError) as raised:
                    Renders._run_all()
        finally:
            self.swap_renders_state_back()
        message = str(raised.exception)
        self.assertIn("checkbox", message)
        self.assertIn("dialog.png", message)
        self.assertIn("the render wrote no capture", message)
        self.assertNotIn("capture preserved at", message)
        self.assertFalse(os.path.isdir(self.root))


if __name__ == "__main__":
    unittest.main()
