"""Makefile tests for the `_uninstall` kwinrc window-decoration theme key.

`make apply` applies the shipped look-and-feel, whose defaults publish
`[kwinrc][org.kde.kdecoration2]` with `theme=org.macos8.desktop`
beside `library=org.kde.kwin.aurorae` -- along with the button pair the existing
kwinrc suites cover. After `make uninstall` removes the installed packages
(the aurorae theme and the kwin/decorations/org.macos8.desktop decoration
package), that
theme id names a decoration package that no longer exists, and KWin silently
falls back on the next start; `_uninstall` prints a diagnostic naming the
`kwriteconfig6 --delete` reset for the two keys when the last value of `theme`
trims to exactly that id, without editing the file. The existing pair diagnostic
stays silent when `library` is missing or foreign, and it remains owned by its
own module, whose wordings and files this one must not touch (the staged
case below asserts only the existing wordings, their relative order on stderr
and the byte identity of the file).
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
    read_bytes,
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
    aurorae_pair_rule as AURORAE_PAIR_RULE,
    button_body,
    button_lines,
    aurorae_theme_body,
    aurorae_theme_lines,
    button_rule as BUTTON_RULE,
    write_kwinrc,
)


def rule_for(path):
    """The expected diagnostic line naming *path* (the wording is the contract)."""
    return (
        "uninstall: the window-decoration selection still names "
        f"{AURORAE_THEME} after removal in {path}; KWin cannot load the "
        "removed kwin/decorations/org.macos8.desktop decoration package "
        "and keeps the default style. Reset it "
        "with: kwriteconfig6 --file kwinrc --group "
        f"{REMOVAL_GROUP} --key {THEME_KEY} --delete && kwriteconfig6 "
        f"--file kwinrc --group {REMOVAL_GROUP} --key {LIBRARY_KEY} --delete"
    )


class TestKwinrcDecorationUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the two-key reset while the theme id is ours."""

    def test_warns_and_names_the_reset_for_the_theme_key(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config, aurorae_theme_body()
        )
        # A diagnostic must not edit the user's kwinrc.
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            rule_for(path),
            absent=(BUTTON_RULE(path), AURORAE_PAIR_RULE(path)),
            unchanged=path,
        )

    def test_warns_with_the_existing_keys_staged_beside(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            aurorae_pair_body() + button_lines(),
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_when_the_value_only_trims_to_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "  [" + REMOVAL_GROUP + "]  \n "
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
            + "  "
            + THEME_KEY
            + " = "
            + AURORAE_THEME
            + "  \r\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_when_an_earlier_foreign_theme_precedes_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            + THEME_KEY
            + "=KvArc\n"
            + LIBRARY_KEY
            + "="
            + AURORAE_LIBRARY
            + "\n"
            + aurorae_theme_lines(),
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warned_when_a_later_duplicate_theme_renames_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            + aurorae_theme_lines()
            + aurorae_theme_lines(theme="KvArc")
            + aurorae_theme_lines(),
        )

        assert_uninstall_diagnostics(self, tmp, config, rule_for(path))

    def test_warns_when_the_library_key_is_missing_or_foreign(self):
        # The existing pair diagnostic names both keys, so these shapes belong
        # to this read: the decoration id survives through `theme` alone.
        for body in (
            aurorae_theme_body(),
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LIBRARY_KEY
            + "=org.kde.kwin.oxygen\n"
            + aurorae_theme_lines(),
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LIBRARY_KEY
            + "=foo\n"
            + aurorae_theme_lines(),
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                path = write_kwinrc(config, body)
                original = read_bytes(path)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertIn(rule_for(path), result.stderr)
                self.assertEqual(original, read_bytes(path))

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
        path = write_kwinrc(config, "[Other]\n" + aurorae_theme_lines())
        assert_uninstall_diagnostics(self, tmp, config, absent="window-decoration", unchanged=path)

    def test_silent_when_the_group_holds_no_theme_key(self):
        for body in (
            "[" + REMOVAL_GROUP + "]\n",
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LIBRARY_KEY
            + "="
            + AURORAE_LIBRARY
            + "\n",
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LIBRARY_KEY
            + "="
            + AURORAE_LIBRARY
            + "\n" + button_lines(),
            button_body(),
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                path = write_kwinrc(config, body)
                original = read_bytes(path)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn("window-decoration", result.stderr)
                self.assertEqual(original, read_bytes(path))

    def test_silent_when_the_theme_value_is_foreign(self):
        for value in ("__aurorae__svg__somethingelse", "Breeze"):
            with self.subTest(value=value):
                tmp, config = make_config_home(self)
                path = write_kwinrc(
                    config,
                    "["
                    + REMOVAL_GROUP
                    + "]\n"
                    + LIBRARY_KEY
                    + "="
                    + AURORAE_LIBRARY
                    + "\n"
                    + aurorae_theme_lines(theme=value),
                )
                original = read_bytes(path)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                # The existing pair diagnostic still fires on its own pair; this
                # suite only forbids its own line.
                self.assertNotIn(rule_for(path), result.stderr)
                self.assertEqual(original, read_bytes(path))

    def test_silent_when_the_theme_value_is_empty(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LIBRARY_KEY
            + "="
            + AURORAE_LIBRARY
            + "\n"
            + aurorae_theme_lines(theme=""),
        )
        assert_uninstall_diagnostics(self, tmp, config, absent=rule_for(path), unchanged=path)

    def test_silent_when_a_later_foreign_duplicate_overrides_ours(self):
        # The scanner takes the last duplicate's value, as the other
        # diagnostics already do.
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LIBRARY_KEY
            + "="
            + AURORAE_LIBRARY
            + "\n"
            + aurorae_theme_lines()
            + THEME_KEY
            + "=KvArc\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, absent=rule_for(path), unchanged=path)

    def test_silent_when_the_key_sits_in_another_group(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LIBRARY_KEY
            + "="
            + AURORAE_LIBRARY
            + "\n[Other]\n"
            + aurorae_theme_lines(),
        )
        assert_uninstall_diagnostics(self, tmp, config, absent="window-decoration", unchanged=path)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the other diagnostics, the guard ignores an unset or
        # relative XDG_CONFIG_HOME and reads `$HOME/.config`.
        assert_home_fallback(
            self,
            lambda config: write_kwinrc(config, aurorae_theme_body()),
            rule_for,
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_kwinrc(config, aurorae_theme_body()),
            rule_for,
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        assert_no_config_home(self, "window-decoration")

    def test_all_kwinrc_diagnostics_share_one_run_in_recipe_order(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(config, aurorae_pair_body() + button_lines())
        result = assert_uninstall_diagnostics(self, tmp, config, unchanged=path)
        assert_diagnostics_in_order(
            self, result, [BUTTON_RULE(path), AURORAE_PAIR_RULE(path), rule_for(path)]
        )

    def test_make_n_uninstall_still_parses(self):
        # The scanner's recipe is pinned by drying the internal recipe
        # directly; the added block must leave the recipe parseable with
        # the two-key reset present in the dried output.
        assert_make_n_uninstall_parses(self, '--aurorae-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
