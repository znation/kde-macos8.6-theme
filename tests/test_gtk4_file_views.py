"""GTK 4 file-browser view-surface checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import VIEW_BACKGROUND


class TestGtk4FileViews(Gtk4SheetRuleCases, unittest.TestCase):
    def test_content_view_field_and_hover(self):
        self.assert_rule(".content-view", VIEW_BACKGROUND)
        self.assert_rule(".content-view:hover", {"-gtk-icon-filter": "none"})

    def test_server_list_button_rotation_motion(self):
        # The places view's server-button icon keeps stock's two
        # orientations (upright at rest, half a turn while checked) while
        # the 200ms rotation ease is erased: the two byte-equal stock twin
        # spellings declare only `transition: none`, sitting after the
        # existing caps-lock groups at the sheet tail.
        selectors = (
            "placesview .server-list-button > image",
            "placesview .server-list-button:checked > image",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assert_rule(selector, {"transition": "none"})
                # Exact-dict, not the per-property subset: a stray
                # rotation, transform, colour or geometry declaration on
                # either twin must fail, per the entry's guarantee.
                self.assertEqual(self.rules[selector], {"transition": "none"}, selector)
        self.assertEqual(
            {s for s in self.rules if "server-list-button" in s},
            set(selectors),
        )
        self.assertGreater(
            self.selectors.index("placesview .server-list-button > image"),
            self.selectors.index("entry.password image.caps-lock-indicator"),
        )


if __name__ == "__main__":
    unittest.main()
