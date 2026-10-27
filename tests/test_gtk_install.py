"""Validate the org.macos8.desktop GTK theme and its install lifecycle."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from support import containment, repo_root
from support.gtk_fixtures import PACKAGE, SHIPPED_FILES
from support.process_assertions import assert_failed, assert_succeeded
from support.shipped_files import shipped_files
from support.symlink_fixtures import symlinked_repo
from support.installed_paths import installed_gtk_theme
from support.tmp_dir import make_tmp_dir
from support.theme_install import (
    assert_files_identical,
    install,
    installed_destdir,
    shadow_command_env,
    uninstall,
    uninstall_recipe,
)
from tools.gtk_user_files import GTK4_CSS_MARKER  # noqa: E402


def _installed_dir(destdir):
    return installed_gtk_theme(destdir)


def _package_bytes(name):
    """Return a shipped GTK package file's bytes through the containment guard.

    The package is contributor-supplied, so a checked-in symlink at *name*
    can resolve outside the repository; a plain ``open().read()`` would
    follow it into a private file or stream a device such as ``/dev/zero``
    without bound. The shared reader refuses that escape before opening and
    bounds the read to a regular file.
    """
    return containment.read_bytes(
        os.path.join(PACKAGE, name), repo_root.ROOT
    )


def _sentinel(name):
    return ("sentinel:" + name).encode()


# Every staging path the opt-in install writes, by shipped name.
STAGING_PATHS = {
    "index.theme": ".index.theme.staging",
    "gtk-3.0/gtk.css": "gtk-3.0/.gtk.css.staging",
    "gtk-4.0/gtk.css": "gtk-4.0/.gtk.css.staging",
    "assets/checkmark.svg": "assets/.checkmark.svg.staging",
    "assets/bullet.svg": "assets/.bullet.svg.staging",
    "assets/check-mixed.svg": "assets/.check-mixed.svg.staging",
    "assets/arrow-down.svg": "assets/.arrow-down.svg.staging",
    "assets/arrow-up.svg": "assets/.arrow-up.svg.staging",
    "assets/arrow-right.svg": "assets/.arrow-right.svg.staging",
    "assets/submenu-arrow.svg": "assets/.submenu-arrow.svg.staging",
    "assets/window-close.svg": "assets/.window-close.svg.staging",
    "assets/window-maximize.svg": "assets/.window-maximize.svg.staging",
    "assets/window-minimize.svg": "assets/.window-minimize.svg.staging",
}


class TestPackage(unittest.TestCase):
    def test_package_ships_exactly_the_theme_files(self):
        shipped = shipped_files(PACKAGE)
        self.assertEqual(shipped, set(SHIPPED_FILES))


class TestPackageBytesContainment(unittest.TestCase):
    """The package-bytes read refuses a checked-in symlink escape."""

    def test_a_package_symlink_outside_the_repository_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(tmp, "index.theme", "PRIVATE-SECRET")
            with mock.patch.object(
                sys.modules[__name__], "PACKAGE", str(root)
            ), mock.patch.object(repo_root, "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    _package_bytes("index.theme")
        self.assertIn(str(link), str(caught.exception))
        self.assertNotIn("PRIVATE-SECRET", str(caught.exception))


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
                "  */assets/.window-minimize.svg.staging)\n"
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


class TestUninstallWarnsForTheDanglingGtkSelection(unittest.TestCase):
    """`make uninstall` must name a still-published GTK selection.

    The opt-in `apply-gtk` sets `gtk-theme-name=org.macos8.desktop` in the
    `[Settings]` of `<config>/gtk-3.0/settings.ini` and
    `<config>/gtk-4.0/settings.ini`, and writes `<config>/gtk-4.0/gtk.css`,
    whose first line is `GTK4_CSS_MARKER` and whose `@import` names the
    installed GTK 4 sheet. `make uninstall` removes those installed sheets,
    so a selection still naming them points at files that no longer exist
    and GTK applications silently keep their default style. The recipe warns
    and names `make remove-gtk`, reads the ini files the way
    ``tools.gtk_settings`` reads them, and must not edit the user's config.
    """

    def _uninstall(self, tmp, config=None, home=None):
        """Run the `_uninstall` recipe with a controlled config resolution.

        When *config* is given it becomes `XDG_CONFIG_HOME`; otherwise the
        variable is dropped and *home* (which must be absolute) becomes
        `HOME`, so the recipe resolves the XDG default `<home>/.config`.
        """
        env = dict(os.environ)
        env.pop("XDG_CONFIG_HOME", None)
        if config is None:
            env["HOME"] = home
        else:
            env["XDG_CONFIG_HOME"] = config
        return uninstall_recipe(tmp, env=env)

    @staticmethod
    def _config_home(tmp):
        """Return `<tmp>/config` after creating it."""
        config = os.path.join(str(tmp), "config")
        os.makedirs(config, exist_ok=True)
        return config

    @staticmethod
    def _write(path, text):
        """Create *path*'s directory and write *text* as UTF-8."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return text

    @staticmethod
    def _read(path):
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def test_warns_for_a_still_selected_gtk3_settings_ini(self):
        # The install put the theme's sheets in place; uninstall removes
        # them, and the ini line that names the removed package must then be
        # reported, together with the reset that clears it.
        with installed_destdir(self, packages="gtk") as destdir:
            config = self._config_home(destdir)
            ini = os.path.join(config, "gtk-3.0", "settings.ini")
            original = self._write(
                ini, "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
            )
            installed = _installed_dir(destdir)

            removed = self._uninstall(destdir, config=config)

            assert_succeeded(self, removed)
            self.assertFalse(
                os.path.exists(os.path.join(installed, "index.theme")),
                "the theme the ini names must have been removed",
            )
            self.assertIn("a GTK selection still names", removed.stderr)
            self.assertIn(
                os.path.join(config, "gtk-3.0", "settings.ini"), removed.stderr
            )
            self.assertIn("make remove-gtk", removed.stderr)
            self.assertEqual(
                original, self._read(ini), "uninstall must not edit the ini"
            )

    def test_warns_for_a_still_selected_gtk4_settings_ini(self):
        tmp = make_tmp_dir(self)
        config = self._config_home(tmp)
        ini = os.path.join(config, "gtk-4.0", "settings.ini")
        original = self._write(
            ini, "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        )

        removed = self._uninstall(tmp, config=config)

        assert_succeeded(self, removed)
        self.assertIn("a GTK selection still names", removed.stderr)
        self.assertIn(
            os.path.join(config, "gtk-4.0", "settings.ini"), removed.stderr
        )
        self.assertIn("make remove-gtk", removed.stderr)
        self.assertEqual(
            original, self._read(ini), "uninstall must not edit the ini"
        )

    def test_warns_for_the_marked_gtk4_user_css(self):
        tmp = make_tmp_dir(self)
        config = self._config_home(tmp)
        css = os.path.join(config, "gtk-4.0", "gtk.css")
        original = self._write(
            css, f'{GTK4_CSS_MARKER}\n@import url("file:///gone/gtk.css");\n'
        )

        removed = self._uninstall(tmp, config=config)

        assert_succeeded(self, removed)
        self.assertIn("a GTK selection still names", removed.stderr)
        self.assertIn(os.path.join(config, "gtk-4.0", "gtk.css"), removed.stderr)
        self.assertIn("make remove-gtk", removed.stderr)
        self.assertEqual(
            original, self._read(css), "uninstall must not edit the user CSS"
        )

    def test_warns_for_a_bom_prefixed_indented_selection(self):
        # tools.gtk_settings strips the first line's BOM and trims each line,
        # and apply-gtk preserves both; the recipe's awk must read the file
        # the same way or it silently misses the dangling selection.
        tmp = make_tmp_dir(self)
        config = self._config_home(tmp)
        ini = os.path.join(config, "gtk-3.0", "settings.ini")
        original = self._write(
            ini, "\ufeff[Settings]\n  gtk-theme-name = org.macos8.desktop  \n"
        )

        removed = self._uninstall(tmp, config=config)

        assert_succeeded(self, removed)
        self.assertIn("a GTK selection still names", removed.stderr)
        self.assertEqual(original, self._read(ini))

    def test_does_not_warn_for_a_foreign_theme_name(self):
        tmp = make_tmp_dir(self)
        config = self._config_home(tmp)
        ini = os.path.join(config, "gtk-3.0", "settings.ini")
        original = self._write(ini, "[Settings]\ngtk-theme-name=Adwaita\n")
        css = os.path.join(config, "gtk-4.0", "gtk.css")
        foreign_css = self._write(css, "/* the user's own CSS */\nbody {}\n")

        removed = self._uninstall(tmp, config=config)

        assert_succeeded(self, removed)
        self.assertNotIn("still names", removed.stderr)
        self.assertEqual(original, self._read(ini))
        self.assertEqual(foreign_css, self._read(css))

    def test_the_ini_peek_agrees_with_the_settings_scanner(self):
        # tools.gtk_settings selects keys only under `[Settings]`: a key in
        # another section, before any section, or a comment line names no
        # live selection, and a section switch stops a later key from
        # counting. A later duplicate inside the same section still names
        # our theme because remove_theme_name would delete it too.
        tmp = make_tmp_dir(self)
        config = self._config_home(tmp)
        ini = os.path.join(config, "gtk-3.0", "settings.ini")
        cases = (
            ("[Other]\ngtk-theme-name=org.macos8.desktop\n", False),
            ("gtk-theme-name=org.macos8.desktop\n[Settings]\n", False),
            ("[Settings]\n# gtk-theme-name=org.macos8.desktop\n", False),
            ("[Settings]\n;gtk-theme-name=org.macos8.desktop\n", False),
            ("[Settings]\n[Other]\ngtk-theme-name=org.macos8.desktop\n", False),
            ("[Settings]\ngtk-theme-name=org.macos8.desktop\n", True),
            (
                "[Settings]\ngtk-theme-name=Adwaita\n"
                "gtk-theme-name=org.macos8.desktop\n",
                True,
            ),
        )
        for text, warns in cases:
            with self.subTest(text=text):
                self._write(ini, text)
                removed = self._uninstall(tmp, config=config)
                assert_succeeded(self, removed)
                self.assertNotIn("is still selected", removed.stderr)
                self.assertEqual(
                    warns,
                    "a GTK selection still names" in removed.stderr,
                    f"the uninstall recipe disagreed with the ini: {text!r}",
                )

    def test_warns_at_the_xdg_default_when_config_home_is_unset(self):
        # The apply path resolves `$XDG_CONFIG_HOME` the XDG way: an empty or
        # relative value falls back to `<HOME>/.config`. The recipe must warn
        # about the selection published at that same default, not only when
        # the variable names the directory.
        tmp = make_tmp_dir(self)
        home = os.path.join(str(tmp), "home")
        ini = os.path.join(home, ".config", "gtk-4.0", "settings.ini")
        original = self._write(
            ini, "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        )

        removed = self._uninstall(tmp, config=None, home=home)

        assert_succeeded(self, removed)
        self.assertIn("a GTK selection still names", removed.stderr)
        self.assertIn(ini, removed.stderr)
        self.assertEqual(original, self._read(ini))


if __name__ == "__main__":
    unittest.main()
