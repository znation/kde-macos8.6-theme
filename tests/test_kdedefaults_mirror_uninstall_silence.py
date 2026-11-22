"""Makefile tests for the silent shapes of the `_uninstall` kdedefaults mirror diagnostics.

The mirror diagnostics in test_kdedefaults_mirror_uninstall_diagnostic print one
line per still-standing selection. This module pins the shapes that print
nothing: an absent kdedefaults directory, a non-regular file, a missing group
or key, a foreign or empty last value, a later foreign override, and the
one-key, other-group and NoPlugin-only cases. The warn shapes stay in the
diagnostic module.
"""

import os
import unittest

from support.process_assertions import assert_succeeded
from support.theme_install import write_file
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
from support.tmp_dir import make_config_home


class TestKdedefaultsMirrorUninstallSilence(unittest.TestCase):
    """`make _uninstall` stays quiet about the mirror selections that are not ours."""

    def test_silent_without_a_kdedefaults_directory(self):
        tmp, config = make_config_home(self)
        os.makedirs(config, exist_ok=True)

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        for path in mirror_paths(config):
            self.assertNotIn(os.path.basename(path), result.stderr)

    def test_silent_when_a_path_is_a_non_regular_file(self):
        for name in ("kdeglobals", "kwinrc", "plasmarc"):
            with self.subTest(name=name):
                tmp, config = scratch_home(self)
                os.makedirs(
                    os.path.join(config, "kdedefaults", name), exist_ok=True
                )

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn("kdedefaults/" + name, result.stderr)

    def test_silent_for_a_missing_group_or_a_missing_key(self):
        for name, body in (
            ("kdeglobals", "widgetStyle=kvantum\n"),  # no [KDE] group above
            ("kdeglobals", "[KDE]\n"),  # group without the key
            ("kdeglobals", "[Icons]\nThemeSet=breeze\n"),
            ("kwinrc", "[org.kde.kdecoration2]\nNoPlugin=false\n"),
            ("kwinrc", "[org.kde.kdecoration2]\nlibrary=\n"),
            ("plasmarc", "[Theme]\nSomething=" + LNF_ID + "\n"),
        ):
            with self.subTest(name=name):
                tmp, config = scratch_home(self)
                write_file(os.path.join(config, "kdedefaults", name), body)

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                kglobal_path, kwin_path, plasma_path = mirror_paths(config)
                self.assertNotIn(widget_rule(kglobal_path), result.stderr)
                self.assertNotIn(icons_rule(kglobal_path), result.stderr)
                self.assertNotIn(mirror_kwinrc_rule(kwin_path), result.stderr)
                self.assertNotIn(mirror_plasmarc_rule(plasma_path), result.stderr)

    def test_silent_for_a_foreign_or_empty_last_value(self):
        for name, body in (
            ("kdeglobals", "[KDE]\nwidgetStyle=breeze\n"),
            ("kdeglobals", "[KDE]\nwidgetStyle=\n"),
            ("kdeglobals", "[Icons]\nTheme=breeze\n"),
            ("kdeglobals", "[Icons]\nTheme=\n"),
            (
                "kwinrc",
                "[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae\n"
                "theme=breeze\n",
            ),
            ("kwinrc", "[org.kde.kdecoration2]\nlibrary=\ntheme=\n"),
            ("plasmarc", "[Theme]\nname=breeze\n"),
            ("plasmarc", "[Theme]\nname=\n"),
        ):
            with self.subTest(name=name):
                tmp, config = scratch_home(self)
                write_file(os.path.join(config, "kdedefaults", name), body)

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                kglobal_path, kwin_path, plasma_path = mirror_paths(config)
                self.assertNotIn(widget_rule(kglobal_path), result.stderr)
                self.assertNotIn(icons_rule(kglobal_path), result.stderr)
                self.assertNotIn(mirror_kwinrc_rule(kwin_path), result.stderr)
                self.assertNotIn(mirror_plasmarc_rule(plasma_path), result.stderr)

    def test_silent_when_a_later_foreign_value_overrides_ours(self):
        for name, body in (
            (
                "kdeglobals",
                "[KDE]\nwidgetStyle=kvantum\nwidgetStyle=breeze\n"
                "[Icons]\nTheme=" + LNF_ID + "\nTheme=breeze\n",
            ),
            (
                "kwinrc",
                "[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae\n"
                "theme=" + LNF_ID + "\nlibrary=other\n",
            ),
            ("plasmarc", "[Theme]\nname=" + LNF_ID + "\nname=breeze\n"),
        ):
            with self.subTest(name=name):
                tmp, config = scratch_home(self)
                path = write_file(
                    os.path.join(config, "kdedefaults", name), body
                )

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                expected_silent = {
                    "kdeglobals": (widget_rule(path), icons_rule(path)),
                    "kwinrc": (mirror_kwinrc_rule(path),),
                    "plasmarc": (mirror_plasmarc_rule(path),),
                }[name]
                for rule_text in expected_silent:
                    self.assertNotIn(rule_text, result.stderr)

    def test_silent_when_either_kdeglobals_selection_is_foreign(self):
        # The two kdeglobals lines are independent: a foreign [Icons] Theme
        # leaves a matching [KDE] widgetStyle warning alone, and vice versa.
        for body, expected in (
            (
                "[KDE]\nwidgetStyle=kvantum\n[Icons]\nTheme=breeze\n",
                "widget",
            ),
            (
                "[KDE]\nwidgetStyle=breeze\n[Icons]\nTheme=" + LNF_ID + "\n",
                "icons",
            ),
        ):
            with self.subTest(expected=expected):
                tmp, config = scratch_home(self)
                path = write_file(
                    os.path.join(config, "kdedefaults", "kdeglobals"), body
                )

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                if expected == "widget":
                    self.assertIn(widget_rule(path), result.stderr)
                    self.assertNotIn(icons_rule(path), result.stderr)
                else:
                    self.assertIn(icons_rule(path), result.stderr)
                    self.assertNotIn(widget_rule(path), result.stderr)

    def test_silent_when_either_kwinrc_pair_key_fails_alone(self):
        for body, keep in (
            ("[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae\n", "library"),
            (
                "[org.kde.kdecoration2]\ntheme="
                + LNF_ID
                + "\n",
                "theme",
            ),
        ):
            with self.subTest(keep=keep):
                tmp, config = scratch_home(self)
                path = write_file(
                    os.path.join(config, "kdedefaults", "kwinrc"), body
                )

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                self.assertNotIn(mirror_kwinrc_rule(path), result.stderr)

    def test_silent_when_noplugin_matches_without_the_pair(self):
        tmp, config = scratch_home(self)
        path = write_file(
            os.path.join(config, "kdedefaults", "kwinrc"),
            "[org.kde.kdecoration2]\nNoPlugin=false\n",
        )

        result = run_uninstall(tmp, config)

        assert_succeeded(self, result)
        self.assertNotIn(mirror_kwinrc_rule(path), result.stderr)
        self.assertNotIn("NoPlugin", result.stderr)

    def test_silent_when_the_selections_live_in_other_groups(self):
        for name, body in (
            ("kdeglobals", "[General]\nwidgetStyle=kvantum\nTheme=" + LNF_ID + "\n"),
            ("kwinrc", "[Misc]\nlibrary=org.kde.kwin.aurorae\ntheme=" + LNF_ID + "\n"),
            ("plasmarc", "[General]\nname=" + LNF_ID + "\n"),
        ):
            with self.subTest(name=name):
                tmp, config = scratch_home(self)
                write_file(os.path.join(config, "kdedefaults", name), body)

                result = run_uninstall(tmp, config)

                assert_succeeded(self, result)
                path = os.path.join(config, "kdedefaults", name)
                self.assertNotIn(widget_rule(path), result.stderr)
                self.assertNotIn(icons_rule(path), result.stderr)
                self.assertNotIn(mirror_kwinrc_rule(path), result.stderr)
                self.assertNotIn(mirror_plasmarc_rule(path), result.stderr)


if __name__ == "__main__":
    unittest.main()
