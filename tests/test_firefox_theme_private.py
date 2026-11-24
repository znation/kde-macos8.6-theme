"""Private-window tab panel face in the Firefox chrome sheet."""

from __future__ import annotations

import unittest

from support.firefox.chrome_cases import FirefoxChromeTestCase

PRIVATE_ROOT = ':root[privatebrowsingmode="temporary"]'


class TestFirefoxPrivateWindowFace(FirefoxChromeTestCase):
    """The private window's content face matches the ordinary window's."""

    def test_private_tabpanel_face_overrides_the_stock_gradient(self):
        # Firefox's stock content-area sheet sets this variable to a purple
        # gradient with !important; the shipped sheet must override it with a
        # user-sheet !important so the private window keeps a flat face.
        self.assertIn(PRIVATE_ROOT, self.rules)
        self.assertEqual(
            self.rules[PRIVATE_ROOT],
            {"--tabpanel-background-color": "#F9F9FB !important"},
        )


if __name__ == "__main__":
    unittest.main()
