"""Pins for the kwinrc uninstall-diagnostic suites' shared body builders.

`tests/support/kwinrc_uninstall_wording.py` shares the kwinrc body bytes
the aurorae-pair and theme-key suites stage as file content for the
`make _uninstall` scanners to parse; a missing newline, a swapped key or a
dropped value would silently change which shape a suite exercises. These
pins hold each builder's exact output, restating the plain bodies the two
suites hand-wrote before the builders shared them.
"""

import unittest

from support.kwinrc_uninstall_wording import (
    REMOVAL_GROUP,
    aurorae_pair_body,
    aurorae_pair_lines,
    aurorae_theme_body,
    aurorae_theme_lines,
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
