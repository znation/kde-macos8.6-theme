"""Makefile tests for the `_uninstall` kdedefaults defaults-layer diagnostics.

`make apply` runs `lookandfeeltool -a org.macos8.desktop` first, and that
tool also writes the defaults layer of the KDE config search path: a
scratch-home apply on this host left `kdedefaults/ksplashrc` holding
`[KSplash] Engine=KSplashQML` and `Theme=org.macos8.desktop`, and a flat
`kdedefaults/package` file holding exactly `org.macos8.desktop`. After
`make uninstall` removes the installed packages and the existing resets
`--delete` the live keys, a start still resolves those defaults, naming
removed ids silently; the splash selection appears nowhere else in any read
config. `_uninstall` prints one diagnostic per still-standing selection at
its recipe tail, naming the reset (`kwriteconfig6 --file <ksplashrc path>
--group KSplash --key Theme --delete` for the splash, `rm "<package path>"`
for the flat package default) without editing either file. The scanner
mirrors the shared `_uninstall` reads, so the existing diagnostics' suites
keep their exact wordings and this module must not touch them or their
files.
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
    write_file,
)
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir

LNF_ID = "org.macos8.desktop"




def splash_rule(path):
    """The expected splash diagnostic line (the wording is the contract)."""
    return (
        "uninstall: the splash selection the look-and-feel apply left in "
        f"defaults still names {LNF_ID} after removal in {path}; the start "
        "splash cannot load the removed SplashQML and keeps the platform "
        f'default splash. Reset it with: kwriteconfig6 --file "{path}" '
        "--group KSplash --key Theme --delete"
    )


def package_rule(path):
    """The expected package diagnostic line (the wording is the contract)."""
    return (
        "uninstall: the look-and-feel package default the look-and-feel "
        f"apply left in defaults still names {LNF_ID} after removal in "
        f"{path}; the defaults file the apply wrote names the removed "
        f'look-and-feel package. Reset it with: rm "{path}"'
    )


class TestKdedefaultsUninstallDiagnostic(theme_install.UninstallRecipeTestCase):
    """`make _uninstall` names the defaults-layer resets when the ids are ours."""

    def defaults_paths(self, config):
        return (
            os.path.join(config, "kdedefaults", "ksplashrc"),
            os.path.join(config, "kdedefaults", "package"),
        )

    # -- warn shapes ---------------------------------------------------------

    def test_warns_for_a_staged_splash_selection(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nEngine=KSplashQML\nTheme=" + LNF_ID + "\n",
        )
        # A diagnostic must not edit the user's defaults layer.
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            splash_rule(path),
            absent=package_rule(self.defaults_paths(config)[1]),
            unchanged=path,
        )

    def test_warns_for_a_staged_package_default(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_file(os.path.join(config, "kdedefaults", "package"), LNF_ID)
        assert_uninstall_diagnostics(
            self,
            tmp,
            config,
            package_rule(path),
            absent=splash_rule(self.defaults_paths(config)[0]),
            unchanged=path,
        )

    def test_both_staged_selections_warn_in_recipe_order(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        ksplash = write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nTheme=" + LNF_ID + "\n",
        )
        package = write_file(os.path.join(config, "kdedefaults", "package"), LNF_ID)
        splash_bytes, package_bytes = read_bytes(ksplash), read_bytes(package)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        splash_at = result.stderr.index(splash_rule(ksplash))
        package_at = result.stderr.index(package_rule(package))
        self.assertLess(splash_at, package_at)
        self.assertEqual(splash_bytes, read_bytes(ksplash))
        self.assertEqual(package_bytes, read_bytes(package))

    def test_warns_for_a_bom_prefixed_file_with_comments_and_indentation(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "﻿[KSplash]\r\n# a comment line\r\n  Theme = " + LNF_ID + "  \r\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, splash_rule(path), unchanged=path)

    def test_warns_when_the_theme_value_only_trims_to_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\n  Theme = " + LNF_ID + "  \n",
        )
        assert_uninstall_diagnostics(self, tmp, config, splash_rule(path), unchanged=path)

    def test_warns_when_an_earlier_foreign_value_precedes_ours(self):
        # The scanner takes the last duplicate's value, as the other
        # uninstall diagnostics already do.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nTheme=breeze\nTheme=" + LNF_ID + "\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, splash_rule(path), unchanged=path)

    def test_splash_reset_quotes_a_config_home_path_with_a_space(self):
        # A space is legal in XDG_CONFIG_HOME (the Makefile refuses only
        # control characters there), so the copy-pasteable reset must keep
        # the path inside its double quotes, as the package reset already
        # does.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "con fig")
        path = write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nTheme=" + LNF_ID + "\n",
        )
        assert_uninstall_diagnostics(self, tmp, config, splash_rule(path), unchanged=path)

    def test_warns_for_a_padded_or_newline_terminated_package(self):
        for body in (" " + LNF_ID + " ", LNF_ID + "\n", "  " + LNF_ID + " \n\n"):
            with self.subTest(body=body):
                tmp = str(make_tmp_dir(self))
                config = os.path.join(tmp, "config")
                path = write_file(os.path.join(config, "kdedefaults", "package"), body)
                original = read_bytes(path)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertIn(package_rule(path), result.stderr)
                self.assertEqual(original, read_bytes(path))

    def test_warns_for_a_bom_prefixed_package_file(self):
        # flat_text strips only the first line's byte-order mark, so a
        # BOM-prefixed flat package name still trims back to ours: the flat
        # scanner warns exactly as it does without the mark.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        path = write_file(
            os.path.join(config, "kdedefaults", "package"), "\ufeff" + LNF_ID
        )
        assert_uninstall_diagnostics(self, tmp, config, package_rule(path), unchanged=path)

    # -- silent shapes -------------------------------------------------------

    def test_silent_without_a_kdedefaults_directory(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        os.makedirs(config, exist_ok=True)

        result = assert_uninstall_diagnostics(self, tmp, config, absent=splash_rule(self.defaults_paths(config)[0]))
        self.assertNotIn(package_rule(self.defaults_paths(config)[1]), result.stderr)

    def test_silent_when_a_path_is_a_non_regular_file(self):
        for name in ("ksplashrc", "package"):
            with self.subTest(name=name):
                tmp = str(make_tmp_dir(self))
                config = os.path.join(tmp, "config")
                os.makedirs(os.path.join(config, "kdedefaults", name), exist_ok=True)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn("kdedefaults/" + name, result.stderr)

    def test_silent_for_a_ksplashrc_without_the_group_or_the_key(self):
        for body in (
            "[General]\nTheme=" + LNF_ID + "\n",  # id in a foreign group
            "[KSplash]\nEngine=KSplashQML\n",  # no Theme key
        ):
            with self.subTest(body=body):
                tmp = str(make_tmp_dir(self))
                config = os.path.join(tmp, "config")
                write_file(os.path.join(config, "kdedefaults", "ksplashrc"), body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(splash_rule(self.defaults_paths(config)[0]), result.stderr)

    def test_silent_for_a_foreign_or_empty_theme_value(self):
        for body in ("[KSplash]\nTheme=breeze\n", "[KSplash]\nTheme=\n"):
            with self.subTest(body=body):
                tmp = str(make_tmp_dir(self))
                config = os.path.join(tmp, "config")
                write_file(os.path.join(config, "kdedefaults", "ksplashrc"), body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(splash_rule(self.defaults_paths(config)[0]), result.stderr)

    def test_silent_when_matching_engine_leaves_a_foreign_theme(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nEngine=KSplashQML\nTheme=breeze\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=splash_rule(self.defaults_paths(config)[0]))

    def test_silent_when_a_later_foreign_value_overrides_ours(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nTheme=" + LNF_ID + "\nTheme=breeze\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=splash_rule(self.defaults_paths(config)[0]))

    def test_silent_when_an_unterminated_header_starts_no_group(self):
        # `[KSplash` is not a header, so it starts no section: the Theme line
        # that follows sits in no group and cannot warn.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash\nTheme=" + LNF_ID + "\n",
        )

        assert_uninstall_diagnostics(self, tmp, config, absent=splash_rule(self.defaults_paths(config)[0]))

    def test_silent_for_a_foreign_or_empty_package_file(self):
        for body in ("breeze", "", LNF_ID + " is the id", "x " + LNF_ID + " y"):
            with self.subTest(body=body):
                tmp = str(make_tmp_dir(self))
                config = os.path.join(tmp, "config")
                write_file(os.path.join(config, "kdedefaults", "package"), body)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(package_rule(self.defaults_paths(config)[1]), result.stderr)

    def test_silent_when_marker_bytes_reach_the_package_name(self):
        # Only a byte-order mark leading the first line is stripped; one on a
        # later line, or right behind the id, is a real byte of the flat
        # name, as the awk scanner treated it, so the joined text breaks the
        # match and the diagnostic stays silent. Nothing is edited either way.
        for body in (LNF_ID + "\n\ufeff", "\n\ufeff" + LNF_ID + "\n", "\n" + LNF_ID + "\ufeff"):
            with self.subTest(body=body):
                tmp = str(make_tmp_dir(self))
                config = os.path.join(tmp, "config")
                path = write_file(
                    os.path.join(config, "kdedefaults", "package"), body
                )
                original = read_bytes(path)

                result = self.uninstall_with_config(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(package_rule(path), result.stderr)
                self.assertEqual(original, read_bytes(path))

    # -- config home resolution ----------------------------------------------

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        assert_home_fallback(
            self,
            lambda config: write_file(
                os.path.join(config, "kdedefaults", "ksplashrc"),
                "[KSplash]\nTheme=" + LNF_ID + "\n",
            ),
            splash_rule,
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_file(
                os.path.join(config, "kdedefaults", "package"), LNF_ID
            ),
            package_rule,
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        assert_no_config_home(self, "kdedefaults/ksplashrc", "kdedefaults/package")

    # -- one run with the existing diagnostics -------------------------------

    def test_recipe_order_keeps_the_existing_aurorae_wordings_ahead(self):
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "config")
        ksplash = write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nTheme=" + LNF_ID + "\n",
        )
        kwinrc = os.path.join(config, "kwinrc")
        write_file(
            kwinrc,
            (
                "[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae\n"
                "theme=" + LNF_ID + "\n"
            ),
        )
        ksplash_bytes, kwinrc_bytes = read_bytes(ksplash), read_bytes(kwinrc)

        result = self.uninstall_with_config(tmp, config)

        assert_succeeded(self, result)
        aurorae_at = result.stderr.index(
            "uninstall: the window-decoration selection [library="
            "org.kde.kwin.aurorae, theme=" + LNF_ID + "]"
        )
        splash_at = result.stderr.index(splash_rule(ksplash))
        self.assertLess(aurorae_at, splash_at)
        self.assertEqual(ksplash_bytes, read_bytes(ksplash))
        self.assertEqual(kwinrc_bytes, read_bytes(kwinrc))

    def test_make_n_uninstall_still_parses(self):
        assert_make_n_uninstall_parses(self, '--lnf-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
