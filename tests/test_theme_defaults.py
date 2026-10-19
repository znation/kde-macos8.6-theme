"""Tests for tools/theme_defaults.py, the global theme's ``defaults`` reader."""

from __future__ import annotations

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
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
        path = make_tmp_dir(self) / "defaults"
        path.write_text(
            "# note\n[a][B]\n k = v \n\n[Plain]\nx=1\n[a][C]\nz=2=3\n",
            encoding="utf-8",
        )
        self.assertEqual(
            {("a", "B"): {"k": "v"}, ("a", "C"): {"z": "2=3"}},
            theme_defaults.defaults_groups(path),
        )

    def test_strips_a_leading_utf8_bom_before_the_first_heading(self):
        # An editor may save the contributor-supplied defaults file with a
        # UTF-8 BOM. Decoding as plain utf-8 folds the BOM into the first
        # heading, which then matches neither heading pattern and is silently
        # skipped -- dropping the whole section from the written config (the
        # render's kwinrc would lose its decoration theme). utf-8-sig strips
        # the leading BOM so the first section parses like the rest.
        path = make_tmp_dir(self) / "defaults"
        path.write_bytes(
            b"\xef\xbb\xbf[kwinrc][org.kde.kdecoration2]\ntheme=x\n"
            b"[plasmarc][Theme]\nname=y\n"
        )
        self.assertEqual(
            {
                ("kwinrc", "org.kde.kdecoration2"): {"theme": "x"},
                ("plasmarc", "Theme"): {"name": "y"},
            },
            theme_defaults.defaults_groups(path),
        )

    def test_skips_a_bare_line_inside_a_section(self):
        # A hand-edited defaults file can carry a stray line with no "="
        # inside a [file][group] section. The guard skips it; without it
        # line.split("=", 1) returns one field and unpacking raises, aborting
        # the whole parse. The keys around the bare line must survive.
        path = make_tmp_dir(self) / "defaults"
        path.write_text(
            "[a][B]\nbefore=1\nstray line\nafter=2\n",
            encoding="utf-8",
        )
        self.assertEqual(
            {("a", "B"): {"before": "1", "after": "2"}},
            theme_defaults.defaults_groups(path),
        )

    def test_rejects_a_heading_that_is_neither_plain_nor_file_group(self):
        # KDE's parser and configparser read a trailing comment after a
        # section header as the same section, so a contributor can add one
        # and `make check` stays green; the reader must not silently drop the
        # section's keys and write a config missing them. An incomplete or
        # extended bracket pair is rejected by name instead.
        path = make_tmp_dir(self) / "defaults"
        path.write_text(
            "[kwinrc][org.kde.kdecoration2] # decoration\ntheme=x\n",
            encoding="utf-8",
        )
        with self.assertRaises(ValueError) as caught:
            theme_defaults.defaults_groups(path)
        self.assertIn("malformed section heading", str(caught.exception))
        self.assertIn(
            "[kwinrc][org.kde.kdecoration2] # decoration",
            str(caught.exception),
        )


class TestWriteConfigs(unittest.TestCase):
    def test_written_configs_follow_the_defaults(self):
        directory = make_tmp_dir(self)
        theme_defaults.write_configs(directory, ("kwinrc", "plasmarc"))
        kwinrc = (directory / "kwinrc").read_text(encoding="utf-8")
        plasmarc = (directory / "plasmarc").read_text(encoding="utf-8")
        self.assertEqual({"kwinrc", "plasmarc"}, set(os.listdir(directory)))
        self.assertIn("[org.kde.kdecoration2]\n", kwinrc)
        self.assertIn("theme=__aurorae__svg__org.macos8.desktop\n", kwinrc)
        self.assertIn("[Theme]\nname=org.macos8.desktop\n", plasmarc)
        self.assertNotIn("ColorScheme", kwinrc + plasmarc)


if __name__ == "__main__":
    unittest.main()
