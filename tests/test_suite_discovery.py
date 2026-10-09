"""Guard that every ``tests/test*.py`` module actually contributes tests.

``make check`` runs ``python3 -m unittest discover -s tests -p 'test*.py'``.
Discovery imports every module the pattern matches, but a matched module that
defines no :class:`unittest.TestCase` yields an empty suite and is silently
skipped: the run stays green while the file's tests, if the author meant it to
have any, never execute. This module imports each pattern-matched file through
the loader and fails naming the ones that collect nothing.

Helper modules that hold shared cases but are not discovered themselves use the
repository's other naming conventions (``*_fixtures.py``, ``*_case.py``,
``*_assertions.py``, ``package_metadata.py``), so they do not match ``test*.py``
and are not reported here.
"""

from __future__ import annotations

import fnmatch
import importlib
import os
import sys
import tempfile
import unittest


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
# The default of the Makefile's CHECK_PATTERN, which `make check` passes to
# `unittest discover -p`.
DISCOVERY_PATTERN = "test*.py"


def test_module_names(directory):
    """Return the ``test*.py`` module names in *directory*, sorted.

    Only the directory itself is listed: ``discover -s tests`` does not recurse
    into a subdirectory without an ``__init__.py``, so neither does this guard.
    """
    return sorted(
        filename[: -len(".py")]
        for filename in os.listdir(directory)
        if filename.endswith(".py") and fnmatch.fnmatch(filename, DISCOVERY_PATTERN)
    )


def modules_without_tests(directory):
    """Return the ``test*.py`` module names in *directory* that collect no tests.

    Each name is imported (the discovery run has usually imported it already,
    so the cached module is reused) and loaded with the default loader; a
    module whose loaded suite has zero cases is reported. The loader is the
    same one ``discover`` uses, so a module the loader collects something from
    is a module the suite runs.
    """
    loader = unittest.defaultTestLoader
    empty = []
    for name in test_module_names(directory):
        module = importlib.import_module(name)
        if loader.loadTestsFromModule(module).countTestCases() == 0:
            empty.append(name)
    return empty


class TestSuiteDiscovery(unittest.TestCase):
    def test_every_test_module_contributes_tests(self):
        names = test_module_names(TESTS_DIR)
        # Without this, a broken directory listing would make the assertion
        # below pass vacuously (no modules checked, no empties found).
        self.assertIn("test_suite_discovery", names)
        empty = modules_without_tests(TESTS_DIR)
        self.assertEqual(
            empty,
            [],
            "these tests/test*.py modules define no test cases, so `make "
            "check` silently runs nothing from them; give each a "
            "unittest.TestCase (or rename a pure helper to the repo's "
            "*_fixtures.py/_case.py convention): "
            + ", ".join(empty),
        )

    def test_a_test_module_without_tests_is_reported(self):
        # Prove the guard bites: a matched module with no TestCase is exactly
        # what test_every_test_module_contributes_tests must catch. The probe
        # is imported by bare name, so put its directory on sys.path for the
        # call and take both it and its module back out afterwards.
        with tempfile.TemporaryDirectory() as tmp:
            probe = os.path.join(tmp, "test_empty_guard_probe.py")
            with open(probe, "w", encoding="utf-8") as handle:
                handle.write('"""A probe module that defines no tests."""\n')
            sys.path.insert(0, tmp)
            try:
                self.assertEqual(
                    modules_without_tests(tmp), ["test_empty_guard_probe"]
                )
            finally:
                sys.path.remove(tmp)
                sys.modules.pop("test_empty_guard_probe", None)


if __name__ == "__main__":
    unittest.main()
