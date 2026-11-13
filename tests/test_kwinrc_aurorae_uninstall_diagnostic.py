"""Makefile tests for the `_uninstall` kwinrc window-decoration diagnostic.

`make apply` applies the shipped look-and-feel, whose defaults publish
`[kwinrc][org.kde.kdecoration2] library=org.kde.kwin.aurorae` and
`theme=org.macos8.desktop` -- the Aurorae plugin library and the
`KWin/Decoration` package id KWin resolves the window decoration through.
`make uninstall`
removes the aurorae package and the installed kwin/decorations package but
leaves those keys, and KWin keeps drawing
its built-in default window decoration; `_uninstall` prints a diagnostic
naming the `kwriteconfig6 --delete` reset for the two keys when the last
values of both still trim to exactly that pair, without editing the file.
The scanner it runs on mirrors the shared `_uninstall` reads the existing
kwinrc button-layout diagnostic sits beside, so that suite keeps its own
exact wordings and this module must not touch them or their files (the
both-diagnostics staged case only asserts the existing wording and its
position before this one on stderr).
The window-decoration theme key also carries its own later diagnostic,
whose line fires even when this pair stays silent; the silent shapes below
pin *this pair's* line rather than the whole `window-decoration` family,
so the floor it tested still holds unchanged.
"""

import os
import unittest

from support import theme_install
from support.config_home_cases import (
    assert_home_fallback,
    assert_no_config_home,
)
from support.theme_install import (
    assert_diagnostics_in_order,
    assert_make_n_uninstall_parses,
    assert_uninstall_diagnostics,
    write_config_file,
)
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_config_home
from support.kwinrc_uninstall_wording import (
    AURORAE_LIBRARY,
    AURORAE_THEME,
    LIBRARY_KEY,
    REMOVAL_GROUP,
    THEME_KEY,
    aurorae_pair_body,
    aurorae_pair_lines,
    aurorae_pair_rule as rule_for,
    button_body,
    button_rule as BUTTON_RULE,
)

def write_kwinrc(config, body):
    """Write *body* as `<config>/kwinrc`; return its path."""
    return write_config_file(config, "kwinrc", body)


class TestKwinrcAuroraeUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the two-key reset when both keys are ours."""

    def test_warns_and_names_the_reset_for_kept_keys(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            aurorae_pair_body(),
        )
        # A diagnostic must not edit the user's kwinrc.
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_when_values_only_trim_to_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "  [" + REMOVAL_GROUP + "]  \n "
            + LIBRARY_KEY
            + " = "
            + AURORAE_LIBRARY
            + "  \n "
            + THEME_KEY
            + " =  "
            + AURORAE_THEME
            + "\t\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_for_a_bom_prefixed_file_with_comments_and_crlf(self):
        # Editors add BOMs and CRLF endings; the scanner strips the first
        # line's BOM and trims every line, so the selection stays visible.
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "\ufeff[" + REMOVAL_GROUP + "]\r\n; a comment\r\n# another\r\n"
            + aurorae_pair_lines(eol="\r\n"),
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warned_when_an_earlier_foreign_pair_precedes_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            + LIBRARY_KEY
            + "=foo\n"
            + THEME_KEY
            + "=KvArc\n"
            + aurorae_pair_lines(),
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warned_when_a_later_duplicate_pair_names_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            + aurorae_pair_lines()
            + aurorae_pair_lines(library="foo", theme="KvArc")
            + aurorae_pair_lines(),
        )

        assert_uninstall_diagnostics(self, tmp, config, rule_for(path))

    def test_silent_when_there_is_no_kwinrc(self):
        tmp, config = make_config_home(self)
        os.makedirs(config, exist_ok=True)

        assert_uninstall_diagnostics(self, tmp, config, absent="window-decoration")

    def test_silent_when_the_path_is_a_directory(self):
        tmp, config = make_config_home(self)
        os.makedirs(os.path.join(config, "kwinrc"))

        assert_uninstall_diagnostics(self, tmp, config, absent="window-decoration")

    def test_silent_without_a_decoration_group(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[Other]\n" + aurorae_pair_lines(),
        )
        assert_uninstall_diagnostics(self, tmp, config, absent="window-decoration", unchanged=path)

    def test_silent_with_only_one_of_the_two_keys(self):
        for body in (
            "[" + REMOVAL_GROUP + "]\n" + LIBRARY_KEY + "=" + AURORAE_LIBRARY + "\n",
            "[" + REMOVAL_GROUP + "]\n" + THEME_KEY + "=" + AURORAE_THEME + "\n",
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                path = write_kwinrc(config, body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                # The theme key alone warns from the later theme-key
                # diagnostic's own line; this suite pins its pair's silence.
                self.assertNotIn(rule_for(path), result.stderr)

    def test_silent_when_one_key_holds_a_foreign_value(self):
        for body in (
            aurorae_pair_body(theme="__aurorae__svg__KvArc"),
            aurorae_pair_body(library="org.kde.kwin.oxygen"),
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                path = write_kwinrc(config, body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                # A foreign library leaves the pair silent but lets the
                # theme-key diagnostic warn on its own line (the pair rule).
                self.assertNotIn(rule_for(path), result.stderr)

    def test_silent_when_either_value_is_empty(self):
        for body in (
            aurorae_pair_body(library=""),
            aurorae_pair_body(theme=""),
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                path = write_kwinrc(config, body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                # An empty value leaves the pair silent; with the empty
                # library under a named theme, the theme-key diagnostic
                # warns on its own line (the pair rule).
                self.assertNotIn(rule_for(path), result.stderr)

    def test_silent_when_a_later_foreign_duplicate_overrides_ours(self):
        # The scanner takes the last duplicate's value, as the other
        # diagnostics already do.
        tmp, config = make_config_home(self)
        write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            + aurorae_pair_lines()
            + LIBRARY_KEY
            + "=foo\n"
            + THEME_KEY
            + "=KvArc\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent="window-decoration")

    def test_silent_when_the_keys_are_split_across_groups(self):
        tmp, config = make_config_home(self)
        write_kwinrc(
            config,
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LIBRARY_KEY
            + "="
            + AURORAE_LIBRARY
            + "\n[Other]\n"
            + THEME_KEY
            + "="
            + AURORAE_THEME
            + "\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent="window-decoration")

    def test_silent_for_a_group_holding_only_the_existing_button_pair(self):
        # The existing button-layout diagnostic covers the ButtonsOn pair; a
        # group with only that pair holds no decoration selection of ours.
        tmp, config = make_config_home(self)
        write_kwinrc(config, button_body())

        assert_uninstall_diagnostics(self, tmp, config, absent="window-decoration")

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the other diagnostics, the guard ignores an unset or
        # relative XDG_CONFIG_HOME and reads `$HOME/.config`.
        assert_home_fallback(
            self,
            lambda config: write_kwinrc(config, aurorae_pair_body()),
            rule_for,
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_kwinrc(config, aurorae_pair_body()),
            rule_for,
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        assert_no_config_home(self, "window-decoration")

    def test_both_kwinrc_diagnostics_share_one_run_in_recipe_order(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            "library=org.kde.kwin.aurorae\n"
            "theme=org.macos8.desktop\n"
            "ButtonsOnLeft=X\n"
            "ButtonsOnRight=AL\n",
        )
        result = assert_uninstall_diagnostics(self, tmp, config, unchanged=path)
        assert_diagnostics_in_order(
            self, result, [BUTTON_RULE(path), rule_for(path)]
        )

    def test_make_n_uninstall_still_parses(self):
        # The scanner's recipe is pinned by drying the internal recipe
        # directly; the added block must leave the recipe parseable with
        # both wordings present in the dried output.
        assert_make_n_uninstall_parses(self, '--aurorae-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
