"""Makefile tests for the `_uninstall` kdeglobals widget-style/icon-theme diagnostics.

`make apply` applies the shipped look-and-feel, whose defaults publish
`[KDE] widgetStyle=kvantum` (the Kvantum style plugin as Qt's widget style)
and `[Icons] Theme=org.macos8.desktop` (the installed icon theme) into the
user's `kdeglobals`; `make uninstall` removes the icon theme package and the
theme's Kvantum artifacts, and KDE silently keeps both selections.
`_uninstall` prints one diagnostic per key naming the matching
`kwriteconfig6 --delete` reset when that key's last value in its own section
still trims to exactly the published one, without editing the file. The two
conditions are independent: either key alone warns only its own line. The
scanner it runs on mirrors the shared `_uninstall` reads the color-scheme
diagnostic pins for kdeglobals, so that suite keeps its exact wording and
this module must not touch it or its other files.
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

ICON_THEME_ID = "org.macos8.desktop"
RESET = "kwriteconfig6 --file kdeglobals"
STYLE_RESET = RESET + " --group KDE --key widgetStyle --delete"
ICONS_RESET = RESET + " --group Icons --key Theme --delete"
COLOR_SCHEME_RESET = "plasma-apply-colorscheme BreezeLight"



def write_selection(config, body):
    """Write *body* as `<config>/kdeglobals`; return its path."""
    return write_config_file(config, "kdeglobals", body)


def style_rule_for(path):
    """The expected widget-style diagnostic line naming *path* (wording is the contract)."""
    return (
        "uninstall: the widget-style selection the look-and-feel apply wrote "
        "([KDE] widgetStyle=kvantum) is still in " + path + " after removal; "
        "every Qt start keeps selecting the style that key names whether or "
        "not it still resolves. Reset it with: " + STYLE_RESET
    )


def icons_rule_for(path):
    """The expected icon-theme diagnostic line naming *path* (wording is the contract)."""
    return (
        "uninstall: the icon-theme selection the look-and-feel apply wrote "
        "([Icons] Theme=" + ICON_THEME_ID + ") is still in " + path
        + " after removal; KDE and Qt applications cannot load the removed "
        "icon theme and keep the default icons. Reset it with: " + ICONS_RESET
    )


class TestKdeglobalsUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the two kdeglobals resets when the selections are ours."""

    def test_warns_and_names_the_reset_for_a_kept_widget_style(self):
        tmp, config = make_config_home(self)
        path = write_selection(config, "[KDE]\nwidgetStyle=kvantum\n")
        # A diagnostic must not edit the user's kdeglobals.
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            style_rule_for(path),
            absent=icons_rule_for(path),
            unchanged=path,
        )

    def test_warns_and_names_the_reset_for_a_kept_icon_theme(self):
        tmp, config = make_config_home(self)
        path = write_selection(config, "[Icons]\nTheme=" + ICON_THEME_ID + "\n")
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            icons_rule_for(path),
            absent=style_rule_for(path),
            unchanged=path,
        )

    def test_both_selections_warn_in_the_published_order(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "[KDE]\nwidgetStyle=kvantum\n[Icons]\nTheme=" + ICON_THEME_ID + "\n",
        )
        # One key's match never gates the other's line; the widget-style
        # warning precedes the icon-theme warning as printed.
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            style_rule_for(path),
            icons_rule_for(path),
            unchanged=path,
        )

    def test_warns_when_the_value_only_trims_to_ours(self):
        tmp, config = make_config_home(self)
        path = write_selection(config, "[KDE]\n  widgetStyle = kvantum  \n")

        assert_uninstall_diagnostics(self, tmp, config, style_rule_for(path))

    def test_warns_for_a_bom_prefixed_file_with_comments_and_indents(self):
        # The look-and-feel apply would never write this shape, but an editor
        # BOM-save must not hide the selections from the scanner: it strips
        # the first line's BOM and trims every line.
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "\ufeff[KDE]\n# a comment\n; another\n  widgetStyle = kvantum\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, style_rule_for(path))

    def test_warned_when_an_earlier_foreign_value_precedes_ours(self):
        tmp, config = make_config_home(self)
        path = write_selection(config, "[Icons]\nTheme=breeze_dark\nTheme=" + ICON_THEME_ID + "\n")

        assert_uninstall_diagnostics(self, tmp, config, icons_rule_for(path))

    def test_warned_when_a_later_duplicate_names_ours(self):
        # The scanner takes the last duplicate's value, as the other
        # uninstall diagnostics already do.
        tmp, config = make_config_home(self)
        path = write_selection(
            config, "[KDE]\nwidgetStyle=kvantum\nSingleClick=true\nwidgetStyle=kvantum\n"
        )

        assert_uninstall_diagnostics(self, tmp, config, style_rule_for(path))

    def test_warns_when_an_unterminated_header_precedes_the_group(self):
        # A header that never closes is skipped and cannot switch the
        # section, so the following key stays in the group it opened.
        tmp, config = make_config_home(self)
        path = write_selection(config, "[Stale\n[KDE]\nwidgetStyle=kvantum\n")

        assert_uninstall_diagnostics(self, tmp, config, style_rule_for(path))

    def test_not_warned_for_a_foreign_value(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[KDE]\nwidgetStyle=kvantum-dark\n[Icons]\nTheme=breeze_dark\n")

        result = assert_uninstall_diagnostics(self, tmp, config, absent=STYLE_RESET)
        self.assertNotIn(ICONS_RESET, result.stderr)

    def test_not_warned_for_a_case_mismatch(self):
        # Keys and values are case-sensitive in kdeglobals.
        tmp, config = make_config_home(self)
        write_selection(config, "[KDE]\nwidgetStyle=Kvantum\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=STYLE_RESET)

    def test_not_warned_for_an_empty_value(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[Icons]\nTheme=\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=ICONS_RESET)

    def test_not_warned_when_either_group_or_key_is_absent(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[General]\nColorScheme=BreezeLight\n[Icons]\nSingleClick=true\n")

        result = assert_uninstall_diagnostics(self, tmp, config, absent=STYLE_RESET)
        self.assertNotIn(ICONS_RESET, result.stderr)

    def test_independence_each_key_silent_outside_its_own_group(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "[KDE]\nTheme=" + ICON_THEME_ID + "\n[Icons]\nwidgetStyle=kvantum\n",
        )
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            absent=(STYLE_RESET, ICONS_RESET),
            unchanged=path,
        )

    def test_not_warned_when_a_later_foreign_value_overrides_ours(self):
        tmp, config = make_config_home(self)
        write_selection(config, "[KDE]\nwidgetStyle=kvantum\nwidgetStyle=kvantum-dark\n")

        assert_uninstall_diagnostics(self, tmp, config, absent=STYLE_RESET)

    def test_silent_when_there_is_no_kdeglobals(self):
        tmp, config = make_config_home(self)
        os.makedirs(config, exist_ok=True)

        result = assert_uninstall_diagnostics(self, tmp, config, absent=STYLE_RESET)
        self.assertNotIn(ICONS_RESET, result.stderr)

    def test_silent_when_the_path_is_a_directory(self):
        tmp, config = make_config_home(self)
        os.makedirs(os.path.join(config, "kdeglobals"), exist_ok=True)

        result = assert_uninstall_diagnostics(self, tmp, config, absent=STYLE_RESET)
        self.assertNotIn(ICONS_RESET, result.stderr)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the existing diagnostics, the guard ignores an unset
        # XDG_CONFIG_HOME and reads `$HOME/.config`.
        assert_home_fallback(
            self,
            lambda config: write_selection(config, "[KDE]\nwidgetStyle=kvantum\n"),
            style_rule_for,
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_selection(
                config, "[Icons]\nTheme=" + ICON_THEME_ID + "\n"
            ),
            icons_rule_for,
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        # With neither an absolute XDG_CONFIG_HOME nor an absolute HOME there
        # is no config home to read, so the diagnostics must be skipped.
        assert_no_config_home(self, STYLE_RESET, ICONS_RESET)

    def test_all_three_kdeglobals_diagnostics_share_one_run_in_recipe_order(self):
        # The staged color-scheme selection and the two look-and-feel keys
        # warn in one run; each keeps its existing wording and the lines appear
        # in recipe order (color scheme, widget style, icon theme).
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "[General]\nColorScheme=MacOS8\n"
            "[KDE]\nwidgetStyle=kvantum\n"
            "[Icons]\nTheme=" + ICON_THEME_ID + "\n",
        )
        scheme_line = (
            "uninstall: color scheme MacOS8 is still selected in "
            + path + " after removal"
        )
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            scheme_line,
            style_rule_for(path),
            icons_rule_for(path),
            unchanged=path,
        )

    def test_make_n_uninstall_still_parses(self):
        # The internal recipe is pinned by drying it directly, as the other
        # uninstall diagnostic suites do.
        assert_make_n_uninstall_parses(self, '--icon-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
