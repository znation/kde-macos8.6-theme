"""Validate GTK 3 needs-attention badge declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeAttention(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_needs_attention_badges(self):
        """Needs-attention labels and images keep no stock accent pulse."""
        spellings = (
            "stacksidebar row.needs-attention > label",
            ".stack-switcher > button.needs-attention > label",
            ".stack-switcher > button.needs-attention > image",
        )
        self.assert_rule_group(
            {selector: {"animation": "none", "background-image": "none"}
             for selector in spellings}
        )
        # Source order: the restated group sits after the existing
        # stack-switcher checked face group. Stock spells the switcher as
        # the .stack-switcher class, so the restatement must be the same
        # byte-equal spelling to win the cascade.
        self.assertGreater(
            self.selectors.index(".stack-switcher > button.needs-attention"
                                 " > label"),
            self.selectors.index("stackswitcher > button:checked:hover"),
        )
        # The restated spellings are the only needs-attention arms the sheet
        # declares: the scan kills renamed and stray variants.
        self.assertEqual(
            {selector for selector in self.rules
             if "needs-attention" in selector},
            set(spellings),
        )


if __name__ == "__main__":
    unittest.main()
