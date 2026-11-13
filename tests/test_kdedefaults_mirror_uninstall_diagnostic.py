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
    read_bytes,
    write_file,
)
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_config_home, make_tmp_dir

LNF_ID = "org.macos8.desktop"




def widget_rule(path):
    """The expected mirror widget-style line (the wording is the contract)."""
    return (
        "uninstall: the widget-style selection the look-and-feel apply left "
        "in defaults ([KDE] widgetStyle=kvantum) is still in " + path +
        " after removal; when the live key is absent or reset away, the "
        "defaults layer re-selects the style that key names. Reset it with: "
        "kwriteconfig6 --file \"" + path + "\" --group KDE --key widgetStyle "
        "--delete"
    )


def icons_rule(path):
    """The expected mirror icon-theme line (the wording is the contract)."""
    return (
        "uninstall: the icon-theme selection the look-and-feel apply left "
        "in defaults ([Icons] Theme=" + LNF_ID + ") is still in " + path +
        " after removal; when the live key is absent or reset away, the "
        "defaults layer re-selects the removed icon theme and KDE and Qt "
        "applications keep the default icons. Reset it with: kwriteconfig6 "
        "--file \"" + path + "\" --group Icons --key Theme --delete"
    )


def mirror_kwinrc_rule(path):
    """The expected mirror decoration-pair line (wording is the contract)."""
    return (
        "uninstall: the window-decoration selection [library="
        "org.kde.kwin.aurorae, theme=" + LNF_ID +
        "] that the look-and-feel apply left in defaults is still in " +
        path + "; when the live keys are absent or reset away, the defaults "
        "layer re-selects the removed kwin/decorations/org.macos8.desktop "
        "decoration package and KWin keeps a "
        "default window decoration. Reset it with: kwriteconfig6 --file \"" +
        path + "\" --group org.kde.kdecoration2 --key library --delete && "
        "kwriteconfig6 --file \"" + path +
        "\" --group org.kde.kdecoration2 --key theme --delete"
    )


def mirror_plasmarc_rule(path):
    """The expected mirror desktop-theme line (wording is the contract)."""
    return (
        "uninstall: the desktop theme selection the look-and-feel apply "
        "left in defaults still names " + LNF_ID + " after removal in" +
        " " + path + "; when the live key is absent or reset away, the "
        "defaults layer re-selects the removed desktop theme. Reset it "
        "with: kwriteconfig6 --file \"" + path + "\" --group Theme --key name "
        "--delete"
    )


def scratch_home(case):
    """A temporary config home with the `kdedefaults/` directory created."""
    tmp, config = make_config_home(case)
    os.makedirs(os.path.join(config, "kdedefaults"), exist_ok=True)
    return tmp, config


def run_uninstall(tmp, config, env=None):
    """Run the uninstall recipe with XDG_CONFIG_HOME at *config*, or with *env*."""
    return theme_install.uninstall_recipe(
        tmp,
        extra=(),
        env=env if env is not None else dict(os.environ, XDG_CONFIG_HOME=config),
    )


def mirror_paths(config):
    """The three mirror paths under *config*, in recipe order."""
    return (
        os.path.join(config, "kdedefaults", "kdeglobals"),
        os.path.join(config, "kdedefaults", "kwinrc"),
        os.path.join(config, "kdedefaults", "plasmarc"),
    )


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
        order = (
            result.stderr.index(widget_rule(kglobal_path)),
            result.stderr.index(icons_rule(kglobal_path)),
            result.stderr.index(mirror_kwinrc_rule(kwin_path)),
            result.stderr.index(mirror_plasmarc_rule(plasma_path)),
        )
        self.assertEqual(list(order), sorted(order))
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

    # -- silent shapes -------------------------------------------------------

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
        order = (
            result.stderr.index(
                "uninstall: the window-decoration selection [library="
                "org.kde.kwin.aurorae, theme=" + LNF_ID + "]"
            ),
            result.stderr.index("uninstall: the splash selection"),
            result.stderr.index("uninstall: the look-and-feel package default"),
            result.stderr.index(widget_rule(kglobal_path)),
            result.stderr.index(icons_rule(kglobal_path)),
            result.stderr.index(mirror_kwinrc_rule(kwin_path)),
            result.stderr.index(mirror_plasmarc_rule(plasma_path)),
        )
        self.assertEqual(list(order), sorted(order))
        for path in (ksplash, package) + mirror_paths(config) + (live_kwinrc,):
            with self.subTest(path=path):
                self.assertTrue(os.path.isfile(path))

    def test_make_n_uninstall_still_parses(self):
        assert_make_n_uninstall_parses(self, '--lnf-id "org.macos8.desktop"')


if __name__ == "__main__":
    unittest.main()
