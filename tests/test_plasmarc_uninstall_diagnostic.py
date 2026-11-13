"""Makefile tests for the `_uninstall` plasmarc desktop-theme diagnostic.

`make apply` selects the Plasma desktop theme with `plasma-apply-desktoptheme`,
which writes `[Theme] name=org.macos8.desktop` into the user's `plasmarc` (the
shipped look-and-feel's defaults carry the same `[plasmarc][Theme]` group, so
`lookandfeeltool -a` writes it first); `make uninstall` then removes the
installed desktoptheme package, and Plasma silently keeps the default style.
`_uninstall` prints a diagnostic naming the reset
(`plasma-apply-desktoptheme breeze`) when that selection still names our id,
without editing the file. The scanner it runs on mirrors the shared
`_uninstall` reads the color scheme, GTK, kvconfig and kcminputrc diagnostics
already pin, so those suites keep their own exact wordings and this module
must not touch them or their files.
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

DTHEME_ID = "org.macos8.desktop"
RESET = "plasma-apply-desktoptheme breeze"



def write_selection(config, body):
    """Write *body* as `<config>/plasmarc`; return its path."""
    return write_config_file(config, "plasmarc", body)


def rule_for(path, prefix="uninstall: the desktop theme selection"):
    """The expected diagnostic line naming *path* (the wording is the contract)."""
    return (
        f"{prefix} still names {DTHEME_ID} after removal in {path}; Plasma "
        "cannot load the removed desktop theme and keeps the default style. "
        f"Reset it with: {RESET}"
    )


class TestPlasmarcUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the desktop-theme reset when the selection is ours."""

    def test_warns_and_names_the_reset_for_a_kept_selection(self):
        tmp, config = make_config_home(self)
        path = write_selection(config, "[Theme]\nname=" + DTHEME_ID + "\n")
        # A diagnostic must not edit the user's plasmarc.
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_when_the_value_only_trims_to_ours(self):
        tmp, config = make_config_home(self)
        path = write_selection(config, "[Theme]\n  name = " + DTHEME_ID + "  \n")
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_for_a_bom_prefixed_file_with_comments_and_crlf(self):
        # plasma-apply-desktoptheme would never write this shape, but an
        # editor BOM-save plus CRLF endings must not hide the selection from
        # the scanner: it strips the first line's BOM and trims every line.
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "\ufeff[Theme]\r\n# a comment line\r\nname=" + DTHEME_ID + "\r\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warned_when_an_earlier_foreign_value_precedes_ours(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config, "[Theme]\nname=breeze_dark\nname=" + DTHEME_ID + "\n"
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warned_when_a_later_duplicate_names_ours(self):
        # The scanner takes the last duplicate's value, as the other four
        # uninstall diagnostics already do.
        tmp, config = make_config_home(self)
        path = write_selection(
            config, "[Theme]\nname=" + DTHEME_ID + "\ncursorTheme=ignored\nname=" + DTHEME_ID + "\n"
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_not_warned_for_a_foreign_value(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[Theme]\nname=breeze_dark\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_not_warned_for_an_empty_value(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[Theme]\nname=\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_not_warned_without_a_theme_group(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[General]\nname=" + DTHEME_ID + "\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_not_warned_when_the_key_sits_in_another_group(self):
        tmp, config = make_config_home(self)
        write_selection(
            config, "[Theme]\nextra=1\n[Other]\nname=" + DTHEME_ID + "\n"
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_not_warned_when_a_later_foreign_value_overrides_ours(self):
        tmp, config = make_config_home(self)
        write_selection(
            config, "[Theme]\nname=" + DTHEME_ID + "\nname=breeze_dark\n"
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_silent_when_there_is_no_plasmarc(self):
        tmp, config = make_config_home(self)
        os.makedirs(config, exist_ok=True)

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_silent_when_the_path_is_a_directory(self):
        tmp, config = make_config_home(self)
        os.makedirs(os.path.join(config, "plasmarc"), exist_ok=True)

        assert_uninstall_diagnostics(self, tmp, config, absent=RESET)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the four existing diagnostics, the guard ignores an unset or
        # relative XDG_CONFIG_HOME and reads `$HOME/.config`.
        assert_home_fallback(
            self,
            lambda config: write_selection(config, "[Theme]\nname=" + DTHEME_ID + "\n"),
            rule_for,
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_selection(config, "[Theme]\nname=" + DTHEME_ID + "\n"),
            rule_for,
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        # With neither an absolute XDG_CONFIG_HOME nor an absolute HOME there
        # is no config home to read, so the diagnostic must be skipped.
        assert_no_config_home(self, RESET)

    def test_both_diagnostics_share_one_run_with_their_existing_wordings(self):
        # The staged plasmarc selection and the pointer diagnostic's
        # kcminputrc selection can both warn in one run; each keeps its own
        # existing wording.
        tmp, config = make_config_home(self)
        plasmarc = write_selection(config, "[Theme]\nname=" + DTHEME_ID + "\n")
        kcminputrc = os.path.join(config, "kcminputrc")
        os.makedirs(config, exist_ok=True)
        with open(kcminputrc, "wb") as handle:
            handle.write(("[Mouse]\ncursorTheme=" + DTHEME_ID + "\n").encode("utf-8"))
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            rule_for(plasmarc),
            RESET,
            "plasma-apply-cursortheme breeze_cursors",
            "uninstall: the pointer selection still names "
            + DTHEME_ID
            + " after removal in "
            + kcminputrc,
            unchanged=plasmarc,
        )

    def test_make_n_uninstall_still_parses(self):
        assert_make_n_uninstall_parses(self, '--desktop-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
