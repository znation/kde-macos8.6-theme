"""Makefile tests for the `_uninstall` kwinrc layout diagnostic.

`make apply` writes the theme's window-button layout with `kwriteconfig6`:
`[org.kde.kdecoration2] ButtonsOnLeft=X` and `ButtonsOnRight=AL` in `kwinrc`
(the pair `tools/apply_theme.py::DECORATION_BUTTONS` writes). `make
uninstall` removes the aurorae and look-and-feel packages but leaves those
keys, and KWin keeps honoring the Platinum box layout under its built-in
default decoration; `_uninstall` prints a diagnostic naming the
`kwriteconfig6 --delete` reset when the last values of both keys still trim
to exactly that pair, without editing the file. The scanner it runs on
mirrors the shared `_uninstall` reads the color scheme, GTK, kvconfig and
kcminputrc diagnostics already pin, so those suites keep their own exact
wordings and this module must not touch them or their files (the both-files
staged case only asserts the existing pointer wording stays intact).
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
from support.kwinrc_uninstall_wording import (
    RIGHT_KEY,
    LEFT_KEY,
    REMOVAL_GROUP,
    button_rule as rule_for,
)


def POINTER_RULE(path):
    """The existing pointer diagnostic's line (wording owned by that suite)."""
    return (
        "uninstall: the pointer selection still names org.macos8.desktop "
        f"after removal in {path}; Xcursor applications cannot load the "
        "removed cursor theme and keep the default pointer. Reset it with: "
        "plasma-apply-cursortheme breeze_cursors"
    )



def write_kwinrc(config, body):
    """Write *body* as `<config>/kwinrc`; return its path."""
    return write_config_file(config, "kwinrc", body)


def write_kcminputrc(config):
    """Stage the existing pointer selection in `<config>/kcminputrc`."""
    return write_config_file(
        config, "kcminputrc", "[Mouse]\ncursorTheme=org.macos8.desktop\n"
    )


class TestKwinrcUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the layout reset when both keys are ours."""

    def test_warns_and_names_the_reset_for_a_kept_layout(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n" + LEFT_KEY + "=X\n" + RIGHT_KEY + "=AL\n",
        )
        # A diagnostic must not edit the user's kwinrc.
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_when_values_only_trim_to_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "  [" + REMOVAL_GROUP + "]  \n "
            + LEFT_KEY
            + " = X  \n "
            + RIGHT_KEY
            + " =  AL\t\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warns_for_a_bom_prefixed_file_with_comments_and_crlf(self):
        # Editors add BOMs and CRLF endings; the scanner strips the first
        # line's BOM and trims every line, so the selection stays visible.
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "\ufeff[" + REMOVAL_GROUP + "]\r\n; a comment\r\n# another\r\n"
            + LEFT_KEY
            + "=X\r\n"
            + RIGHT_KEY
            + "=AL\r\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warned_when_an_earlier_foreign_pair_precedes_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            + LEFT_KEY
            + "=B\n"
            + RIGHT_KEY
            + "=M\n"
            + LEFT_KEY
            + "=X\n"
            + RIGHT_KEY
            + "=AL\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, rule_for(path), unchanged=path)

    def test_warned_when_a_later_duplicate_pair_names_ours(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            + LEFT_KEY
            + "=X\n"
            + RIGHT_KEY
            + "=AL\n"
            + LEFT_KEY
            + "=B\n"
            + RIGHT_KEY
            + "=M\n"
            + LEFT_KEY
            + "=X\n"
            + RIGHT_KEY
            + "=AL\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, rule_for(path))

    def test_silent_when_there_is_no_kwinrc(self):
        tmp, config = make_config_home(self)
        os.makedirs(config, exist_ok=True)

        assert_uninstall_diagnostics(self, tmp, config, absent=LEFT_KEY)

    def test_silent_when_the_path_is_a_directory(self):
        tmp, config = make_config_home(self)
        os.makedirs(os.path.join(config, "kwinrc"))

        assert_uninstall_diagnostics(self, tmp, config, absent=LEFT_KEY)

    def test_silent_without_a_decoration_group(self):
        tmp, config = make_config_home(self)
        path = write_kwinrc(config, "[Other]\n" + LEFT_KEY + "=X\n" + RIGHT_KEY + "=AL\n")
        assert_uninstall_diagnostics(self, tmp, config, absent=LEFT_KEY, unchanged=path)

    def test_silent_with_only_one_of_the_two_keys(self):
        for body in (
            "[" + REMOVAL_GROUP + "]\n" + LEFT_KEY + "=X\n",
            "[" + REMOVAL_GROUP + "]\n" + RIGHT_KEY + "=AL\n",
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                write_kwinrc(config, body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(LEFT_KEY + "=X", result.stderr)

    def test_silent_when_one_key_holds_a_foreign_value(self):
        for body in (
            "[" + REMOVAL_GROUP + "]\n" + LEFT_KEY + "=X\n" + RIGHT_KEY + "=M\n",
            "[" + REMOVAL_GROUP + "]\n" + LEFT_KEY + "=B\n" + RIGHT_KEY + "=AL\n",
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                write_kwinrc(config, body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(LEFT_KEY, result.stderr)

    def test_silent_when_either_value_is_empty(self):
        for body in (
            "[" + REMOVAL_GROUP + "]\n" + LEFT_KEY + "=\n" + RIGHT_KEY + "=AL\n",
            "[" + REMOVAL_GROUP + "]\n" + LEFT_KEY + "=X\n" + RIGHT_KEY + "=\n",
        ):
            with self.subTest(body=body):
                tmp, config = make_config_home(self)
                write_kwinrc(config, body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(LEFT_KEY, result.stderr)

    def test_silent_when_a_later_foreign_duplicate_overrides_ours(self):
        # The scanner takes the last duplicate's value, as the other four
        # diagnostics already do.
        tmp, config = make_config_home(self)
        write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n"
            + LEFT_KEY
            + "=X\n"
            + RIGHT_KEY
            + "=AL\n"
            + LEFT_KEY
            + "=B\n"
            + RIGHT_KEY
            + "=M\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=LEFT_KEY)

    def test_silent_when_our_keys_are_split_across_groups(self):
        tmp, config = make_config_home(self)
        write_kwinrc(
            config,
            "["
            + REMOVAL_GROUP
            + "]\n"
            + LEFT_KEY
            + "=X\n[Other]\n"
            + RIGHT_KEY
            + "=AL\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=LEFT_KEY)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the four existing diagnostics, the guard ignores an unset or
        # relative XDG_CONFIG_HOME and reads `$HOME/.config`.
        assert_home_fallback(
            self,
            lambda config: write_kwinrc(
                config,
                "["
                + REMOVAL_GROUP
                + "]\n"
                + LEFT_KEY
                + "=X\n"
                + RIGHT_KEY
                + "=AL\n",
            ),
            rule_for,
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_kwinrc(
                config,
                "["
                + REMOVAL_GROUP
                + "]\n"
                + LEFT_KEY
                + "=X\n"
                + RIGHT_KEY
                + "=AL\n",
            ),
            rule_for,
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        assert_no_config_home(self, LEFT_KEY)

    def test_both_diagnostics_share_one_run_with_their_existing_wordings(self):
        tmp, config = make_config_home(self)
        pointer_path = write_kcminputrc(config)
        kwin_path = write_kwinrc(
            config,
            "[" + REMOVAL_GROUP + "]\n" + LEFT_KEY + "=X\n" + RIGHT_KEY + "=AL\n",
        )
        original_pointer = read_bytes(pointer_path)
        original_kwin = read_bytes(kwin_path)

        result = assert_uninstall_diagnostics(self, tmp, config, POINTER_RULE(pointer_path))
        self.assertIn(rule_for(kwin_path), result.stderr)
        self.assertEqual(original_pointer, read_bytes(pointer_path))
        self.assertEqual(original_kwin, read_bytes(kwin_path))

    def test_make_n_uninstall_still_parses(self):
        assert_make_n_uninstall_parses(self, '--scheme-id "MacOS8"')


if __name__ == "__main__":
    unittest.main()
