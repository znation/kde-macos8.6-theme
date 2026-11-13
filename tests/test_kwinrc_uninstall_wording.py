"""Pins for the kwinrc uninstall-diagnostic suites' shared body builders.

`tests/support/kwinrc_uninstall_wording.py` shares the kwinrc body bytes
the aurorae-pair and theme-key suites stage as file content for the
`make _uninstall` scanners to parse; a missing newline, a swapped key or a
dropped value would silently change which shape a suite exercises. These
pins hold each builder's exact output, restating the plain bodies the
button-layout and decoration suites hand-wrote before the builders shared
them.
"""

import unittest

from support.kwinrc_uninstall_wording import (
    REMOVAL_GROUP,
    aurorae_pair_body,
    aurorae_pair_lines,
    aurorae_theme_body,
    aurorae_theme_lines,
    button_body,
    button_lines,
)


class TestButtonBuilders(unittest.TestCase):
    """The `ButtonsOnLeft=`/`ButtonsOnRight=` pair builders' exact bytes."""

    def test_the_plain_body_holds_the_header_then_both_our_values(self):
        self.assertEqual(
            button_body(),
            "[" + REMOVAL_GROUP + "]\n"
            "ButtonsOnLeft=X\n"
            "ButtonsOnRight=AL\n",
        )

    def test_the_lines_carry_only_the_two_value_lines(self):
        self.assertEqual(
            button_lines(), "ButtonsOnLeft=X\n" "ButtonsOnRight=AL\n",
        )

    def test_an_eol_override_ends_both_lines_differently(self):
        self.assertEqual(
            button_lines(eol="\r\n"),
            "ButtonsOnLeft=X\r\n" "ButtonsOnRight=AL\r\n",
        )

    def test_a_foreign_left_value_replaces_only_that_value(self):
        self.assertEqual(
            button_body(left="B"),
            "[" + REMOVAL_GROUP + "]\n" "ButtonsOnLeft=B\n" "ButtonsOnRight=AL\n",
        )

    def test_a_foreign_right_value_replaces_only_that_value(self):
        self.assertEqual(
            button_body(right="M"),
            "[" + REMOVAL_GROUP + "]\n"
            "ButtonsOnLeft=X\n"
            "ButtonsOnRight=M\n",
        )

    def test_an_empty_value_replaces_only_that_value(self):
        self.assertEqual(
            button_body(left=""),
            "[" + REMOVAL_GROUP + "]\n"
            "ButtonsOnLeft=\n"
            "ButtonsOnRight=AL\n",
        )


class TestAuroraePairBuilders(unittest.TestCase):
    """The `library=`/`theme=` pair builders' exact bytes."""

    def test_the_plain_body_holds_the_header_then_both_our_values(self):
        self.assertEqual(
            aurorae_pair_body(),
            "[" + REMOVAL_GROUP + "]\n"
            "library=org.kde.kwin.aurorae\n"
            "theme=org.macos8.desktop\n",
        )

    def test_the_lines_carry_only_the_two_value_lines(self):
        self.assertEqual(
            aurorae_pair_lines(),
            "library=org.kde.kwin.aurorae\n" "theme=org.macos8.desktop\n",
        )

    def test_an_eol_override_ends_both_lines_differently(self):
        self.assertEqual(
            aurorae_pair_lines(eol="\r\n"),
            "library=org.kde.kwin.aurorae\r\n" "theme=org.macos8.desktop\r\n",
        )

    def test_a_foreign_library_replaces_only_that_value(self):
        self.assertEqual(
            aurorae_pair_body(library="foo"),
            "[" + REMOVAL_GROUP + "]\n" "library=foo\n" "theme=org.macos8.desktop\n",
        )

    def test_a_foreign_theme_replaces_only_that_value(self):
        self.assertEqual(
            aurorae_pair_body(theme="KvArc"),
            "[" + REMOVAL_GROUP + "]\n"
            "library=org.kde.kwin.aurorae\n"
            "theme=KvArc\n",
        )


class TestComposedFourKeyBody(unittest.TestCase):
    """The recipe-order pins' staged body: the pair plus the button layout."""

    def test_the_pair_body_then_the_button_lines_compose_the_four_keys(self):
        # The aurorae-pair and decoration suites' recipe-order tests stage
        # this composition; a swapped concatenation order or a dropped
        # trailing newline would silently re-order or merge the staged keys.
        self.assertEqual(
            aurorae_pair_body() + button_lines(),
            "[" + REMOVAL_GROUP + "]\n"
            "library=org.kde.kwin.aurorae\n"
            "theme=org.macos8.desktop\n"
            "ButtonsOnLeft=X\n"
            "ButtonsOnRight=AL\n",
        )


class TestAuroraeThemeBuilders(unittest.TestCase):
    """The `theme=`-only builders' exact bytes."""

    def test_the_lines_carry_only_the_theme_value(self):
        self.assertEqual(aurorae_theme_lines(), "theme=org.macos8.desktop\n")

    def test_the_plain_body_holds_the_header_then_the_theme_value(self):
        self.assertEqual(
            aurorae_theme_body(),
            "[" + REMOVAL_GROUP + "]\n" "theme=org.macos8.desktop\n",
        )

    def test_a_foreign_theme_replaces_only_that_value(self):
        self.assertEqual(
            aurorae_theme_body(theme="KvArc"),
            "[" + REMOVAL_GROUP + "]\n" "theme=KvArc\n",
        )


if __name__ == "__main__":
    unittest.main()
