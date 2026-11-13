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
from support.config_home_cases import (
    assert_home_fallback,
    assert_no_config_home,
)
from support.theme_install import (
    assert_make_n_uninstall_parses,
    assert_uninstall_diagnostics,
    write_config_file,
)
from support.tmp_dir import make_config_home

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
        tmp, config = make_config_home(self)
        path = write_selection(config, "[Mouse]\ncursorTheme=" + CURSOR_ID + "\n")
        # A diagnostic must not edit the user's kcminputrc.
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_when_the_value_only_trims_to_ours(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config, "[Mouse]\n  cursorTheme = " + CURSOR_ID + "  \n"
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_for_a_bom_prefixed_file_with_comments_and_crlf(self):
        # plasma-apply-cursortheme would never write this shape, but an
        # editor BOM-save plus CRLF endings must not hide the selection from
        # the scanner: it strips the first line's BOM and trims every line.
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "\ufeff[Mouse]\r\n# a comment line\r\ncursorTheme=" + CURSOR_ID + "\r\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_not_warned_for_a_foreign_value(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[Mouse]\ncursorTheme=breeze_cursors\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_not_warned_for_an_empty_value(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[Mouse]\ncursorTheme=\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_not_warned_when_the_key_sits_in_another_section(self):
        tmp, config = make_config_home(self)
        write_selection(
            config, "[Mouse]\ncursorSize=1\n[Other]\ncursorTheme=" + CURSOR_ID + "\n"
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_not_warned_for_a_different_key_in_the_mouse_section(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[Mouse]\ncursorSize=" + CURSOR_ID + "\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_not_warned_when_a_later_foreign_value_overrides_ours(self):
        # The scanner takes the last duplicate's value, as the color-scheme
        # and kvconfig diagnostics already do.
        tmp, config = make_config_home(self)
        write_selection(
            config,
            "[Mouse]\ncursorTheme=" + CURSOR_ID + "\ncursorTheme=breeze_cursors\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_warned_when_a_later_duplicate_names_ours(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "[Mouse]\ncursorTheme=breeze_cursors\ncursorTheme=" + CURSOR_ID + "\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, rule_for(path))

    def test_silent_when_there_is_no_kcminputrc(self):
        tmp, config = make_config_home(self)
        os.makedirs(config, exist_ok=True)

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_silent_for_an_unreadable_kcminputrc(self):
        if os.geteuid() == 0:
            self.skipTest("root bypasses file permissions")
        tmp, config = make_config_home(self)
        path = write_selection(config, "[Mouse]\ncursorTheme=" + CURSOR_ID + "\n")
        os.chmod(path, 0o000)

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the three existing diagnostics, the guard ignores an unset or
        # relative XDG_CONFIG_HOME and reads `$HOME/.config`.
        assert_home_fallback(
            self,
            lambda config: write_selection(
                config, "[Mouse]\ncursorTheme=" + CURSOR_ID + "\n"
            ),
            rule_for,
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_selection(
                config, "[Mouse]\ncursorTheme=" + CURSOR_ID + "\n"
            ),
            rule_for,
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        # With neither an absolute XDG_CONFIG_HOME nor an absolute HOME there
        # is no config home to read, so the diagnostic must be skipped.
        assert_no_config_home(self, RESET)

    def test_make_n_uninstall_still_parses(self):
        assert_make_n_uninstall_parses(self, '--icon-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
