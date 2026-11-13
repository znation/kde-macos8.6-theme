"""Tests for tools/check_parallel_discovery.py's module discovery.

The coordinator and the serial fallback replace `unittest discover`'s glob
walk with this module's discovery, whose module set both paths must import
the same way; these cases pin that discovery mirrors unittest's package
recursion, keeps symlinked directories and module files outside the
selected tree, and hands back collision-safe worker-log names.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (sys.path bootstrap)
from support.check_parallel_fixtures import OK_MODULE, OTHER_MODULE, _write_module
from support.tmp_dir import make_tmp_dir
from tools import check_parallel_discovery




class TestDiscovery(unittest.TestCase):
    """The module discovery mirrors `unittest discover`'s semantics."""

    def test_an_unlistable_subdirectory_is_reported_not_skipped(self):
        # A package directory whose listing fails must stop discovery:
        # skipping it would silently drop its modules from the run and let
        # a module count that never matches the tree pass, so the walk
        # raises DiscoveryError naming the directory and the underlying
        # error instead of the bare OSError one would get unwound through
        # visit.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        gone = os.path.join(tests_dir, "gone")
        os.mkdir(gone)
        _write_module(gone, "__init__.py", "")
        _write_module(gone, "test_hidden.py", OK_MODULE)
        real_listdir = os.listdir

        def guarded_listdir(directory):
            if os.path.samefile(directory, gone):
                raise PermissionError(13, "Permission denied")
            return real_listdir(directory)

        with mock.patch(
            "tools.check_parallel_discovery.os.listdir",
            side_effect=guarded_listdir,
        ):
            with self.assertRaises(check_parallel_discovery.DiscoveryError) as raised:
                check_parallel_discovery.discover_modules(tests_dir, "test*.py")
        self.assertIn("cannot list ", str(raised.exception))
        self.assertIn("Permission denied", str(raised.exception))

    def test_a_top_level_list_failure_names_the_selected_directory(self):
        # The same guard covers the directory the --tests-dir check already
        # saw pass: a directory swapped out or locked after that check
        # raises DiscoveryError naming it, not an OSError traceback from
        # the sorted() walk.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        with mock.patch(
            "tools.check_parallel_discovery.os.listdir",
            side_effect=PermissionError(13, "Permission denied"),
        ):
            with self.assertRaises(check_parallel_discovery.DiscoveryError) as raised:
                check_parallel_discovery.discover_modules(tests_dir, "test*.py")
        self.assertIn("cannot list ", str(raised.exception))

    def test_names_top_level_modules_in_sorted_order(self):
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        for name in ("test_b.py", "test_a.py", "helper.py"):
            _write_module(tests_dir, name, OK_MODULE)
        self.assertEqual(
            ["test_a", "test_b"],
            check_parallel_discovery.discover_modules(tests_dir, "test*.py"),
        )

    def test_non_package_directories_are_not_recursed(self):
        # discover recurses into a subdirectory only when it is a package;
        # a test*.py file under a plain directory stays invisible, as
        # test_suite_discovery's guard documents for the real suite.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        plain = os.path.join(tests_dir, "plain")
        os.mkdir(plain)
        _write_module(plain, "test_hidden.py", OK_MODULE)
        package = os.path.join(tests_dir, "shown_pkg")
        os.mkdir(package)
        _write_module(package, "__init__.py", "")
        _write_module(package, "test_shown.py", OK_MODULE)
        self.assertEqual(
            ["shown_pkg.test_shown"],
            check_parallel_discovery.discover_modules(tests_dir, "test*.py"),
        )

    def test_symlinked_package_directories_are_not_recursed(self):
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        outside = os.path.join(os.path.dirname(tests_dir), "outside_pkg")
        os.mkdir(outside)
        _write_module(outside, "__init__.py", "")
        _write_module(outside, "test_outside.py", OK_MODULE)
        os.symlink(outside, os.path.join(tests_dir, "linked_pkg"))
        self.assertEqual(
            [], check_parallel_discovery.discover_modules(tests_dir, "test*.py")
        )

    def test_a_symlinked_test_module_file_is_not_imported(self):
        # The islink guard applies to module files as well as package
        # directories: unittest discover follows a symlinked top-level test
        # module and would import it where the serial run does, so a link
        # under the tests directory pointing outside the selected tree must
        # stay invisible here too.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        outside = os.path.join(os.path.dirname(tests_dir), "outside_pkg")
        os.mkdir(outside)
        _write_module(outside, "test_outside.py", OK_MODULE)
        os.symlink(
            os.path.join(outside, "test_outside.py"),
            os.path.join(tests_dir, "test_linked.py"),
        )
        _write_module(tests_dir, "test_ok.py", OK_MODULE)
        self.assertEqual(
            ["test_ok"],
            check_parallel_discovery.discover_modules(tests_dir, "test*.py"),
        )

    def test_files_unittest_cannot_load_are_skipped(self):
        # unittest discovery gates every file on VALID_MODULE_NAME (a valid
        # Python identifier ending in .py) before the pattern match, so a
        # stray testaux.pyz under a broad pattern is not the module
        # "testaux.", and a hyphenated test-x.py under the default pattern is
        # not the module "test-x": discovery skips both, and a worker fed
        # either name would import nothing or fail the run.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        _write_module(tests_dir, "test_ok.py", OK_MODULE)
        _write_module(tests_dir, "testaux.pyz", "not python\n")
        _write_module(tests_dir, "test-x.py", OK_MODULE)
        self.assertEqual(
            ["test_ok"], check_parallel_discovery.discover_modules(tests_dir, "test*")
        )
        self.assertEqual(
            ["test_ok"],
            check_parallel_discovery.discover_modules(tests_dir, "test*.py"),
        )

    def test_modules_sharing_one_log_stem_get_unique_paths(self):
        # The dotted module name becomes one _-joined log stem, and two
        # distinct modules can share it: the package module `test_a.test_b`
        # and the top-level `test_a_test_b.py` both give `test_a_test_b`,
        # so the coordinator must not derive the log path from the stem
        # alone.
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        package = os.path.join(tests_dir, "test_a")
        os.mkdir(package)
        _write_module(package, "__init__.py", "")
        _write_module(package, "test_b.py", OK_MODULE)
        _write_module(tests_dir, "test_a_test_b.py", OTHER_MODULE)
        modules = check_parallel_discovery.discover_modules(tests_dir, "test*.py")
        self.assertEqual(["test_a.test_b", "test_a_test_b"], modules)
        paths = check_parallel_discovery.assign_log_paths(modules, "/scratch")
        self.assertEqual(2, len(set(paths.values())))

    def test_a_disambiguated_log_never_claims_another_modules_name(self):
        # The `_2` suffix must not collide with a third module's own natural
        # stem: `test_a_test_b_2` keeps its natural log, and the later
        # colliding module takes the next free suffix.
        paths = check_parallel_discovery.assign_log_paths(
            ["test_a.test_b", "test_a_test_b_2", "test_a_test_b"],
            "/scratch",
        )
        self.assertEqual(3, len(set(paths.values())))
        self.assertTrue(
            paths["test_a_test_b_2"].endswith("test_a_test_b_2.log")
        )

if __name__ == "__main__":
    unittest.main()
