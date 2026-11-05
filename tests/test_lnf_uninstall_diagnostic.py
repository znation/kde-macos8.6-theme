"""Makefile tests for the `_uninstall` kdeglobals global-theme diagnostic.

`make apply`'s first required step applies the shipped look-and-feel with
`lookandfeeltool -a`, which publishes the global-theme selection as
`[KDE] LookAndFeelPackage=org.macos8.desktop` in the user's `kdeglobals`;
`make uninstall` then deletes the installed look-and-feel package
(`$(LNF_INSTALL_DIR)/$(LNF_ID)`), and Plasma keeps naming the removed
global theme. `_uninstall` prints one diagnostic naming the matching
`kwriteconfig6 --delete` reset when the key's last value inside `[KDE]`
still trims to exactly the published one, without editing the file. The
command runs through the shared `_uninstall` kdeglobals scanner the
landed widget-style/icon-theme diagnostic pins, so that suite keeps its
exact wording and this module must not touch it or its other files.
"""

import os
import unittest

from support import theme_install
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir

LNF_VALUE = "org.macos8.desktop"
RESET = (
    "kwriteconfig6 --file kdeglobals --group KDE --key LookAndFeelPackage --delete"
)
# The wording is the contract, pinned by the plan's acceptance criteria.
LINE_HEAD = (
    "uninstall: the global theme the look-and-feel apply step selected "
    "([KDE] LookAndFeelPackage=" + LNF_VALUE + ") is still in "
)
LINE_TAIL = (
    " after removal; Plasma keeps naming the removed global theme and draws "
    "the stock look-and-feel on the next start. Reset it with: " + RESET
)
COLOR_SCHEME_ID = "MacOS8"
ICON_THEME_ID = "org.macos8.desktop"


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def write_selection(config, body):
    """Write *body* as `<config>/kdeglobals`; return its path."""
    path = os.path.join(config, "kdeglobals")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(body.encode("utf-8") if isinstance(body, str) else body)
    return path


def rule_for(path):
    """The expected diagnostic line (the wording is the contract)."""
    return LINE_HEAD + path + LINE_TAIL


class TestLnfUninstallDiagnostic(unittest.TestCase):
    """`make _uninstall` names the global-theme reset when the selection is ours."""

    def uninstall_with_config(self, tmp, config, env=None):
        return theme_install.uninstall_recipe(
            tmp,
            extra=(),
            env=env if env is not None else dict(os.environ, XDG_CONFIG_HOME=config),
        )

    def test_warns_and_names_the_reset_when_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config, "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n"
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        # A diagnostic must not edit the user's kdeglobals.
        self.assertEqual(original, read_bytes(path))

    def test_warns_when_the_value_only_trims_to_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config, "  [KDE]  \n LookAndFeelPackage = " + LNF_VALUE + "  \n"
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warns_for_a_bom_prefixed_file_with_comments_crlf_and_indents(self):
        # The apply would never write this shape, but an editor BOM-save plus
        # CRLF endings must not hide the selection from the scanner: it
        # strips the first line's BOM and trims every line.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config,
            "\ufeff# header\r\n; another comment\r\n[KDE]\r\n"
            "  LookAndFeelPackage = " + LNF_VALUE + "  \r\n",
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warned_when_an_earlier_foreign_value_precedes_ours(self):
        # The scanner takes the last duplicate's value, as the other
        # uninstall diagnostics already do.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config, "[KDE]\nLookAndFeelPackage=BreezeDark\n"
            "LookAndFeelPackage=" + LNF_VALUE + "\n"
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warns_when_an_unterminated_header_leaves_the_section(self):
        # A header that never closes is skipped without changing the
        # section, so the keys stay in the group they opened.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config, "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n[KDE\n"
            "LookAndFeelPackage=" + LNF_VALUE + "\n"
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_not_warned_for_a_later_foreign_duplicate_overriding_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(
            config, "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n"
            "LookAndFeelPackage=BreezeDark\n"
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_for_a_foreign_or_empty_last_value(self):
        for last in ["BreezeDark", ""]:
            with self.subTest(last=last):
                tmp = str(make_tmp_dir(self))
                config = os.path.join(tmp, "config")
                write_selection(
                    config, "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n"
                    "LookAndFeelPackage=" + last + "\n"
                )

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(RESET, result.stderr)

    def test_not_warned_for_a_case_mismatch(self):
        # Keys are case-sensitive, as the landed kdeglobals diagnostics are.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(
            config, "[KDE]\nlookandfeelpackage=" + LNF_VALUE + "\n"
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_independent_of_the_key_living_in_another_group(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(
            config,
            "[General]\nLookAndFeelPackage=" + LNF_VALUE + "\n",
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_silent_when_there_is_no_kdeglobals(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        os.makedirs(config, exist_ok=True)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_silent_when_the_path_is_a_directory(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        os.makedirs(os.path.join(config, "kdeglobals"), exist_ok=True)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_silent_for_a_file_without_the_group_or_without_the_key(self):
        for body in (
            "[Other]\nname=whatever\n",
            "[General]\nColorScheme=" + COLOR_SCHEME_ID + "\n",
            "[KDE]\nsingleClick=true\n",
        ):
            with self.subTest(body=body):
                tmp = str(make_tmp_dir(self))
                config = os.path.join(tmp, "config")
                write_selection(config, body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(RESET, result.stderr)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the existing diagnostics, the guard ignores an unset
        # XDG_CONFIG_HOME and reads `$HOME/.config`.
        tmp = str(make_tmp_dir(self))
        home = os.path.join(tmp, "home")
        config = os.path.join(home, ".config")
        path = write_selection(config, "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n")
        env = theme_install.make_env("XDG_CONFIG_HOME")
        env["HOME"] = home

        result = theme_install.uninstall_recipe(str(make_tmp_dir(self)), extra=(), env=env)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(
            "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n",
            read_bytes(path).decode("utf-8"),
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        tmp = str(make_tmp_dir(self))
        home = os.path.join(tmp, "home")
        config = os.path.join(home, ".config")
        path = write_selection(config, "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n")
        env = theme_install.make_env("XDG_CONFIG_HOME")
        env["HOME"] = home
        env["XDG_CONFIG_HOME"] = "relative/config"

        result = theme_install.uninstall_recipe(str(make_tmp_dir(self)), extra=(), env=env)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(
            "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n",
            read_bytes(path).decode("utf-8"),
        )

    def test_without_a_config_home_nothing_is_checked(self):
        # With neither an absolute XDG_CONFIG_HOME nor an absolute HOME there
        # is no config home to read, so the diagnostic must be skipped.
        tmp = str(make_tmp_dir(self))
        env = theme_install.make_env("XDG_CONFIG_HOME", "HOME")

        result = theme_install.uninstall_recipe(tmp, extra=(), env=env)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_all_kdeglobals_diagnostics_share_one_run_in_recipe_order(self):
        # The staged color-scheme, widget-style, icon-theme and global-theme
        # selections warn in one run; each keeps its landed wording and the
        # lines appear in recipe order (color scheme, widget style, icon
        # theme, then the global theme).
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config,
            "[General]\nColorScheme=" + COLOR_SCHEME_ID + "\n"
            "[KDE]\nwidgetStyle=kvantum\nLookAndFeelPackage=" + LNF_VALUE + "\n"
            "[Icons]\nTheme=" + ICON_THEME_ID + "\n",
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        order = [
            "uninstall: color scheme " + COLOR_SCHEME_ID + " is still selected in " + path,
            "uninstall: the widget-style selection the look-and-feel apply wrote",
            "uninstall: the icon-theme selection the look-and-feel apply wrote",
            rule_for(path),
        ]
        for fragment in order:
            self.assertIn(fragment, result.stderr)
        for earlier, later in zip(order, order[1:]):
            self.assertLess(result.stderr.index(earlier), result.stderr.index(later))
        self.assertEqual(original, read_bytes(path))

    def test_the_font_diagnostics_keep_their_own_lines_beside_ours(self):
        # The landed five Lato font lines share the same kdeglobals reads
        # in one run; the font block sits before this block, so the five
        # font lines appear before the global-theme line, whose own
        # wording stays unchanged.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config,
            "[General]\nfont=Lato,10\n"
            "[KDE]\nLookAndFeelPackage=" + LNF_VALUE + "\n",
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        font_rule = (
            "uninstall: the font selection [General] font=Lato,10 "
            "the look-and-feel apply wrote is still in " + path
        )
        self.assertIn(font_rule, result.stderr)
        self.assertIn(rule_for(path), result.stderr)
        self.assertLess(
            result.stderr.index(font_rule), result.stderr.index(rule_for(path))
        )
        self.assertEqual(original, read_bytes(path))

    def test_make_n_uninstall_still_parses(self):
        # The internal recipe is pinned by drying it directly, as the other
        # uninstall diagnostic suites do.
        result = theme_install.run_make(
            ["-n", "_uninstall"], env=theme_install.make_env()
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("tools/uninstall_diagnostics.py", result.stdout)
        self.assertIn('--lnf-id "org.macos8.desktop"', result.stdout)


if __name__ == "__main__":
    unittest.main()
