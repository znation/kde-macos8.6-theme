"""Makefile tests for the `_uninstall` kdeglobals font diagnostics.

`make apply` applies the shipped look-and-feel, whose defaults publish the
five font selections `[General] font=Lato,10`, `menuFont=ChicagoFLF,10`,
`toolBarFont=Lato,10` and `smallestReadableFont=Lato,8`, and
`[WM] activeFont=ChicagoFLF,10`, into the user's `kdeglobals`, and whose
apply run additionally writes the fixed-width selection
`[General] fixed=JetBrains Mono,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium`
(the Qt 6 serialized QFont form naming the shipped JetBrains Mono Medium;
`tools/apply_theme.py` writes it because the look-and-feel apply publishes
no defaults' font key); `make uninstall`
then deletes the installed font package (`$(FONT_INSTALL_DIR)/$(FONT_ID)`),
and KDE and Qt keep
naming the removed family. `_uninstall` prints one diagnostic per key
naming the matching `kwriteconfig6 --delete` reset when that key's last
value in its own section still trims to exactly the published one, without
editing the file. The six conditions are independent: one key's match
never gates another's line. The scanner it runs on mirrors the shared
`_uninstall` read the existing kdeglobals widget-style/icon-theme diagnostic
pins, so that suite keeps its exact wording and this module must not touch
it or its other files.
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
    read_bytes,
    write_config_file,
)
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_config_home

FONT_VALUE = "Lato,10"
CHICAGO_VALUE = "ChicagoFLF,10"
SMALL_VALUE = "Lato,8"
FIXED_VALUE = "JetBrains Mono,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium"
FONT_RESET = "kwriteconfig6 --file kdeglobals"
RESET_TAIL = (
    " after removal; KDE and Qt keep naming the selected font family the removal deleted and fall "
    "back to a default where no other copy of that family remains installed. "
    "Reset it with: " + FONT_RESET
)
# (section, key, published value) in the order the diagnostics print.
KEYS = [
    ("General", "font", FONT_VALUE),
    ("General", "fixed", FIXED_VALUE),
    ("General", "menuFont", CHICAGO_VALUE),
    ("General", "toolBarFont", FONT_VALUE),
    ("General", "smallestReadableFont", SMALL_VALUE),
    ("WM", "activeFont", CHICAGO_VALUE),
]
COLOR_SCHEME_RESET = "plasma-apply-colorscheme BreezeLight"
ICON_THEME_ID = "org.macos8.desktop"



def write_selection(config, body):
    """Write *body* as `<config>/kdeglobals`; return its path."""
    return write_config_file(config, "kdeglobals", body)


def rule_for(path, section, key, value):
    """The expected diagnostic line for one key (the wording is the contract)."""
    return (
        "uninstall: the font selection [" + section + "] " + key + "=" + value
        + " the look-and-feel apply wrote is still in " + path
        + RESET_TAIL
        + " --group " + section + " --key " + key + " --delete"
    )


def reset_for(section, key):
    """The reset tail one diagnostic names, for silence assertions."""
    return "kdeglobals --group " + section + " --key " + key + " --delete"


class TestKdeglobalsFontsUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the six font resets when the selections are ours."""

    def assert_warns(self, result, path, *indexed):
        """Every staged key warns with its own line, no other key's line."""
        rules = [rule_for(path, section, key, value) for section, key, value in KEYS]
        for sub, rule in enumerate(rules):
            if sub in indexed:
                self.assertIn(rule, result.stderr)
            else:
                self.assertNotIn(rule, result.stderr)

    def test_warns_and_names_the_reset_for_each_kept_key(self):
        for section, key, value in KEYS:
            with self.subTest(key=key):
                tmp, config = make_config_home(self)
                path = write_selection(
                    config, "[" + section + "]\n" + key + "=" + value + "\n"
                )
                original = read_bytes(path)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                # Independence: a single staged key warns only its own line.
                self.assert_warns(
                    result, path, [k for _, k, _ in KEYS].index(key)
                )
                # A diagnostic must not edit the user's kdeglobals.
                self.assertEqual(original, read_bytes(path))

    def test_all_six_keys_warn_in_the_published_order(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "[General]\nfont=Lato,10\nfixed=" + FIXED_VALUE + "\nmenuFont=ChicagoFLF,10\ntoolBarFont=Lato,10\n"
            "smallestReadableFont=Lato,8\n[WM]\nactiveFont=ChicagoFLF,10\n",
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        rules = [rule_for(path, *triple) for triple in KEYS]
        for rule in rules:
            self.assertIn(rule, result.stderr)
        for earlier, later in zip(rules, rules[1:]):
            self.assertLess(result.stderr.index(earlier), result.stderr.index(later))
        self.assertEqual(original, read_bytes(path))

    def test_warns_when_the_value_only_trims_to_ours(self):
        tmp, config = make_config_home(self)
        path = write_selection(config, "[General]\n  menuFont = ChicagoFLF,10  \n")
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path, "General", "menuFont", CHICAGO_VALUE), unchanged=path)

    def test_warns_for_a_bom_prefixed_file_with_comments_crlf_and_indents(self):
        # The apply would never write this shape, but an editor BOM-save plus
        # CRLF endings must not hide the selections from the scanner: it
        # strips the first line's BOM and trims every line.
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "\ufeff[General]\r\n# a comment\r\n; another\r\n  font = Lato,10  \r\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path, "General", "font", FONT_VALUE), unchanged=path)

    def test_warned_when_an_earlier_foreign_value_precedes_ours(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config, "[General]\ntoolBarFont=Salsa\ntoolBarFont=Lato,10\n"
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(
            rule_for(path, "General", "toolBarFont", FONT_VALUE), result.stderr
        )
        self.assertEqual(original, read_bytes(path))

    def test_warned_when_a_later_duplicate_names_ours(self):
        # The scanner takes the last duplicate's value, as the other
        # uninstall diagnostics already do.
        tmp, config = make_config_home(self)
        path = write_selection(
            config, "[WM]\nactiveFont=Salsa\nactiveFont=ChicagoFLF,10\n"
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path, "WM", "activeFont", CHICAGO_VALUE), unchanged=path)

    def test_warns_when_an_unterminated_header_leaves_the_section(self):
        # A header that never closes is skipped without changing the
        # section, so the keys stay in the group they opened.
        tmp, config = make_config_home(self)
        path = write_selection(
            config, "[General]\nfont=Lato,10\n[KDE\nmenuFont=ChicagoFLF,10\n"
        )
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            rule_for(path, "General", "font", FONT_VALUE),
            rule_for(path, "General", "menuFont", CHICAGO_VALUE),
            unchanged=path,
        )

    def test_not_warned_for_a_later_foreign_value_overriding_ours(self):
        for section, key, value in KEYS:
            with self.subTest(key=key):
                tmp, config = make_config_home(self)
                write_selection(
                    config,
                    "["
                    + section
                    + "]\n"
                    + key
                    + "="
                    + value
                    + "\n"
                    + key
                    + "=Salsa\n",
                )

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(reset_for(section, key), result.stderr)

    def test_not_warned_for_a_foreign_or_empty_last_value(self):
        for section, key, value, last in [
            ("General", "font", FONT_VALUE, "Salsa"),
            ("General", "menuFont", CHICAGO_VALUE, ""),
            ("WM", "activeFont", CHICAGO_VALUE, "Salsa"),
        ]:
            with self.subTest(key=key, last=last):
                tmp, config = make_config_home(self)
                write_selection(
                    config,
                    "[" + section + "]\n" + key + "=" + value + "\n" + key + "=" + last + "\n",
                )

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(reset_for(section, key), result.stderr)

    def test_not_warned_for_a_case_mismatch(self):
        # Keys are case-sensitive, as the existing kdeglobals diagnostics are.
        tmp, config = make_config_home(self)
        write_selection(config, "[General]\nFont=Lato,10\n[WM]\nActiveFont=Lato,10\n")

        result = assert_uninstall_diagnostics(self, tmp, config, absent=reset_for("General", "font"))
        self.assertNotIn(reset_for("WM", "activeFont"), result.stderr)

    def test_independence_each_key_silent_outside_its_own_group(self):
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "[WM]\nfont=Lato,10\nmenuFont=ChicagoFLF,10\ntoolBarFont=Lato,10\n"
            "smallestReadableFont=Lato,8\n[General]\nactiveFont=ChicagoFLF,10\n",
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assert_warns(result, path)
        self.assertEqual(original, read_bytes(path))

    def test_silent_when_there_is_no_kdeglobals(self):
        tmp, config = make_config_home(self)
        os.makedirs(config, exist_ok=True)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assert_warns(result, os.path.join(config, "kdeglobals"))

    def test_silent_when_the_path_is_a_directory(self):
        tmp, config = make_config_home(self)
        os.makedirs(os.path.join(config, "kdeglobals"), exist_ok=True)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assert_warns(result, os.path.join(config, "kdeglobals"))

    def test_silent_for_a_file_without_the_two_groups_or_without_the_key(self):
        for body in (
            "[Other]\nname=whatever\n",
            "[General]\nSingleClick=true\n",
            "[WM]\nfoo=bar\n",
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                write_selection(config, body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                for section, key, _ in KEYS:
                    self.assertNotIn(reset_for(section, key), result.stderr)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the existing diagnostics, the guard ignores an unset
        # XDG_CONFIG_HOME and reads `$HOME/.config`.
        assert_home_fallback(
            self,
            lambda config: write_selection(config, "[WM]\nactiveFont=ChicagoFLF,10\n"),
            lambda path: rule_for(path, "WM", "activeFont", CHICAGO_VALUE),
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_selection(
                config, "[General]\nsmallestReadableFont=Lato,8\n"
            ),
            lambda path: rule_for(path, "General", "smallestReadableFont", SMALL_VALUE),
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        # With neither an absolute XDG_CONFIG_HOME nor an absolute HOME there
        # is no config home to read, so the diagnostics must be skipped.
        result = assert_no_config_home(self)
        for section, key, _ in KEYS:
            self.assertNotIn(reset_for(section, key), result.stderr)

    def test_all_kdeglobals_diagnostics_share_one_run_in_recipe_order(self):
        # The staged color-scheme and look-and-feel selections and the five
        # font keys warn in one run; each keeps its existing wording and the
        # lines appear in recipe order (color scheme, widget style, icon
        # theme, then the six font lines).
        tmp, config = make_config_home(self)
        path = write_selection(
            config,
            "[General]\nColorScheme=MacOS8\nfont=Lato,10\nfixed=" + FIXED_VALUE + "\nmenuFont=ChicagoFLF,10\n"
            "toolBarFont=Lato,10\nsmallestReadableFont=Lato,8\n"
            "[KDE]\nwidgetStyle=kvantum\n"
            "[Icons]\nTheme=" + ICON_THEME_ID + "\n"
            "[WM]\nactiveFont=ChicagoFLF,10\n",
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        order = [
            "uninstall: color scheme MacOS8 is still selected in " + path,
            "uninstall: the widget-style selection the look-and-feel apply wrote",
            "uninstall: the icon-theme selection the look-and-feel apply wrote",
        ] + [rule_for(path, *triple) for triple in KEYS]
        for fragment in order:
            self.assertIn(fragment, result.stderr)
        for earlier, later in zip(order, order[1:]):
            self.assertLess(result.stderr.index(earlier), result.stderr.index(later))
        self.assertEqual(original, read_bytes(path))

    def test_the_fixed_selection_warns_with_its_own_value(self):
        # The fixed-width selection's published value is the Qt 6 serialized
        # QFont form naming JetBrains Mono, not a short family,size form: a
        # diagnostic keyed on `JetBrains Mono,10` would miss the real line.
        self.assertIn(("General", "fixed", FIXED_VALUE), KEYS)
        tmp, config = make_config_home(self)
        path = write_selection(config, "[General]\nfixed=" + FIXED_VALUE + "\n")
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path, "General", "fixed", FIXED_VALUE), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_make_n_uninstall_still_parses(self):
        # The internal recipe is pinned by drying it directly, as the other
        # uninstall diagnostic suites do.
        assert_make_n_uninstall_parses(self)


if __name__ == "__main__":
    unittest.main()
