"""Validate the org.macos8.desktop GTK theme and its install lifecycle."""

from __future__ import annotations

import os
import shutil
import unittest

from support.gtk_fixtures import PACKAGE, SHIPPED_FILES
from support.process_assertions import assert_failed, assert_succeeded
from support.shipped_files import shipped_files
from support.installed_paths import installed_gtk_theme
from support.theme_install import (
    assert_files_identical,
    install,
    installed_destdir,
    shadow_command_env,
    uninstall,
)


def _installed_dir(destdir):
    return installed_gtk_theme(destdir)


class TestPackage(unittest.TestCase):
    def test_package_ships_exactly_the_theme_files(self):
        shipped = shipped_files(PACKAGE)
        self.assertEqual(shipped, set(SHIPPED_FILES))


class TestInstall(unittest.TestCase):
    def test_make_install_copies_all_three_byte_for_byte(self):
        with installed_destdir(self, packages="gtk") as tmp:
            installed = _installed_dir(tmp)
            for name in SHIPPED_FILES:
                assert_files_identical(
                    self,
                    os.path.join(PACKAGE, name),
                    os.path.join(installed, name),
                    name,
                )

    def test_make_install_is_repeatable(self):
        with installed_destdir(self, packages="gtk") as tmp:
            assert_succeeded(self, install(tmp, packages="gtk"))

    def test_failed_install_keeps_previous_files(self):
        with installed_destdir(self, packages="gtk") as tmp:
            installed = _installed_dir(tmp)
            good = {}
            for name in SHIPPED_FILES:
                with open(os.path.join(installed, name), "rb") as handle:
                    good[name] = handle.read()
            real_install = shutil.which("install")
            env = shadow_command_env(
                tmp,
                "install",
                "#!/bin/sh\n"
                'case "$3" in\n'
                "  */gtk-3.0/.gtk.css.staging|*/gtk-4.0/.gtk.css.staging|*/.index.theme.staging)\n"
                '    dest="$3"\n'
                '    mkdir -p "$(dirname "$dest")"\n'
                '    printf partial > "$dest"\n'
                "    exit 1;;\n"
                "esac\n"
                'exec "%s" "$@"\n' % real_install,
            )
            result = install(tmp, env=env, packages="gtk")
            assert_failed(self, result)
            # check no staging siblings
            for path in [os.path.join(installed, ".index.theme.staging"),
                         os.path.join(installed, "gtk-3.0", ".gtk.css.staging"),
                         os.path.join(installed, "gtk-4.0", ".gtk.css.staging")]:
                self.assertFalse(os.path.exists(path))
            for name in SHIPPED_FILES:
                with open(os.path.join(installed, name), "rb") as handle:
                    self.assertEqual(handle.read(), good[name])


    def test_make_install_leaves_preexisting_kvantum_file_untouched(self):
        with installed_destdir(self, packages="gtk") as tmp:
            installed = _installed_dir(tmp)
            kvantum_dir = os.path.join(installed, "Kvantum")
            os.makedirs(kvantum_dir, exist_ok=True)
            sentinel = os.path.join(kvantum_dir, "sentinel.txt")
            with open(sentinel, "wb") as handle:
                handle.write(b"keep me")
            assert_succeeded(self, install(tmp, packages="gtk"))
            with open(sentinel, "rb") as handle:
                self.assertEqual(handle.read(), b"keep me")
            for name in SHIPPED_FILES:
                self.assertTrue(os.path.exists(os.path.join(installed, name)))

    def test_default_install_writes_no_gtk_files(self):
        with installed_destdir(self) as tmp:
            installed = _installed_dir(tmp)
            for name in SHIPPED_FILES:
                self.assertFalse(os.path.exists(os.path.join(installed, name)))




class TestUninstall(unittest.TestCase):
    def test_make_uninstall_removes_the_installed_files(self):
        with installed_destdir(self, packages="gtk") as tmp:
            installed = _installed_dir(tmp)
            self.assertTrue(os.path.isdir(installed), installed)
            planted = os.path.join(installed, "Kvantum", "sentinel.txt")
            os.makedirs(os.path.dirname(planted), exist_ok=True)
            with open(planted, "wb") as handle:
                handle.write(b"keep me")
            sibling = os.path.join(os.path.dirname(installed), "second-theme")
            os.makedirs(sibling, exist_ok=True)
            with open(os.path.join(sibling, "marker"), "wb") as handle:
                handle.write(b"sibling")
            # staging leftovers
            for path in [os.path.join(installed, ".index.theme.staging"),
                         os.path.join(installed, "gtk-3.0", ".gtk.css.staging"),
                         os.path.join(installed, "gtk-4.0", ".gtk.css.staging")]:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as handle:
                    handle.write("partial")
            assert_succeeded(self, uninstall(tmp))
            for name in SHIPPED_FILES:
                self.assertFalse(os.path.exists(os.path.join(installed, name)))
            self.assertFalse(os.path.isdir(os.path.join(installed, "gtk-3.0")))
            self.assertFalse(os.path.isdir(os.path.join(installed, "gtk-4.0")))
            with open(planted, "rb") as handle:
                self.assertEqual(handle.read(), b"keep me")
            with open(os.path.join(sibling, "marker"), "rb") as handle:
                self.assertEqual(handle.read(), b"sibling")
            self.assertTrue(os.path.isdir(installed))
            again = uninstall(tmp)
            assert_succeeded(self, again)

    def test_make_uninstall_on_tree_with_no_gtk_install(self):
        with installed_destdir(self) as tmp:
            assert_succeeded(self, uninstall(tmp))


if __name__ == "__main__":
    unittest.main()
