"""Guard that every ``tests/test*.py`` module actually contributes tests.

``make check`` discovers its modules with the filename glob in the Makefile's
``CHECK_PATTERN ?=`` (default ``test*.py``) and runs them through the parallel
coordinator ``tools/check_parallel.py``, whose worker runs each module the
same way ``unittest discover -s tests -p 'test*.py'`` imports it; the same
discovery semantics therefore decide both the coordinator's and the serial
fallback's (`make check CHECK_PARALLEL=0`) module set.

Discovery imports every module the pattern matches, but a matched module that
defines no :class:`unittest.TestCase` yields an empty suite and is silently
skipped: the run stays green while the file's tests, if the author meant it to
have any, never execute. This module imports each pattern-matched file through
the loader and fails naming the ones that collect nothing.

Helper modules that hold shared cases but are not discovered themselves live in
the ``tests/support/`` package (and the ``tests/svg_assertions/`` package),
including the ``invariants`` and ``placeholders`` register checkers, so they do
not match ``test*.py`` and are not reported by the check above.

The opposite mistake is guarded too: a file that defines test cases but does
not match ``test*.py`` (say ``png_checks.py``) is never imported by discovery,
so its tests silently never run. The second check loads every other
``tests/**/*.py`` file and fails naming any that collects test cases.

A third mistake is guarded: ``discover`` recurses into a subdirectory only
when it is a package (one holding ``__init__.py``), so a ``test*.py`` file
inside a plain subdirectory is never imported either. The third check walks
the same tree and fails naming each such file.
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
from unittest import mock

from support import containment
from support.repo_root import ROOT
from support.symlink_fixtures import symlinked_repo
from support.tmp_dir import make_tmp_dir


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
# The default of the Makefile's CHECK_PATTERN, which `make check` passes to
# `unittest discover -p`. test_discovery_pattern_matches_the_makefile_default
# pins it to the Makefile so the guard cannot silently check a pattern the
# suite no longer runs with.
DISCOVERY_PATTERN = "test*.py"

# A minimal probe module that defines one passing test. The two
# misnamed-module guards below import it under a name discovery never
# matches, so they need a module that would contribute tests; an empty one
# would not prove the same.
PROBE_TEST_MODULE_SOURCE = (
    "import unittest\n\n"
    "class TestProbe(unittest.TestCase):\n"
    "    def test_ok(self):\n"
    "        self.assertTrue(True)\n"
)


def makefile_check_pattern():
    """Return the Makefile's literal ``CHECK_PATTERN ?=`` default.

    ``make check`` passes ``$(CHECK_PATTERN)`` to ``unittest discover -p``,
    and this module's guards mirror that discovery with
    :data:`DISCOVERY_PATTERN`. Reading the default from the Makefile lets the
    guard compare against the pattern the suite really uses instead of a
    second copy that could drift. Only the literal right-hand side is read,
    matching ``test_make_help.TestHelp._tunable_defaults``.
    """
    makefile = os.path.join(ROOT, "Makefile")
    # The Makefile is contributor-supplied, and a checked-in symlink at its
    # path can point at a private file. The default this returns reaches the
    # ``assertEqual`` in test_discovery_pattern_matches_the_makefile_default,
    # whose failure echoes both values, so a path that resolves outside the
    # repository is refused before it is opened.
    text = containment.read_text(makefile, ROOT, encoding="utf-8")
    for line in text.splitlines():
        match = re.match(r"CHECK_PATTERN\s*\?=(.*)$", line)
        if match:
            return match.group(1).split("#", 1)[0].strip()
    raise AssertionError("Makefile has no `CHECK_PATTERN ?=` default")


class TestMakefileReadContainment(unittest.TestCase):
    """The Makefile read refuses a symlink that escapes the repository."""

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "Makefile", "CHECK_PATTERN ?= private-*.py\n"
            )
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    makefile_check_pattern()
        self.assertIn(str(link), str(caught.exception))
        self.assertNotIn("private-*.py", str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = symlinked_repo(
                tmp,
                "Makefile",
                "CHECK_PATTERN ?= test*.py\n",
                target="actual.mk",
            )
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                self.assertEqual(makefile_check_pattern(), "test*.py")


def _is_package(directory):
    """Return True when *directory* is a package ``discover`` recurses into."""
    return os.path.isfile(os.path.join(directory, "__init__.py"))


def _module_names(directory, predicate, prefix=""):
    """Return the sorted dotted module names under *directory* matching *predicate*.

    ``discover -s tests`` recurses into every subdirectory that is a package
    (one holding ``__init__.py``), importing each module the pattern matches,
    so these guards walk the same tree. A module inside a package is named by
    its dotted path (``svg_assertions.pixels``); *prefix* is the dotted name of
    the package *directory* sits in and is empty at the top level. *predicate*
    takes a filename and decides whether its module is listed.
    """
    names = []
    for entry in sorted(os.listdir(directory)):
        full = os.path.join(directory, entry)
        if entry.endswith(".py"):
            if predicate(entry):
                names.append(prefix + entry[: -len(".py")])
        elif _is_package(full):
            names.extend(_module_names(full, predicate, prefix + entry + "."))
    return sorted(names)


def test_module_names(directory):
    """Return the ``test*.py`` module names in *directory*, sorted."""
    return _module_names(
        directory, lambda filename: fnmatch.fnmatch(filename, DISCOVERY_PATTERN)
    )


def non_test_module_names(directory):
    """Return the non-``test*.py`` module names under *directory*, sorted.

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


def _skipped_test_modules(directory, prefix, hidden):
    """Return the discovery-skipped ``test*.py`` files below *directory*.

    *prefix* is the path of *directory* relative to the walk's start, ending
    in ``os.sep`` (empty at the start). *hidden* becomes True once the walk
    enters a directory discovery does not recurse into; every ``test*.py``
    below it is then reported, including one inside a package nested under
    the non-package directory, which discovery never reaches either.
    """
    names = []
    for entry in sorted(os.listdir(directory)):
        full = os.path.join(directory, entry)
        if entry.endswith(".py"):
            if hidden and fnmatch.fnmatch(entry, DISCOVERY_PATTERN):
                names.append(prefix + entry)
        elif os.path.isdir(full) and entry != "__pycache__":
            names.extend(
                _skipped_test_modules(
                    full,
                    prefix + entry + os.sep,
                    hidden or not _is_package(full),
                )
            )
    return names


def skipped_test_modules(directory):
    """Return the ``test*.py`` files under *directory* discovery never imports.

    ``discover`` recurses into a subdirectory only when it is a package (one
    holding ``__init__.py``), so a ``test*.py`` file inside a directory that
    is not a package is never imported and its tests silently never run. The
    returned names are each file's path relative to *directory*, so the
    diagnostic can name the file to move or the ``__init__.py`` to add.
    """
    return sorted(_skipped_test_modules(directory, "", False))


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


@contextlib.contextmanager
def probe_package(directory, package, modules):
    """Create *package* under *directory* from *modules*, undoing it on exit.

    The package's ``__init__.py`` is created empty. *modules* maps a filename
    inside the package to its source. The guard walks packages the way
    ``discover`` does, so a probe lives in one; the dotted names it imports are
    dropped from ``sys.modules`` again on exit.
    """
    package_dir = os.path.join(directory, package)
    os.makedirs(package_dir)
    with open(os.path.join(package_dir, "__init__.py"), "w", encoding="utf-8"):
        pass
    for filename, source in modules.items():
        with open(os.path.join(package_dir, filename), "w", encoding="utf-8") as handle:
            handle.write(source)
    sys.path.insert(0, directory)
    try:
        yield
    finally:
        sys.path.remove(directory)
        for filename in modules:
            sys.modules.pop(f"{package}.{filename[: -len('.py')]}", None)
        sys.modules.pop(package, None)


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
            "unittest.TestCase (or move a pure helper to the tests/support/ "
            "package): "
            + ", ".join(empty),
        )

    def test_every_test_case_module_matches_the_discovery_pattern(self):
        names = non_test_module_names(TESTS_DIR)
        # Without this, a broken directory listing would make the assertion
        # below pass vacuously (no modules checked, no misnamed ones found).
        self.assertIn("support.repo_root", names)
        misnamed = misnamed_test_modules(TESTS_DIR)
        self.assertEqual(
            misnamed,
            [],
            "these tests/*.py modules define test cases but do not match "
            "`make check`'s test*.py discovery pattern, so their tests "
            "silently never run; rename each to test_*.py (or move shared "
            "helpers to the tests/support/ package): "
            + ", ".join(misnamed),
        )

    def test_every_test_module_lives_in_a_directory_discovery_recurses_into(self):
        # A test*.py file under a subdirectory without __init__.py is never
        # imported by `unittest discover`, so its tests silently never run.
        # The other two checks walk the modules discovery does import; this
        # one walks the files it walks past.
        names = test_module_names(TESTS_DIR)
        # Without this, a broken directory listing would make the assertion
        # below pass vacuously (no modules checked, no skipped files found).
        self.assertIn("test_suite_discovery", names)
        skipped = skipped_test_modules(TESTS_DIR)
        self.assertEqual(
            skipped,
            [],
            "these tests/test*.py files sit under a directory that is not a "
            "package (it has no __init__.py), so `unittest discover` never "
            "imports them and their tests silently never run; add an "
            "__init__.py to every directory between tests/ and the file (or "
            "move the file into tests/): " + ", ".join(skipped),
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
        tmp = str(make_tmp_dir(self))
        with probe_module(tmp, "checks_guard_probe.py", PROBE_TEST_MODULE_SOURCE):
            self.assertEqual(
                misnamed_test_modules(tmp), ["checks_guard_probe"]
            )

    def test_a_test_module_without_tests_is_reported(self):
        # Prove the guard bites: a matched module with no TestCase is exactly
        # what test_every_test_module_contributes_tests must catch. The probe
        # is imported by bare name, so put its directory on sys.path for the
        # call and take both it and its module back out afterwards.
        source = '"""A probe module that defines no tests."""\n'
        tmp = str(make_tmp_dir(self))
        with probe_module(tmp, "test_empty_guard_probe.py", source):
            self.assertEqual(
                modules_without_tests(tmp), ["test_empty_guard_probe"]
            )

    def test_a_test_module_without_tests_inside_a_package_is_reported(self):
        # `discover` recurses into tests/svg_assertions because it is a
        # package, so a test*.py module there that defines no tests is skipped
        # exactly as a top-level one is; the guard must walk packages too.
        source = '"""A probe module that defines no tests."""\n'
        tmp = str(make_tmp_dir(self))
        with probe_package(tmp, "guard_probe_pkg", {"test_empty_probe.py": source}):
            self.assertEqual(
                modules_without_tests(tmp), ["guard_probe_pkg.test_empty_probe"]
            )

    def test_a_test_module_under_a_non_package_directory_is_reported(self):
        # Prove the guard bites: a test*.py file under a directory without
        # __init__.py is exactly what
        # test_every_test_module_lives_in_a_directory_discovery_recurses_into
        # must catch.
        tmp = make_tmp_dir(self)
        hidden = tmp / "hidden"
        hidden.mkdir()
        (hidden / "test_probe.py").write_text("", encoding="utf-8")
        self.assertEqual(
            skipped_test_modules(str(tmp)),
            [os.path.join("hidden", "test_probe.py")],
        )

    def test_a_test_module_inside_a_package_is_not_reported(self):
        # The negative control: discovery does recurse into a package, so a
        # test*.py file there must not be reported.
        tmp = make_tmp_dir(self)
        package = tmp / "guard_probe_pkg"
        package.mkdir()
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "test_probe.py").write_text("", encoding="utf-8")
        self.assertEqual(skipped_test_modules(str(tmp)), [])

    def test_a_test_module_in_a_package_under_a_non_package_is_reported(self):
        # A package nested under a non-package directory is unreachable too:
        # discovery stops at the non-package directory, so the test file in
        # the package must be reported even though its own directory has an
        # __init__.py.
        tmp = make_tmp_dir(self)
        package = tmp / "hidden" / "guard_probe_pkg"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "test_probe.py").write_text("", encoding="utf-8")
        self.assertEqual(
            skipped_test_modules(str(tmp)),
            [os.path.join("hidden", "guard_probe_pkg", "test_probe.py")],
        )

    def test_a_misnamed_test_module_inside_a_package_is_reported(self):
        # The reverse mistake inside a package: a module that defines tests but
        # does not match test*.py is never imported by discovery, so its tests
        # silently never run.
        tmp = str(make_tmp_dir(self))
        with probe_package(
            tmp, "guard_probe_pkg", {"checks_probe.py": PROBE_TEST_MODULE_SOURCE}
        ):
            self.assertEqual(
                misnamed_test_modules(tmp), ["guard_probe_pkg.checks_probe"]
            )


if __name__ == "__main__":
    unittest.main()
