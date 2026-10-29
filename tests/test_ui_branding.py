"""Theme selection metadata uses neutral Platinum display labels."""
import configparser
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r"apple|mac\s*os", re.IGNORECASE)


class TestUiBranding(unittest.TestCase):
    def check_fields(self, fields):
        for field in fields:
            self.assertEqual(field, "Platinum")
            self.assertIsNone(FORBIDDEN.search(field))

    def test_json_package_labels(self):
        paths = (
            "theme/look-and-feel/org.macos8.desktop/metadata.json",
            "theme/desktoptheme/org.macos8.desktop/metadata.json",
            "theme/aurorae/themes/org.macos8.desktop/metadata.json",
            "theme/wallpapers/org.macos8.desktop/metadata.json",
        )
        for path in paths:
            plugin = json.loads((ROOT / path).read_text())["KPlugin"]
            self.check_fields((plugin["Name"],))
            self.assertIsNone(FORBIDDEN.search(plugin["Description"]))

    def test_ini_and_scheme_labels(self):
        for path, section, keys in (
            ("theme/aurorae/themes/org.macos8.desktop/metadata.desktop", "Desktop Entry", ("Name", "Comment")),
            ("theme/gtk/org.macos8.desktop/index.theme", "Desktop Entry", ("Name",)),
            ("theme/gtk/org.macos8.desktop/index.theme", "X-GNOME-Metatheme", ("Name",)),
            ("theme/icons/org.macos8.desktop/index.theme", "Icon Theme", ("Name", "Comment")),
            ("theme/color-schemes/MacOS8.colors", "General", ("Name",)),
        ):
            parser = configparser.ConfigParser(interpolation=None)
            parser.read(ROOT / path)
            for key in keys:
                value = parser.get(section, key)
                expected = (
                    "Platinum"
                    if key == "Name"
                    else "Platinum window decoration for Plasma 6"
                    if key == "Comment" and path.endswith("metadata.desktop")
                    else "Platinum icon theme with original placeholder artwork"
                )
                self.assertEqual(value, expected)
                self.assertIsNone(FORBIDDEN.search(value))


if __name__ == "__main__":
    unittest.main()
