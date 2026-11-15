"""GTK 4 link checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk_css import strip_comments
from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import LINK


class TestGtk4Links(Gtk4SheetRuleCases, unittest.TestCase):
    def test_links(self):
        self.assert_links(
            ("button.link",),
            ("link", "button.link > label"),
            ("link:visited", "button.link:visited > label"),
            {"text-decoration": "underline"},
        )

    def test_inline_link_interaction_colours(self):
        css = strip_comments(self.css)
        self.assert_rule("link:hover", {"color": LINK})
        self.assert_rule("link:active", {"color": LINK})
        self.assert_disabled_text(("link:disabled",))
        hover = css.index("link:hover")
        active = css.index("link:active")
        visited = css.index("link:visited")
        disabled = css.index("link:disabled")
        self.assertLess(hover, visited)
        self.assertLess(active, visited)
        self.assertGreater(disabled, visited)

    def test_link_button_follows_the_button_state_rules(self):
        # button.link ties button:hover and :active on specificity, so only
        # coming later keeps the link button faceless while hovered or pressed.
        link = self.css.index("button.link {")
        for rule in ("button {", "button:hover {", "button:active, button:checked {"):
            self.assertGreater(link, self.css.index("\n" + rule), rule)


if __name__ == "__main__":
    unittest.main()
