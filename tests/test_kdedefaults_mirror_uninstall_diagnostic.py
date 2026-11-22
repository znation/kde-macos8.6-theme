"""Makefile tests for the `_uninstall` kdedefaults mirror diagnostics.

The same look-and-feel apply that writes the live-config selections also
left defaults-layer mirrors under `kdedefaults/`: the scratch-home apply
recorded on the existing kdedefaults diagnostics wrote `kdedefaults/kdeglobals`
holding `[Icons] Theme=org.macos8.desktop` and `[KDE] widgetStyle=kvantum`,
`kdedefaults/kwinrc` holding `[org.kde.kdecoration2]` `NoPlugin=false` beside
the `library=org.kde.kwin.aurorae` and
`theme=org.macos8.desktop` pair, and `kdedefaults/plasmarc`
holding `[Theme] name=org.macos8.desktop`. After `make uninstall` removes
the installed packages and the existing resets `--delete` the live keys, a
start still re-resolves the removed ids from these untouched mirrors.
`_uninstall` prints one diagnostic per still-standing selection (up to two
from the kdeglobals mirror) at its recipe tail, after part 1/2's splash and
package checks, naming the `kwriteconfig6 --delete` reset against the
mirror's literal path without editing any file. The scanners mirror the
existing live-config diagnostics', so this module must not change their
wordings or their files, and asserts their lines still read back unchanged.

The silent shapes, the cases that print nothing, live in
`test_kdedefaults_mirror_uninstall_silence`.
"""

import os
import unittest

from support.config_home_cases import (
    assert_home_fallback,
    assert_no_config_home,
)
from support.kde.kdedefaults_mirror_cases import (
    LNF_ID,
    icons_rule,
    mirror_kwinrc_rule,
    mirror_paths,
    mirror_plasmarc_rule,
    run_uninstall,
    scratch_home,
    widget_rule,
)
from support.theme_install import (
    assert_diagnostics_in_order,
    assert_make_n_uninstall_parses,
    read_bytes,
    write_file,
)
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir


class TestKdedefaultsMirrorUninstallDiagnostic(unittest.TestCase):
    """`make _uninstall` names the mirror resets when the selections are ours."""

    # -- warn shapes ---------------------------------------------------------

    def test_warns_for_a_staged_widget_style_mirror(self):
        tmp, config = scratch_home(self)
        path = write_file(
            os.path.join(config, "kdedefaults", "kdeglobals"),
            "[KDE]\nwidgetStyle=kvantum\n",
        )
        original = read_bytes(path)

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(widget_rule(path), result.stderr)
        self.assertNotIn(icons_rule(path), result.stderr)
        # A diagnostic must not edit the user's defaults layer.
        self.assertEqual(original, read_bytes(path))

    def test_warns_for_a_staged_icons_mirror(self):
        tmp, config = scratch_home(self)
        path = write_file(
            os.path.join(config, "kdedefaults", "kdeglobals"),
            "[Icons]\nTheme=" + LNF_ID + "\n",
        )
        original = read_bytes(path)

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(icons_rule(path), result.stderr)
        self.assertNotIn(widget_rule(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warns_for_a_staged_kwinrc_pair_mirror(self):
        tmp, config = scratch_home(self)
        path = write_file(
            os.path.join(config, "kdedefaults", "kwinrc"),
            (
                "[org.kde.kdecoration2]\nNoPlugin=false\n"
                "library=org.kde.kwin.aurorae\n"
                "theme=" + LNF_ID + "\n"
            ),
        )
        original = read_bytes(path)

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(mirror_kwinrc_rule(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_kwinrc_pair_reset_quotes_a_config_home_path_with_a_space(self):
        # A space is legal in XDG_CONFIG_HOME (the Makefile refuses only
        # control characters there), so both `--file` words of the
        # two-command reset must keep the path inside their double quotes.
        tmp = str(make_tmp_dir(self))
        config = os.path.join(tmp, "con fig")
        path = write_file(
            os.path.join(config, "kdedefaults", "kwinrc"),
            (
                "[org.kde.kdecoration2]\n"
                "library=org.kde.kwin.aurorae\n"
                "theme=" + LNF_ID + "\n"
            ),
        )
        original = read_bytes(path)

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(mirror_kwinrc_rule(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warns_for_a_staged_plasmarc_mirror(self):
        tmp, config = scratch_home(self)
        path = write_file(
            os.path.join(config, "kdedefaults", "plasmarc"),
            "[Theme]\nname=" + LNF_ID + "\n",
        )
        original = read_bytes(path)

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(mirror_plasmarc_rule(path), result.stderr)
        self.assertEqual(original, read_bytes(path))

    def test_warns_for_the_recorded_scratch_home_mirror_files(self):
        # The exact kdedefaults files the isolated apply left, so the
        # shipped diagnostics fire on the real application artifact.
        tmp, config = scratch_home(self)
        kglobal_path, kwin_path, plasma_path = mirror_paths(config)
        write_file(
            kglobal_path,
            "[Icons]\nTheme=" + LNF_ID + "\n\n[KDE]\nwidgetStyle=kvantum\n",
        )
        write_file(
            kwin_path,
            (
                "[org.kde.kdecoration2]\nNoPlugin=false\n"
                "library=org.kde.kwin.aurorae\n"
                "theme=" + LNF_ID + "\n"
            ),
        )
        write_file(plasma_path, "[Theme]\nname=" + LNF_ID + "\n")
        originals = [read_bytes(p) for p in mirror_paths(config)]

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        self.assertIn(widget_rule(kglobal_path), result.stderr)
        self.assertIn(icons_rule(kglobal_path), result.stderr)
        self.assertIn(mirror_kwinrc_rule(kwin_path), result.stderr)
        self.assertIn(mirror_plasmarc_rule(plasma_path), result.stderr)
        self.assertEqual(originals[0], read_bytes(kglobal_path))
        self.assertEqual(originals[1], read_bytes(kwin_path))
        self.assertEqual(originals[2], read_bytes(plasma_path))

    def test_four_staged_lines_warn_in_recipe_order(self):
        tmp, config = scratch_home(self)
        kglobal_path, kwin_path, plasma_path = mirror_paths(config)
        write_file(
            kglobal_path,
            "[KDE]\nwidgetStyle=kvantum\n\n[Icons]\nTheme=" + LNF_ID + "\n",
        )
        write_file(
            kwin_path,
            (
                "[org.kde.kdecoration2]\nNoPlugin=false\n"
                "library=org.kde.kwin.aurorae\n"
                "theme=" + LNF_ID + "\n"
            ),
        )
        write_file(plasma_path, "[Theme]\nname=" + LNF_ID + "\n")
        originals = [read_bytes(p) for p in mirror_paths(config)]

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        assert_diagnostics_in_order(
            self,
            result,
            [
                widget_rule(kglobal_path),
                icons_rule(kglobal_path),
                mirror_kwinrc_rule(kwin_path),
                mirror_plasmarc_rule(plasma_path),
            ],
        )
        self.assertEqual(originals[0], read_bytes(kglobal_path))
        self.assertEqual(originals[1], read_bytes(kwin_path))
        self.assertEqual(originals[2], read_bytes(plasma_path))

    def test_warns_for_a_bom_prefixed_file_with_comments_and_indentation(self):
        for name, body in (
            (
                "kdeglobals",
                "﻿[KDE]\r\n# mine\r\n  widgetStyle = kvantum  \r\n",
            ),
            (
                "kwinrc",
                "﻿[org.kde.kdecoration2]\r\nlibrary = org.kde.kwin.aurorae\r\n"
                "theme = " + LNF_ID + "\r\n",
            ),
            ("plasmarc", "﻿[Theme]\r\n  name = " + LNF_ID + "  \r\n"),
        ):
            with self.subTest(name=name):
                tmp, config = scratch_home(self)
                path = write_file(
                    os.path.join(config, "kdedefaults", name), body
                )
                original = read_bytes(path)

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                expected = {
                    "kdeglobals": widget_rule,
                    "kwinrc": mirror_kwinrc_rule,
                    "plasmarc": mirror_plasmarc_rule,
                }[name](path)
                self.assertIn(expected, result.stderr)
                self.assertEqual(original, read_bytes(path))

    def test_warns_when_values_only_trim_to_ours(self):
        for name, body, rule in (
            ("kdeglobals", "[KDE]\n  widgetStyle = kvantum  \n", widget_rule),
            ("kdeglobals", "[Icons]\n  Theme = " + LNF_ID + "  \n", icons_rule),
            (
                "kwinrc",
                "[org.kde.kdecoration2]\n  library = org.kde.kwin.aurorae\n"
                "  theme = " + LNF_ID + "  \n",
                mirror_kwinrc_rule,
            ),
            ("plasmarc", "[Theme]\n  name = " + LNF_ID + "  \n", mirror_plasmarc_rule),
        ):
            with self.subTest(name=name):
                tmp, config = scratch_home(self)
                path = write_file(
                    os.path.join(config, "kdedefaults", name), body
                )
                original = read_bytes(path)

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                self.assertIn(rule(path), result.stderr)
                self.assertEqual(original, read_bytes(path))

    def test_warns_when_an_earlier_foreign_value_precedes_ours(self):
        # The scanner takes the last duplicate's value, as the other
        # uninstall diagnostics already do.
        for name, body, rule in (
            (
                "kdeglobals",
                "[KDE]\nwidgetStyle=breeze\nwidgetStyle=kvantum\n",
                widget_rule,
            ),
            (
                "kdeglobals",
                "[Icons]\nTheme=breeze\nTheme=" + LNF_ID + "\n",
                icons_rule,
            ),
            (
                "kwinrc",
                "[org.kde.kdecoration2]\nlibrary=other\ntheme=breeze\n"
                "library=org.kde.kwin.aurorae\ntheme="
                + LNF_ID
                + "\n",
                mirror_kwinrc_rule,
            ),
            (
                "plasmarc",
                "[Theme]\nname=breeze\nname=" + LNF_ID + "\n",
                mirror_plasmarc_rule,
            ),
        ):
            with self.subTest(name=name):
                tmp, config = scratch_home(self)
                path = write_file(
                    os.path.join(config, "kdedefaults", name), body
                )
                original = read_bytes(path)

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                self.assertIn(rule(path), result.stderr)
                self.assertEqual(original, read_bytes(path))

    # -- config home resolution ----------------------------------------------

    def test_reads_the_home_fallback_when_the_config_variable_is_unset(self):
        assert_home_fallback(
            self,
            lambda config: write_file(
                os.path.join(config, "kdedefaults", "kdeglobals"),
                "[KDE]\nwidgetStyle=kvantum\n",
            ),
            widget_rule,
        )

    def test_reads_the_home_fallback_for_a_relative_xdg_config_home(self):
        assert_home_fallback(
            self,
            lambda config: write_file(
                os.path.join(config, "kdedefaults", "plasmarc"),
                "[Theme]\nname=" + LNF_ID + "\n",
            ),
            mirror_plasmarc_rule,
            relative=True,
        )

    def test_without_a_config_home_nothing_is_checked(self):
        assert_no_config_home(
            self,
            "kdedefaults/kdeglobals",
            "kdedefaults/kwinrc",
            "kdedefaults/plasmarc",
        )

    # -- one run with the existing diagnostics -------------------------------

    def test_one_run_carries_the_existing_and_mirror_lines_in_recipe_order(self):
        tmp, config = scratch_home(self)
        ksplash = write_file(
            os.path.join(config, "kdedefaults", "ksplashrc"),
            "[KSplash]\nTheme=" + LNF_ID + "\n",
        )
        package = write_file(
            os.path.join(config, "kdedefaults", "package"), LNF_ID
        )
        kglobal_path, kwin_path, plasma_path = mirror_paths(config)
        write_file(
            kglobal_path,
            "[KDE]\nwidgetStyle=kvantum\n[Icons]\nTheme=" + LNF_ID + "\n",
        )
        write_file(
            kwin_path,
            (
                "[org.kde.kdecoration2]\nNoPlugin=false\n"
                "library=org.kde.kwin.aurorae\n"
                "theme=" + LNF_ID + "\n"
            ),
        )
        write_file(plasma_path, "[Theme]\nname=" + LNF_ID + "\n")
        # A live-config diagnostic, from the existing kwinrc aurorae pair.
        live_kwinrc = os.path.join(config, "kwinrc")
        write_file(
            live_kwinrc,
            (
                "[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae\n"
                "theme=" + LNF_ID + "\n"
            ),
        )

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        assert_diagnostics_in_order(
            self,
            result,
            [
                "uninstall: the window-decoration selection [library="
                "org.kde.kwin.aurorae, theme=" + LNF_ID + "]",
                "uninstall: the splash selection",
                "uninstall: the look-and-feel package default",
                widget_rule(kglobal_path),
                icons_rule(kglobal_path),
                mirror_kwinrc_rule(kwin_path),
                mirror_plasmarc_rule(plasma_path),
            ],
        )
        for path in (ksplash, package) + mirror_paths(config) + (live_kwinrc,):
            with self.subTest(path=path):
                self.assertTrue(os.path.isfile(path))

    def test_make_n_uninstall_still_parses(self):
        assert_make_n_uninstall_parses(self, '--lnf-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
