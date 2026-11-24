"""Private-window toolbar ink in the Firefox chrome sheet."""

from __future__ import annotations

import unittest

from support.firefox.chrome_cases import FirefoxChromeTestCase

PRIVATE_ROOT = ':root[privatebrowsingmode="temporary"]'


class TestFirefoxPrivateWindowInk(FirefoxChromeTestCase):
    """A private window's chrome text and icons are black on the grey face."""

    def test_private_chrome_ink_is_black(self):
        # Firefox's dark private variant turns these stock tokens white; they
        # are the names the installed ESR reads for toolbar text and icons.
        self.assertEqual(
            self.rules[PRIVATE_ROOT],
            {
                "--toolbox-text-color": "#000000 !important",
                "--toolbox-text-color-inactive": "#000000 !important",
                "--toolbar-text-color": "#000000 !important",
                "--toolbarbutton-icon-fill": "#000000 !important",
            },
        )


if __name__ == "__main__":
    unittest.main()
