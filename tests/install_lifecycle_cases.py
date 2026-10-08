"""Shared install/uninstall lifecycle cases for the two theme packages.

The look-and-feel and desktop-theme suites both install their package into a
temporary data home and check the same lifecycle: the installed files match the
source byte for byte, a second install succeeds, and `make uninstall` removes
the package along with any staging/old leftovers. Each suite subclasses
`InstallLifecycleCases`, sets `KIND`, `PACKAGE_ID`, `PACKAGE_DIR` and
`INSTALLED_FILES`, and inherits the checks once.
"""

import os
import tempfile

from theme_install import (
    assert_files_identical,
    install,
    installed_package,
    installed_plasma_dir,
    old_sibling,
    staging_sibling,
    uninstall,
)


class InstallLifecycleCases:
    """Mixin: the install/uninstall lifecycle shared by both packages.

    Subclasses set `KIND` (`look-and-feel` or `desktoptheme`), `PACKAGE_ID`,
    `PACKAGE_DIR` (the source package directory) and `INSTALLED_FILES` (paths
    relative to the package root to compare byte for byte). It is a plain
    mixin, not a `TestCase`, so importing it does not collect the unconfigured
    base.
    """

    KIND = None
    PACKAGE_ID = None
    PACKAGE_DIR = None
    INSTALLED_FILES = ()

    def test_make_install_copies_package_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = installed_package(tmp, self.KIND, self.PACKAGE_ID)
            for name in self.INSTALLED_FILES:
                source = os.path.join(self.PACKAGE_DIR, name)
                target = os.path.join(installed, name)
                assert_files_identical(self, source, target, name)

    def test_make_install_is_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = install(tmp)
            self.assertEqual(second.returncode, 0, second.stderr)

    def test_make_uninstall_removes_the_installed_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            parent = installed_plasma_dir(tmp, self.KIND)
            package = os.path.join(parent, self.PACKAGE_ID)
            self.assertTrue(os.path.isdir(package), package)

            # SIGKILL cannot be trapped, so an install killed in the swap
            # window leaves a hidden staging directory and the moved-aside old
            # package behind. `uninstall` must remove those leftovers too.
            leaked = [
                staging_sibling(parent, self.PACKAGE_ID),
                old_sibling(parent, self.PACKAGE_ID),
            ]
            for path in leaked:
                os.makedirs(path)
                with open(
                    os.path.join(path, "metadata.json"), "w", encoding="utf-8"
                ) as handle:
                    handle.write("{}")

            removed = uninstall(tmp)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(os.path.exists(package), package)
            for path in leaked:
                self.assertFalse(
                    os.path.exists(path),
                    f"{path} leaked after uninstall",
                )

            again = uninstall(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)
