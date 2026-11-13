"""Pin the render batch's bookkeeping in ``support.render_gates.Renders``.

The real capture gates run ``Rends``' batch only on a host with the Plasma
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

import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import render_gates
from support.render_gates import Renders


class TestRenderBatch(unittest.TestCase):
    def setUp(self):
        # The class state is shared with the real gates; swap in a fresh
        # table so the pinned assertions are true whatever ran before this
        # module in the same process, and restore it afterwards.
        self._saved = (
            Renders.requested,
            Renders.directories,
            Renders.results,
            Renders.completed,
            Renders.failure,
        )
        Renders.requested = set()
        Renders.directories = {}
        Renders.results = {}
        Renders.completed = False
        Renders.failure = None

    def tearDown(self):
        (
            Renders.requested,
            Renders.directories,
            Renders.results,
            Renders.completed,
            Renders.failure,
        ) = self._saved

    def _run_with_stubbed_runner(self, *kinds):
        """Request *kinds* and run the batch with a stubbed process runner.

        Returns the ``(argv, kwargs)`` list ``start`` received in call
        order and the ``(process, timeout)`` list ``finish`` received.
        """
        started = []

        def fake_start(argv, **kwargs):
            started.append((argv, kwargs))
            return mock.Mock(returncode=None)

        finished = []

        def fake_finish(process, timeout=None):
            finished.append((process, timeout))
            process.returncode = 0
            return ("out", "err")

        Renders.request(*kinds)
        with (
            mock.patch.object(
                render_gates.process_runner, "start", side_effect=fake_start
            ),
            mock.patch.object(
                render_gates.process_runner, "finish", side_effect=fake_finish
            ),
        ):
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
        self.assertEqual(render_gates.SCRIPT, argv[1])
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
                **Renders.HOSTILE_ENVIRONMENTS["calendar_locale"],
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
        for kind in ("checkbox", "splash"):
            stdout, stderr, returncode, directory = Renders.results[kind]
            self.assertEqual("out", stdout)
            self.assertEqual("err", stderr)
            self.assertEqual(0, returncode)
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


if __name__ == "__main__":
    unittest.main()
