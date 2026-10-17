"""Tests for tools/theme_defaults.py, the global theme's ``defaults`` reader."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import repo_root  # noqa: F401
from tools import theme_defaults  # noqa: E402


class TestDefaultsGroups(unittest.TestCase):
    def test_reads_the_decoration_and_desktop_theme_from_the_global_theme(self):
        groups = theme_defaults.defaults_groups()
        decoration = groups[("kwinrc", "org.kde.kdecoration2")]
        self.assertEqual("__aurorae__svg__org.macos8.desktop", decoration["theme"])
        self.assertEqual("org.macos8.desktop", groups[("plasmarc", "Theme")]["name"])

    def test_skips_sections_that_name_no_config_file(self):
        groups = theme_defaults.defaults_groups()
        self.assertNotIn("Wallpaper", {group for _, group in groups})

    def test_parses_comments_blank_lines_and_spacing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "defaults"
            path.write_text(
                "# note\n[a][B]\n k = v \n\n[Plain]\nx=1\n[a][C]\nz=2=3\n",
                encoding="utf-8",
            )
            self.assertEqual(
                {("a", "B"): {"k": "v"}, ("a", "C"): {"z": "2=3"}},
                theme_defaults.defaults_groups(path),
            )


class TestWriteConfigs(unittest.TestCase):
    def test_written_configs_follow_the_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            theme_defaults.write_configs(Path(directory), ("kwinrc", "plasmarc"))
            kwinrc = (Path(directory) / "kwinrc").read_text(encoding="utf-8")
            plasmarc = (Path(directory) / "plasmarc").read_text(encoding="utf-8")
            self.assertEqual({"kwinrc", "plasmarc"}, set(os.listdir(directory)))
        self.assertIn("[org.kde.kdecoration2]\n", kwinrc)
        self.assertIn("theme=__aurorae__svg__org.macos8.desktop\n", kwinrc)
        self.assertIn("[Theme]\nname=org.macos8.desktop\n", plasmarc)
        self.assertNotIn("ColorScheme", kwinrc + plasmarc)


if __name__ == "__main__":
    unittest.main()
