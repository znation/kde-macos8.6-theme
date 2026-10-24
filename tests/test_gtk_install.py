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


def _package_bytes(name):
    with open(os.path.join(PACKAGE, name), "rb") as handle:
        return handle.read()


def _sentinel(name):
    return ("sentinel:" + name).encode()


# Every staging path the opt-in install writes, by shipped name.
STAGING_PATHS = {
    "index.theme": ".index.theme.staging",
    "gtk-3.0/gtk.css": "gtk-3.0/.gtk.css.staging",
    "gtk-4.0/gtk.css": "gtk-4.0/.gtk.css.staging",
    "assets/checkmark.svg": "assets/.checkmark.svg.staging",
    "assets/bullet.svg": "assets/.bullet.svg.staging",
}


class TestPackage(unittest.TestCase):
    def test_package_ships_exactly_the_theme_files(self):
        shipped = shipped_files(PACKAGE)
        self.assertEqual(shipped, set(SHIPPED_FILES))


class TestInstall(unittest.TestCase):
    def test_make_install_copies_every_shipped_file_byte_for_byte(self):
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
            for name in SHIPPED_FILES:
                with open(os.path.join(installed, name), "wb") as handle:
                    handle.write(_sentinel(name))
            real_install = shutil.which("install")
            env = shadow_command_env(
                tmp,
                "install",
                "#!/bin/sh\n"
                'case "$3" in\n'
                "  */assets/.bullet.svg.staging)\n"
                '    dest="$3"\n'
                '    mkdir -p "$(dirname "$dest")"\n'
                '    printf partial > "$dest"\n'
                "    exit 1;;\n"
                "esac\n"
                'exec "%s" "$@"\n' % real_install,
            )
            result = install(tmp, env=env, packages="gtk")
            assert_failed(self, result)
            # The last staging step fails after every earlier one succeeded.
            # The trap removes every staging path, and the sentinels survive
            # only if no rename ran before that last staging step, so this
            # fails unless every staging step precedes every rename.
            for relative in STAGING_PATHS.values():
                self.assertFalse(
                    os.path.exists(os.path.join(installed, relative)), relative
                )
            for name in SHIPPED_FILES:
                with open(os.path.join(installed, name), "rb") as handle:
                    self.assertEqual(handle.read(), _sentinel(name), name)

    def test_a_failed_rename_does_not_roll_back_earlier_renames(self):
        with installed_destdir(self, packages="gtk") as tmp:
            installed = _installed_dir(tmp)
            for name in SHIPPED_FILES:
                with open(os.path.join(installed, name), "wb") as handle:
                    handle.write(_sentinel(name))
            real_mv = shutil.which("mv")
            env = shadow_command_env(
                tmp,
                "mv",
                "#!/bin/sh\n"
                'case "$2" in\n'
                "  */assets/checkmark.svg) exit 1;;\n"
                "esac\n"
                'exec "%s" "$@"\n' % real_mv,
            )
            result = install(tmp, env=env, packages="gtk")
            assert_failed(self, result)
            # The renames before the failing one stay committed, each holding
            # the new package bytes; there is no .old backup and no rollback.
            for name in ("index.theme", "gtk-3.0/gtk.css", "gtk-4.0/gtk.css"):
                with open(os.path.join(installed, name), "rb") as handle:
                    self.assertEqual(handle.read(), _package_bytes(name), name)
            for name in ("assets/checkmark.svg", "assets/bullet.svg"):
                with open(os.path.join(installed, name), "rb") as handle:
                    self.assertEqual(handle.read(), _sentinel(name), name)
            for dirpath, dirnames, filenames in os.walk(installed):
                for name in dirnames + filenames:
                    self.assertFalse(
                        name.endswith((".old", ".staging")),
                        os.path.join(dirpath, name),
                    )


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
            for relative in STAGING_PATHS.values():
                path = os.path.join(installed, relative)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as handle:
                    handle.write("partial")
            assert_succeeded(self, uninstall(tmp))
            for name in SHIPPED_FILES:
                self.assertFalse(os.path.exists(os.path.join(installed, name)))
            self.assertFalse(os.path.isdir(os.path.join(installed, "assets")))
            self.assertFalse(os.path.isdir(os.path.join(installed, "gtk-3.0")))
            self.assertFalse(os.path.isdir(os.path.join(installed, "gtk-4.0")))
            with open(planted, "rb") as handle:
                self.assertEqual(handle.read(), b"keep me")
            with open(os.path.join(sibling, "marker"), "rb") as handle:
                self.assertEqual(handle.read(), b"sibling")
            self.assertTrue(os.path.isdir(installed))
            again = uninstall(tmp)
            assert_succeeded(self, again)

    def test_make_uninstall_leaves_foreign_files_in_the_gtk_directories(self):
        with installed_destdir(self, packages="gtk") as tmp:
            installed = _installed_dir(tmp)
            foreign = b"keep me"
            for directory in ("assets", "gtk-3.0", "gtk-4.0"):
                path = os.path.join(installed, directory, "foreign.txt")
                with open(path, "wb") as handle:
                    handle.write(foreign)
            assert_succeeded(self, uninstall(tmp))
            for name in SHIPPED_FILES:
                self.assertFalse(
                    os.path.exists(os.path.join(installed, name)), name
                )
            # Each directory holds a file the theme did not install, so it is
            # not empty: uninstall removes our files but must not remove the
            # directory or its foreign content.
            for directory in ("assets", "gtk-3.0", "gtk-4.0"):
                path = os.path.join(installed, directory, "foreign.txt")
                self.assertTrue(os.path.isdir(os.path.dirname(path)), directory)
                with open(path, "rb") as handle:
                    self.assertEqual(handle.read(), foreign, directory)

    def test_make_uninstall_on_tree_with_no_gtk_install(self):
        with installed_destdir(self) as tmp:
            assert_succeeded(self, uninstall(tmp))


if __name__ == "__main__":
    unittest.main()
