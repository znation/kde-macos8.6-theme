"""Base class for the parallel-check coordinator tests.

``tools/check_parallel.py`` runs against scratch suites of fixture modules.
``CoordinatorTestCase`` holds the setup the coordinator test classes share: an
isolated durations cache, a scratch suite writer and a runner for the
coordinator's ``main``. The module sources live in
``check_parallel_fixtures.py``.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support.check_parallel_fixtures import _write_module, make_suite_dir
from support.cli_fixtures import run_main
from support.tmp_dir import make_tmp_dir
from tools import check_parallel


class CoordinatorTestCase(unittest.TestCase):
    """Scratch-suite helpers shared by the coordinator's test classes."""


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

    def _project(self, files: dict[str, str]) -> str:
        """Write a scratch suite and return its tests directory."""
        tests_dir = make_suite_dir(self)
        for name, source in files.items():
            _write_module(tests_dir, name, source)
        return tests_dir

    def _run(self, *args):
        return run_main(check_parallel.main, "tools/check_parallel.py", args)
