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
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir

DTHEME_ID = "org.macos8.desktop"
RESET = "plasma-apply-desktoptheme breeze"


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def write_selection(config, body):
    """Write *body* as `<config>/plasmarc`; return its path."""
    path = os.path.join(config, "plasmarc")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(body.encode("utf-8") if isinstance(body, str) else body)
    return path


def rule_for(path, prefix="uninstall: the desktop theme selection"):
    """The expected diagnostic line naming *path* (the wording is the contract)."""
    return (
        f"{prefix} still names {DTHEME_ID} after removal in {path}; Plasma "
        "cannot load the removed desktop theme and keeps the default style. "
        f"Reset it with: {RESET}"
    )


class TestPlasmarcUninstallDiagnostic(unittest.TestCase):
    """`make _uninstall` names the desktop-theme reset when the selection is ours."""

    def uninstall_with_config(self, tmp, config, env=None):
        return theme_install.uninstall_recipe(
            tmp,
            extra=(),
            env=env if env is not None else dict(os.environ, XDG_CONFIG_HOME=config),
        )

    def test_warns_and_names_the_reset_for_a_kept_selection(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(config, "[Theme]\nname=" + DTHEME_ID + "\n")
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        # A diagnostic must not edit the user's plasmarc.
        self.assertEqual(original, read_bytes(path))

    def test_warns_when_the_value_only_trims_to_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(config, "[Theme]\n  name = " + DTHEME_ID + "  \n")
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warns_for_a_bom_prefixed_file_with_comments_and_crlf(self):
        # plasma-apply-desktoptheme would never write this shape, but an
        # editor BOM-save plus CRLF endings must not hide the selection from
        # the scanner: it strips the first line's BOM and trims every line.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config,
            "\ufeff[Theme]\r\n# a comment line\r\nname=" + DTHEME_ID + "\r\n",
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warned_when_an_earlier_foreign_value_precedes_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config, "[Theme]\nname=breeze_dark\nname=" + DTHEME_ID + "\n"
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warned_when_a_later_duplicate_names_ours(self):
        # The scanner takes the last duplicate's value, as the other four
        # uninstall diagnostics already do.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_selection(
            config, "[Theme]\nname=" + DTHEME_ID + "\ncursorTheme=ignored\nname=" + DTHEME_ID + "\n"
        )
        original = read_bytes(path)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_not_warned_for_a_foreign_value(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(config, "[Theme]\nname=breeze_dark\n")

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_for_an_empty_value(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(config, "[Theme]\nname=\n")

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_without_a_theme_group(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(config, "[General]\nname=" + DTHEME_ID + "\n")

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_when_the_key_sits_in_another_group(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(
            config, "[Theme]\nextra=1\n[Other]\nname=" + DTHEME_ID + "\n"
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_not_warned_when_a_later_foreign_value_overrides_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_selection(
            config, "[Theme]\nname=" + DTHEME_ID + "\nname=breeze_dark\n"
        )

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_silent_when_there_is_no_plasmarc(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        os.makedirs(config, exist_ok=True)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_silent_when_the_path_is_a_directory(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        os.makedirs(os.path.join(config, "plasmarc"), exist_ok=True)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        # Like the four existing diagnostics, the guard ignores an unset or
        # relative XDG_CONFIG_HOME and reads `$HOME/.config`.
        tmp = str(make_tmp_dir(self))
        home = os.path.join(tmp, "home")
        config = os.path.join(home, ".config")
        write_selection(config, "[Theme]\nname=" + DTHEME_ID + "\n")
        env = theme_install.make_env("XDG_CONFIG_HOME")
        env["HOME"] = home

        result = theme_install.uninstall_recipe(
            str(make_tmp_dir(self)), extra=(), env=env
        )

        assert_succeeded(self, result)
        self.assertIn(rule_for(os.path.join(config, "plasmarc")), result.stderr)

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        tmp = str(make_tmp_dir(self))
        home = os.path.join(tmp, "home")
        config = os.path.join(home, ".config")
        write_selection(config, "[Theme]\nname=" + DTHEME_ID + "\n")
        env = theme_install.make_env("XDG_CONFIG_HOME")
        env["HOME"] = home
        env["XDG_CONFIG_HOME"] = "relative/config"

        result = theme_install.uninstall_recipe(
            str(make_tmp_dir(self)), extra=(), env=env
        )

        assert_succeeded(self, result)
        self.assertIn(rule_for(os.path.join(config, "plasmarc")), result.stderr)

    def test_without_a_config_home_nothing_is_checked(self):
        # With neither an absolute XDG_CONFIG_HOME nor an absolute HOME there
        # is no config home to read, so the diagnostic must be skipped.
        tmp = str(make_tmp_dir(self))
        env = theme_install.make_env("XDG_CONFIG_HOME", "HOME")

        result = theme_install.uninstall_recipe(tmp, extra=(), env=env)

        assert_succeeded(self, result)
        self.assertNotIn(RESET, result.stderr)

    def test_both_diagnostics_share_one_run_with_their_landed_wordings(self):
        # The staged plasmarc selection and the pointer diagnostic's
        # kcminputrc selection can both warn in one run; each keeps its own
        # landed wording.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        plasmarc = write_selection(config, "[Theme]\nname=" + DTHEME_ID + "\n")
        kcminputrc = os.path.join(config, "kcminputrc")
        os.makedirs(config, exist_ok=True)
        with open(kcminputrc, "wb") as handle:
            handle.write(("[Mouse]\ncursorTheme=" + DTHEME_ID + "\n").encode("utf-8"))
        original = read_bytes(plasmarc)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(rule_for(plasmarc), result.stderr)
        self.assertIn(RESET, result.stderr)
        self.assertIn("plasma-apply-cursortheme breeze_cursors", result.stderr)
        self.assertIn(
            (
                "uninstall: the pointer selection still names "
                + DTHEME_ID
                + " after removal in "
                + kcminputrc
            ),
            result.stderr,
        )
        self.assertEqual(original, read_bytes(plasmarc))

    def test_make_n_uninstall_still_parses(self):
        # The public `uninstall` target only prints the guards and its nested
        # locked `make _uninstall` under -n, so the scanner's recipe is pinned
        # by drying the internal recipe directly.
        result = theme_install.run_make(
            ["-n", "_uninstall"], env=theme_install.make_env()
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("tools/uninstall_diagnostics.py", result.stdout)
        self.assertIn('--desktop-id "org.macos8.desktop"', result.stdout)


if __name__ == "__main__":
    unittest.main()
