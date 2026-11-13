"""Tests for tools/check_parallel_workers.py's concurrency bound and durations.

``supervise`` runs each queued module through ``_fill_workers``, which starts
workers only while fewer than ``workers`` are running. These tests drive that
loop on a virtual clock with mocked workers, so the peak number of live
workers is observed exactly and no real subprocess or wall time is involved.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repo root on sys.path)
from tools import check_parallel_workers


class _VirtualRun:
    """A virtual clock plus mocked workers that finish after *duration*."""

    def __init__(self, duration: float) -> None:
        self.duration = duration
        self.now = 0.0
        self.live: set[str] = set()
        self.peak = 0
        self.spawn_order: list[str] = []

    def sleep(self, seconds: float) -> None:
        self.now += seconds

    def spawn(self, module, argv, cwd, log_path, timeout):
        started = self.now
        process = mock.Mock()

        def poll():
            if self.now - started >= self.duration:
                self.live.discard(module)
                return 0
            return None

        process.poll.side_effect = poll
        self.live.add(module)
        self.peak = max(self.peak, len(self.live))
        self.spawn_order.append(module)
        return check_parallel_workers._Worker(
            module, log_path, process, started + 60.0, started
        )

    def supervise(self, modules, workers, durations=None):
        log_paths = {module: f"{module}.log" for module in modules}
        with mock.patch.object(check_parallel_workers, "_spawn",
                               side_effect=self.spawn), \
                mock.patch.object(check_parallel_workers.time, "sleep",
                                  side_effect=self.sleep), \
                mock.patch.object(check_parallel_workers.time, "monotonic",
                                  side_effect=lambda: self.now):
            return check_parallel_workers.supervise(
                modules, [], ".", log_paths, 60, workers, durations=durations,
            )


class TestSuperviseConcurrencyBound(unittest.TestCase):
    """supervise never has more live workers than its --workers bound."""

    def test_two_workers_overlap_but_never_three(self):
        run = _VirtualRun(duration=1.0)
        statuses = run.supervise(["a", "b", "c", "d"], workers=2)
        # The bound is reached (the second worker starts alongside the
        # first) and is never exceeded by the queued third and fourth.
        self.assertEqual(2, run.peak)
        self.assertEqual({"a": 0, "b": 0, "c": 0, "d": 0}, statuses)
        self.assertEqual(["a", "b", "c", "d"], run.spawn_order)

    def test_one_worker_runs_modules_strictly_in_turn(self):
        run = _VirtualRun(duration=1.0)
        statuses = run.supervise(["a", "b", "c"], workers=1)
        self.assertEqual(1, run.peak)
        self.assertEqual({"a": 0, "b": 0, "c": 0}, statuses)

    def test_a_bound_wider_than_the_queue_starts_every_module_at_once(self):
        run = _VirtualRun(duration=1.0)
        run.supervise(["a", "b"], workers=5)
        self.assertEqual(2, run.peak)


class TestSuperviseDurations(unittest.TestCase):
    """Each finished worker's recorded time is its elapsed wall time."""

    def test_each_module_records_at_least_its_run_time(self):
        run = _VirtualRun(duration=1.0)
        durations: dict[str, float] = {}
        run.supervise(["a", "b", "c"], workers=2, durations=durations)
        self.assertEqual({"a", "b", "c"}, set(durations))
        for module, elapsed in durations.items():
            # A worker is seen finished at the first poll on or after its
            # run time, so the record is at least the run time and at most
            # one poll interval beyond it.
            self.assertGreaterEqual(elapsed, 1.0, module)
            self.assertLess(elapsed, 1.02, module)


class TestSuperviseWorkerCountRefusal(unittest.TestCase):
    """supervise refuses a worker count below one instead of idling forever.

    The fill loop starts a worker only while fewer than *workers* are
    running, so with zero workers the queue can never drain: the old code
    span at full CPU with no output until the run was killed from outside.
    The refusal is a ValueError naming the count, so the caller's bug is
    reported where it is visible.
    """

    def _refused(self, workers) -> str:
        with self.assertRaises(ValueError) as caught:
            check_parallel_workers.supervise(
                ["a"], [], ".", {"a": "a.log"}, 60, workers
            )
        return str(caught.exception)

    def test_zero_workers_is_refused_naming_the_count(self):
        message = self._refused(0)
        self.assertIn("supervise() requires a positive integer", message)
        self.assertIn("workers=0", message)

    def test_a_negative_count_is_refused_naming_the_count(self):
        self.assertIn("workers=-2", self._refused(-2))

    def test_a_non_integer_count_is_refused_naming_the_count(self):
        self.assertIn("workers='2'", self._refused("2"))

    def test_true_is_refused_as_the_count_one_it_wraps(self):
        # bool is an int subclass, so True would pass a bare integer check as
        # the worker count 1; the refusal names the bool instead.
        self.assertIn("workers=True", self._refused(True))

    def test_one_worker_still_runs(self):
        # One is the documented minimum (the check CLI's own floor); a
        # refusal message phrased as "more than one" would fail this.
        run = _VirtualRun(duration=1.0)
        self.assertEqual({"a": 0}, run.supervise(["a"], workers=1))


if __name__ == "__main__":
    unittest.main()
