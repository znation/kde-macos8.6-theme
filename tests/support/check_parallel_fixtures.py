"""Scratch unittest-module sources the parallel-check tests write into suites.

The coordinator and worker suites run their subprocess workers against tiny
fixture suites built in a scratch tests directory. OK_MODULE sleeps nothing
and passes; SLOW_MODULE and FAILING_MODULE drive queueing and failure
outcomes; OTHER_MODULE names a second module for collision and package
cases. ``_write_module`` puts one source into that directory; the callers
build and name the scratch tree themselves.
"""

from __future__ import annotations

import os


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
