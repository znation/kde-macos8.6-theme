"""Makefile tests for the `_uninstall` kcminputrc pointer diagnostic.

`make apply-cursor` selects the pointer with `plasma-apply-cursortheme`, which
writes `[Mouse] cursorTheme=org.macos8.desktop` into the user's
`kcminputrc`; `make uninstall` then removes the installed icon theme, and
Xcursor applications silently keep the default pointer. `_uninstall` prints a
diagnostic naming the external reset (`plasma-apply-cursortheme
breeze_cursors`) when that selection still names our id, without editing the
file. The scanner it runs on mirrors the shared `_uninstall` reads the color
scheme, GTK and kvconfig diagnostics already pin, so those suites keep their
own exact wordings and this module must not touch them or their files.
"""

import os
import unittest

from support import theme_install
from support.theme_install import (
    assert_make_n_uninstall_parses,
    read_bytes,
    write_config_file,
)
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir

CURSOR_ID = "org.macos8.desktop"
RESET = "plasma-apply-cursortheme breeze_cursors"



def write_selection(config, body):
    """Write *body* as `<config>/kcminputrc`; return its path."""
    return write_config_file(config, "kcminputrc", body)


def rule_for(path, prefix="uninstall: the pointer selection"):
    """The expected diagnostic line naming *path* (the wording is the contract)."""
    return (
        f"{prefix} still names {CURSOR_ID} after removal in {path}; Xcursor "
        "applications cannot load the removed cursor theme and keep the "
        f"default pointer. Reset it with: {RESET}"
    )


class TestCursorUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the pointer reset when the selection is ours."""

    def test_warns_and_names_the_reset_for_a_kept_selection(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(config, "[Mouse]\ncursorTheme=" + CURSOR_ID + "\n")
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        # A diagnostic must not edit the user's kcminputrc.
        self.assertEqual(original, read_bytes(path))

    def test_warns_when_the_value_only_trims_to_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config, "[Mouse]\n  cursorTheme = " + CURSOR_ID + "  \n"
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warns_for_a_bom_prefixed_file_with_comments_and_crlf(self):
        # plasma-apply-cursortheme would never write this shape, but an
        # editor BOM-save plus CRLF endings must not hide the selection from
        # the scanner: it strips the first line's BOM and trims every line.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config,
            "\ufeff[Mouse]\r\n# a comment line\r\ncursorTheme=" + CURSOR_ID + "\r\n",
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_not_warned_for_a_foreign_value(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(config, "[Mouse]\ncursorTheme=breeze_cursors\n")

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_for_an_empty_value(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(config, "[Mouse]\ncursorTheme=\n")

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_when_the_key_sits_in_another_section(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(
            config, "[Mouse]\ncursorSize=1\n[Other]\ncursorTheme=" + CURSOR_ID + "\n"
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_for_a_different_key_in_the_mouse_section(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(config, "[Mouse]\ncursorSize=" + CURSOR_ID + "\n")

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_when_a_later_foreign_value_overrides_ours(self):
        # The scanner takes the last duplicate's value, as the color-scheme
        # and kvconfig diagnostics already do.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(
            config,
            "[Mouse]\ncursorTheme=" + CURSOR_ID + "\ncursorTheme=breeze_cursors\n",
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_warned_when_a_later_duplicate_names_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config,
            "[Mouse]\ncursorTheme=breeze_cursors\ncursorTheme=" + CURSOR_ID + "\n",
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)

    def test_silent_when_there_is_no_kcminputrc(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        os.makedirs(config, exist_ok=True)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_silent_for_an_unreadable_kcminputrc(self):
        if os.geteuid() == 0:
            self.skipTest("root bypasses file permissions")
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(config, "[Mouse]\ncursorTheme=" + CURSOR_ID + "\n")
        os.chmod(path, 0o000)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the three existing diagnostics, the guard ignores an unset or
        # relative XDG_CONFIG_HOME and reads `$HOME/.config`.
        tmp = str(make_tmp_dir(self))
        home = os.path.join(tmp, "home")
        config = os.path.join(home, ".config")
        write_selection(config, "[Mouse]\ncursorTheme=" + CURSOR_ID + "\n")
        env = theme_install.make_env("XDG_CONFIG_HOME")
        env["HOME"] = home

        result = theme_install.uninstall_recipe(
            str(make_tmp_dir(self)), extra=(), env=env
        )

        assert_succeeded(self, result)
        self.assertIn(rule_for(os.path.join(config, "kcminputrc")), result.stderr)

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        tmp = str(make_tmp_dir(self))
        home = os.path.join(tmp, "home")
        config = os.path.join(home, ".config")
        write_selection(config, "[Mouse]\ncursorTheme=" + CURSOR_ID + "\n")
        env = theme_install.make_env("XDG_CONFIG_HOME")
        env["HOME"] = home
        env["XDG_CONFIG_HOME"] = "relative/config"

        result = theme_install.uninstall_recipe(
            str(make_tmp_dir(self)), extra=(), env=env
        )

        assert_succeeded(self, result)
        self.assertIn(rule_for(os.path.join(config, "kcminputrc")), result.stderr)

    def test_without_a_config_home_nothing_is_checked(self):
        # With neither an absolute XDG_CONFIG_HOME nor an absolute HOME there
        # is no config home to read, so the diagnostic must be skipped.
        tmp = str(make_tmp_dir(self))
        env = theme_install.make_env("XDG_CONFIG_HOME", "HOME")

        result = theme_install.uninstall_recipe(tmp, extra=(), env=env)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_make_n_uninstall_still_parses(self):
        assert_make_n_uninstall_parses(self, '--icon-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
