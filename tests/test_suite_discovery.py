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
and are not reported by the check above.

The opposite mistake is guarded too: a file that defines test cases but does
not match ``test*.py`` (say ``png_checks.py``) is never imported by discovery,
so its tests silently never run. The second check loads every other
``tests/*.py`` file and fails naming any that collects test cases.
"""

from __future__ import annotations

import contextlib
import fnmatch
import importlib
import os
import re
import sys
import tempfile
import unittest


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
# The default of the Makefile's CHECK_PATTERN, which `make check` passes to
# `unittest discover -p`. test_discovery_pattern_matches_the_makefile_default
# pins it to the Makefile so the guard cannot silently check a pattern the
# suite no longer runs with.
DISCOVERY_PATTERN = "test*.py"


def makefile_check_pattern():
    """Return the Makefile's literal ``CHECK_PATTERN ?=`` default.

    ``make check`` passes ``$(CHECK_PATTERN)`` to ``unittest discover -p``,
    and this module's guards mirror that discovery with
    :data:`DISCOVERY_PATTERN`. Reading the default from the Makefile lets the
    guard compare against the pattern the suite really uses instead of a
    second copy that could drift. Only the literal right-hand side is read,
    matching ``TestHelp._tunable_defaults``.
    """
    makefile = os.path.join(os.path.dirname(TESTS_DIR), "Makefile")
    with open(makefile, encoding="utf-8") as handle:
        for line in handle:
            match = re.match(r"CHECK_PATTERN\s*\?=(.*)$", line)
            if match:
                return match.group(1).split("#", 1)[0].strip()
    raise AssertionError("Makefile has no `CHECK_PATTERN ?=` default")


def _module_names(directory, predicate):
    """Return the sorted ``.py`` module names in *directory* matching *predicate*.

    Only the directory itself is listed: ``discover -s tests`` does not recurse
    into a subdirectory without an ``__init__.py``, so neither do these guards.
    *predicate* takes a filename and decides whether its module is listed.
    """
    return sorted(
        filename[: -len(".py")]
        for filename in os.listdir(directory)
        if filename.endswith(".py") and predicate(filename)
    )


def test_module_names(directory):
    """Return the ``test*.py`` module names in *directory*, sorted."""
    return _module_names(
        directory, lambda filename: fnmatch.fnmatch(filename, DISCOVERY_PATTERN)
    )


def non_test_module_names(directory):
    """Return the ``tests/*.py`` module names in *directory* the pattern misses.

    These are the modules discovery does not import. The dunder names
    (``__init__``) are excluded: they are package plumbing, not test modules,
    and ``importlib`` cannot import ``__init__`` by that name.
    """
    return _module_names(
        directory,
        lambda filename: not filename.startswith("__")
        and not fnmatch.fnmatch(filename, DISCOVERY_PATTERN),
    )


def _modules_by_test_count(directory, names, want_tests):
    """Return the *names*-listed modules in *directory* with or without tests.

    Each name is imported and loaded with the default loader; *want_tests*
    selects the modules whose loaded suite has at least one case (``True``) or
    none at all (``False``).
    """
    loader = unittest.defaultTestLoader
    found = []
    for name in names(directory):
        module = importlib.import_module(name)
        has_tests = loader.loadTestsFromModule(module).countTestCases() > 0
        if has_tests == want_tests:
            found.append(name)
    return found


def misnamed_test_modules(directory):
    """Return the non-matching module names in *directory* that collect tests.

    A module discovery does not import is only a problem when it defines test
    cases: a helper that holds shared cases (a mixin) collects none and is
    correctly left out, so the check catches exactly the files whose tests
    never run.
    """
    return _modules_by_test_count(directory, non_test_module_names, want_tests=True)


def modules_without_tests(directory):
    """Return the ``test*.py`` module names in *directory* that collect no tests.

    The discovery run has usually imported each name already, so the cached
    module is reused; the loader is the same one ``discover`` uses, so a
    module the loader collects something from is a module the suite runs.
    """
    return _modules_by_test_count(directory, test_module_names, want_tests=False)


@contextlib.contextmanager
def probe_module(directory, filename, source):
    """Import a *source* probe module from *directory*, undoing it on exit.

    The guard-bites tests import a probe by bare name, so they must put its
    directory on ``sys.path`` and drop the module from ``sys.modules`` again;
    writing the file and undoing both is what the two tests share.
    """
    with open(os.path.join(directory, filename), "w", encoding="utf-8") as handle:
        handle.write(source)
    sys.path.insert(0, directory)
    try:
        yield
    finally:
        sys.path.remove(directory)
        sys.modules.pop(filename[: -len(".py")], None)


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

    def test_every_test_case_module_matches_the_discovery_pattern(self):
        names = non_test_module_names(TESTS_DIR)
        # Without this, a broken directory listing would make the assertion
        # below pass vacuously (no modules checked, no misnamed ones found).
        self.assertIn("repo_root", names)
        misnamed = misnamed_test_modules(TESTS_DIR)
        self.assertEqual(
            misnamed,
            [],
            "these tests/*.py modules define test cases but do not match "
            "`make check`'s test*.py discovery pattern, so their tests "
            "silently never run; rename each to test_*.py (or move shared "
            "cases to the repo's *_fixtures.py/_case.py convention): "
            + ", ".join(misnamed),
        )

    def test_discovery_pattern_matches_the_makefile_default(self):
        # `make check` discovers with the Makefile's CHECK_PATTERN; this
        # module's guards use DISCOVERY_PATTERN. If the two disagree, a
        # module the real run misses can slip past the guard, so pin them.
        self.assertEqual(DISCOVERY_PATTERN, makefile_check_pattern())

    def test_a_misnamed_test_module_is_reported(self):
        # Prove the guard bites: a module that collects tests but is not
        # named test*.py is exactly what
        # test_every_test_case_module_matches_the_discovery_pattern must
        # catch. Import it by bare name, then take it back out.
        source = (
            "import unittest\n\n"
            "class TestProbe(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            with probe_module(tmp, "checks_guard_probe.py", source):
                self.assertEqual(
                    misnamed_test_modules(tmp), ["checks_guard_probe"]
                )

    def test_a_test_module_without_tests_is_reported(self):
        # Prove the guard bites: a matched module with no TestCase is exactly
        # what test_every_test_module_contributes_tests must catch. The probe
        # is imported by bare name, so put its directory on sys.path for the
        # call and take both it and its module back out afterwards.
        source = '"""A probe module that defines no tests."""\n'
        with tempfile.TemporaryDirectory() as tmp:
            with probe_module(tmp, "test_empty_guard_probe.py", source):
                self.assertEqual(
                    modules_without_tests(tmp), ["test_empty_guard_probe"]
                )


if __name__ == "__main__":
    unittest.main()
