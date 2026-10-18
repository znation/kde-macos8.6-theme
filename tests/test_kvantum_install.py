"""Validate the org.macos8.desktop Kvantum package and its install lifecycle.

The package ships exactly the `.kvconfig` and `.svg`, and `make install` copies
both byte for byte into `themes/org.macos8.desktop/Kvantum/`, where Kvantum
looks for them. The artwork and settings those files hold are covered by the
other `test_kvantum_*` modules.
"""

from __future__ import annotations

import os
import unittest

from support.kvantum_fixtures import KVANTUM_ID, PACKAGE, SHIPPED_FILES
from support.process_assertions import assert_succeeded
from support.shipped_files import shipped_files
from support.theme_install import (
    XDG_DATA_HOME,
    assert_files_identical,
    install,
    installed_destdir,
    uninstall,
)


def _installed_dir(destdir):
    """Directory `make install` writes the Kvantum theme into."""
    return os.path.join(
        destdir, XDG_DATA_HOME.lstrip("/"), "themes", KVANTUM_ID, "Kvantum"
    )


class TestPackage(unittest.TestCase):
    def test_package_ships_exactly_the_theme_files(self):
        shipped = shipped_files(PACKAGE)
        self.assertEqual(shipped, set(SHIPPED_FILES))


class TestInstall(unittest.TestCase):
    def test_make_install_copies_both_files_byte_for_byte(self):
        with installed_destdir(self) as tmp:
            installed = _installed_dir(tmp)
            for name in SHIPPED_FILES:
                assert_files_identical(
                    self,
                    os.path.join(PACKAGE, name),
                    os.path.join(installed, name),
                    name,
                )

    def test_make_install_is_repeatable(self):
        with installed_destdir(self) as tmp:
            assert_succeeded(self, install(tmp))

    def test_make_uninstall_removes_the_installed_files(self):
        with installed_destdir(self) as tmp:
            installed = _installed_dir(tmp)
            self.assertTrue(os.path.isdir(installed), installed)
            assert_succeeded(self, uninstall(tmp))
            for name in SHIPPED_FILES:
                path = os.path.join(installed, name)
                self.assertFalse(os.path.exists(path), path)
            again = uninstall(tmp)
            assert_succeeded(self, again)

    def test_make_uninstall_removes_staging_leftovers(self):
        with installed_destdir(self) as tmp:
            installed = _installed_dir(tmp)
            staging = [
                os.path.join(installed, f".{name}.staging")
                for name in SHIPPED_FILES
            ]
            for path in staging:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write("partial")
            assert_succeeded(self, uninstall(tmp))
            for path in staging:
                self.assertFalse(os.path.exists(path), path)


if __name__ == "__main__":
    unittest.main()
