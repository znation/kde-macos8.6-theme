"""Tests for tools/check_parallel_order.py and the coordinator's use of it.

`make check` runs 175 modules over a bounded worker budget, and one suite
(the real render surface) alone runs for seconds while most modules finish
in far less than one. The coordinator therefore queues the slowest recorded
module first -- durations come from the previous run's completion times,
persisted in a small best-effort JSON cache -- so the critical path starts
covered by workers instead of starting after roughly a batch of shorter
modules. Everything about the cache is best-effort: a missing, malformed or
unwritable file must never fail a run or change the results' discovery
order.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from unittest import mock
from pathlib import Path

from support.cli_fixtures import run_main
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir
from support.fifo_fixtures import make_fifo

from tools import check_parallel, check_parallel_order, check_parallel_workers

OK_MODULE = (
    "import unittest\n"
    "\n"
    "\n"
    "class TestOk(unittest.TestCase):\n"
    "    def test_runs(self):\n"
    "        pass\n"
)

SLEEPER_MODULE = (
    "import time, unittest\n"
    "\n"
    "\n"
    "class TestSlow(unittest.TestCase):\n"
    "    def test_runs(self):\n"
    "        time.sleep(0.3)\n"
)


class TestOrder(unittest.TestCase):
    """The ordering decision over a duration mapping."""

    def test_the_slowest_recorded_module_is_queued_first(self):
        modules = ["test_ok", "test_render", "test_other"]
        self.assertEqual(
            ["test_render", "test_ok", "test_other"],
            check_parallel_order.order_modules(
                modules, {"test_render": 10.8, "test_ok": 0.1},
            ),
        )

    def test_unrecorded_modules_keep_discovery_order_among_themselves(self):
        # A stable sort: modules with no recorded duration (no cache, or a
        # module the previous run never reached) stay in discovery order
        # relative to each other.
        modules = ["test_a", "test_b", "test_c"]
        self.assertEqual(
            modules, check_parallel_order.order_modules(modules, {}),
        )
        self.assertEqual(
            # Equal durations stay in discovery order too.
            ["test_z", "test_render"],
            check_parallel_order.order_modules(
                ["test_z", "test_render"],
                {"test_render": 0.5, "test_z": 0.5},
            ),
        )


class TestCache(unittest.TestCase):
    """The durations cache's best-effort load and save."""

    def test_a_cache_round_trips_through_save_and_load(self):
        path = str(make_tmp_dir(self) / "nested" / "cache.json")
        check_parallel_order.save_durations(
            path, {"test_render": 10.75, "test_ok": 0.1},
        )
        self.assertEqual(
            {"test_render": 10.75, "test_ok": 0.1},
            check_parallel_order.load_durations(path),
        )

    def test_a_missing_or_malformed_cache_loads_nothing(self):
        for contents in (
            "", "not json", "[1, 2]", '{"version": 1}', "{}",
            '{"version": true, "durations": {"test_ok": 0.5}}',
        ):
            path = str(make_tmp_dir(self) / "cache.json")
            with open(path, "wb") as sink:
                sink.write(contents.encode("utf-8"))
            self.assertEqual({}, check_parallel_order.load_durations(path))
        self.assertEqual({}, check_parallel_order.load_durations("/missing/cache.json"))

    def test_deeply_nested_json_cache_loads_nothing(self):
        path = make_tmp_dir(self) / "cache.json"
        path.write_text("[" * 10000 + "0" + "]" * 10000, encoding="utf-8")
        self.assertEqual({}, check_parallel_order.load_durations(str(path)))

    def test_a_fifo_cache_does_not_block_the_coordinator(self):
        path = make_tmp_dir(self) / "cache.json"
        make_fifo(self, path)
        # A timeout bounds this regression test: opening the FIFO normally
        # blocks forever in the coordinator before any worker can start.
        result = subprocess.run(
            [sys.executable, "-c",
             "from tools.check_parallel_order import load_durations; "
             "assert load_durations(__import__('sys').argv[1]) == {}",
             str(path)],
            cwd=str(Path(__file__).resolve().parents[1]),
            capture_output=True, text=True, timeout=3,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_an_oversize_cache_is_ignored(self):
        path = make_tmp_dir(self) / "cache.json"
        path.write_bytes(b" " * (check_parallel_order._MAX_CACHE_BYTES + 1))
        self.assertEqual({}, check_parallel_order.load_durations(str(path)))

    def test_non_numeric_or_invalid_entries_are_ignored(self):
        path = str(make_tmp_dir(self) / "cache.json")
        with open(path, "w", encoding="utf-8") as sink:
            json.dump(
                {"version": 1, "durations": {
                    "test_ok": 0.5, "test_nan": "yesterday",
                    "test_neg": -1, "test_list": [1],
                    "test_nan_float": float("nan"),
                    "test_pos_inf": float("inf"),
                    "test_neg_inf": float("-inf"),
                    # bool is an int subclass in Python, but JSON booleans
                    # are not measured wall durations and must not affect
                    # the worker queue order.
                    "test_bool": True,
                }},
                sink,
            )
        self.assertEqual(
            {"test_ok": 0.5}, check_parallel_order.load_durations(path),
        )

    def test_an_integer_too_large_for_float_conversion_is_ignored(self):
        path = make_tmp_dir(self) / "cache.json"
        path.write_text(
            '{"version":1,"durations":{"test_ok":0.5,"test_huge":'
            + "9" * 400
            + "}}",
            encoding="utf-8",
        )
        self.assertEqual(
            {"test_ok": 0.5},
            check_parallel_order.load_durations(str(path)),
        )

    def test_a_merge_keeps_the_entries_the_run_did_not_touch(self):
        # A narrower run must not erase the durations a full run left for
        # the modules it skipped: they are what keeps the next full run's
        # slowest-first queue from falling back to alphabetical order.
        path = str(make_tmp_dir(self) / "cache.json")
        check_parallel_order.save_durations(
            path, {"test_ok": 0.1, "test_render": 24.0},
        )
        self.assertEqual(
            {"test_ok": 0.2, "test_render": 24.0},
            check_parallel_order.merge_durations(
                path, {"test_ok": 0.2}, {"test_ok", "test_render"},
            ),
        )

    def test_a_merge_drops_entries_for_modules_absent_from_the_tree(self):
        path = str(make_tmp_dir(self) / "cache.json")
        check_parallel_order.save_durations(
            path, {"test_ok": 0.1, "test_gone": 4.0},
        )
        self.assertEqual(
            {"test_ok": 0.2},
            check_parallel_order.merge_durations(
                path, {"test_ok": 0.2}, {"test_ok"},
            ),
        )

    def test_a_merge_treats_a_missing_or_malformed_cache_as_empty(self):
        for contents in ("", "not json", '{"version": 1}'):
            path = str(make_tmp_dir(self) / "cache.json")
            with open(path, "wb") as sink:
                sink.write(contents.encode("utf-8"))
            self.assertEqual(
                {"test_ok": 0.5},
                check_parallel_order.merge_durations(
                    path, {"test_ok": 0.5}, {"test_ok", "test_other"},
                ),
            )
        self.assertEqual(
            {"test_ok": 0.5},
            check_parallel_order.merge_durations(
                "/missing/cache.json", {"test_ok": 0.5}, {"test_ok"},
            ),
        )

    def test_the_cache_lives_under_the_absolute_xdg_cache_home(self):
        with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": "/abs/cache"}):
            self.assertEqual(
                "/abs/cache/kde-macos8.6-theme/check-durations.json",
                check_parallel_order.cache_path(),
            )
        # An unset, empty or relative XDG_CACHE_HOME falls back to ~/.cache,
        # as the XDG base directory spec requires.
        for absent in (None, "", "relative/cache"):
            environ = {} if absent is None else {"XDG_CACHE_HOME": absent}
            with mock.patch.dict(os.environ, environ, clear=True):
                self.assertEqual(
                    os.path.join(
                        os.path.expanduser("~"), ".cache",
                        "kde-macos8.6-theme", "check-durations.json",
                    ),
                    check_parallel_order.cache_path(),
                )


class TestDurationsRecorded(unittest.TestCase):
    """_supervise records each finished module's elapsed wall time."""

    def _supervise(self, tests_dir, modules, log_paths, timeout, workers):
        durations: dict[str, float] = {}
        statuses = check_parallel_workers._supervise(
            modules, [sys.executable, "-m", "unittest", "-v"],
            tests_dir, log_paths, timeout, workers, durations=durations,
        )
        return statuses, durations

    def test_each_finished_module_records_its_elapsed_wall(self):
        # The recorded value covers the module's own run (the fixture sleeps
        # 0.3s) plus its spawn, which is the worker time the next run's
        # ordering should steer around.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        for name, source in (("test_ok.py", OK_MODULE),
                             ("test_slow.py", SLEEPER_MODULE)):
            with open(os.path.join(tests_dir, name), "w", encoding="utf-8") as sink:
                sink.write(source)
        log_paths = {
            module: os.path.join(tests_dir, f"{module}.log")
            for module in ("test_ok", "test_slow")
        }
        statuses, durations = self._supervise(
            tests_dir, ["test_ok", "test_slow"], log_paths, 30, 2,
        )
        self.assertEqual({"test_ok": 0, "test_slow": 0}, statuses)
        self.assertGreaterEqual(durations["test_slow"], 0.3)
        self.assertLess(durations["test_slow"], 30)
        self.assertLess(durations["test_ok"], 30)

    def test_a_never_started_module_records_nothing(self):
        # The unopenable-log case records the module as never started; with
        # no worker time to report, it contributes no duration and the next
        # run keeps it (and everything else) in discovery order.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        with open(os.path.join(tests_dir, "test_ok.py"), "w",
                  encoding="utf-8") as sink:
            sink.write(OK_MODULE)
        missing = make_tmp_dir(self) / "missing-dir" / "worker.log"
        with mock.patch("sys.stderr"):
            statuses, durations = self._supervise(
                tests_dir, ["test_ok"],
                {"test_ok": str(missing)}, 30, 2,
            )
        self.assertEqual({"test_ok": 1}, statuses)
        self.assertEqual({}, durations)


class TestCoordinatorUsesTheCache(unittest.TestCase):
    """End to end: the cache steers the queue and the run stays healthy."""

    def _project(self, files: dict[str, str]) -> str:
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        for name, source in files.items():
            with open(os.path.join(tests_dir, name), "w",
                      encoding="utf-8") as sink:
                sink.write(source)
        return tests_dir

    def _run(self, *args):
        return run_main(check_parallel.main, "tools/check_parallel.py", args)

    def test_a_prior_cache_queues_the_slowest_module_first(self):
        tests_dir = self._project(
            {"test_aaa_ok.py": OK_MODULE, "test_zzz_ok.py": OK_MODULE}
        )
        cache_dir = make_tmp_dir(self) / "cache"
        cache = cache_dir / "kde-macos8.6-theme" / "check-durations.json"
        cache.parent.mkdir(parents=True, exist_ok=True)
        with open(cache, "w", encoding="utf-8") as sink:
            json.dump(
                {"version": 1, "durations": {"test_zzz_ok": 9.9}}, sink,
            )
        seen: dict[str, list[str]] = {}
        real = check_parallel._supervise

        def spy(modules, *args, **kwargs):
            seen["modules"] = list(modules)
            return real(modules, *args, **kwargs)

        with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": str(cache_dir)}):
            with mock.patch.object(check_parallel, "_supervise", spy):
                result = self._run("--tests-dir", tests_dir)
        assert_succeeded(self, result)
        # Discovery order is alphabetical, so without the cache the first
        # queue entry would be the aaa module; a recorded duration for the
        # zzz module queues it first instead.
        self.assertEqual(["test_zzz_ok", "test_aaa_ok"], seen["modules"])
        # The results still print in discovery order whatever the queue was.
        self.assertLess(
            result.stdout.index("===== test_aaa_ok"),
            result.stdout.index("===== test_zzz_ok"),
        )

    def test_a_targeted_run_keeps_its_sibling_modules_recorded_durations(self):
        # A run over a narrower pattern records its own module without
        # erasing the entries a full run left for the modules it did not
        # run: erasing them would send the next full run (this one's
        # distribution of long and short modules) back to alphabetical
        # ordering. A module removed from the tree still leaves no entry.
        tests_dir = self._project(
            {"test_aaa_ok.py": OK_MODULE, "test_zzz_ok.py": OK_MODULE}
        )
        cache_dir = make_tmp_dir(self) / "cache"
        cache = cache_dir / "kde-macos8.6-theme" / "check-durations.json"
        cache.parent.mkdir(parents=True, exist_ok=True)
        with open(cache, "w", encoding="utf-8") as sink:
            json.dump(
                {"version": 1,
                 "durations": {"test_zzz_ok": 9.9, "test_gone": 4.0}},
                sink,
            )
        with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": str(cache_dir)}):
            result = self._run(
                "--tests-dir", tests_dir, "-p", "test_aaa*.py",
            )
        assert_succeeded(self, result)
        record = json.loads(cache.read_text(encoding="utf-8"))
        self.assertEqual(
            9.9, record["durations"]["test_zzz_ok"],
        )
        self.assertGreater(record["durations"]["test_aaa_ok"], 0.0)
        self.assertEqual(
            {"test_aaa_ok", "test_zzz_ok"}, set(record["durations"]),
        )

    def test_a_run_rewrites_the_cache_with_its_own_modules(self):
        # The save drops entries whose modules left the tree -- a renamed
        # or removed test module -- and records every module that ran, so
        # the file cannot grow beyond the tree.
        tests_dir = self._project({"test_ok.py": OK_MODULE})
        cache_dir = make_tmp_dir(self) / "cache"
        cache = cache_dir / "kde-macos8.6-theme" / "check-durations.json"
        cache.parent.mkdir(parents=True, exist_ok=True)
        with open(cache, "w", encoding="utf-8") as sink:
            json.dump(
                {"version": 1,
                 "durations": {"test_gone": 4.0, "test_ok": 0.1}},
                sink,
            )
        with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": str(cache_dir)}):
            result = self._run("--tests-dir", tests_dir)
        assert_succeeded(self, result)
        record = json.loads(cache.read_text(encoding="utf-8"))
        self.assertEqual({"version": 1, "durations": {"test_ok": record["durations"]["test_ok"]}}, record)
        self.assertGreater(record["durations"]["test_ok"], 0.0)


if __name__ == "__main__":
    unittest.main()
