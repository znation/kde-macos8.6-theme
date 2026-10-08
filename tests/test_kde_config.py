"""The KDE INI reader must match Plasma's own config semantics.

`test_colorscheme`, `test_lookandfeel` and `test_desktoptheme` parse theme
files through `kde_config.read`, but they exercise only a few of its settings.
The tests below pin the reader's two `configparser` deviations from the
defaults — `%` is literal, and key names keep their case — and that the file
is explicitly decoded as UTF-8.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import kde_config


class TestReadKdeConfig(unittest.TestCase):
    def _read(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "theme.ini"
            path.write_text(text, encoding="utf-8")
            return kde_config.read(path)

    def test_percent_in_value_is_not_interpolated(self):
        # Plasma values may contain a literal '%' (e.g. a colour or a path).
        # configparser's default interpolation raises InterpolationSyntaxError
        # on get() for '100%', so read() must disable interpolation.
        parser = self._read("[Colors:Button]\nBackgroundNormal=100%\n")
        self.assertEqual(parser.get("Colors:Button", "BackgroundNormal"), "100%")

    def test_key_names_are_case_sensitive(self):
        # KDE keys are case-sensitive. configparser's default optionxform
        # lowercases them, which makes the two keys below collide and raises
        # DuplicateOptionError, so read() must keep the original case.
        parser = self._read("[Colors:Button]\nBackgroundNormal=1\nbackgroundnormal=2\n")
        section = parser["Colors:Button"]
        self.assertEqual(section["BackgroundNormal"], "1")
        self.assertEqual(section["backgroundnormal"], "2")

    def test_values_are_read_as_utf8(self):
        # Theme labels and paths can hold non-ASCII text; the file must be
        # decoded as UTF-8 rather than the platform locale's encoding. The
        # locale here is UTF-8, so the decoded text cannot distinguish the
        # explicit encoding from the default; pin the argument read() passes
        # to open() instead.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "theme.ini"
            path.write_text("[Desktop Entry]\nName=Caf\u00e9\n", encoding="utf-8")
            with mock.patch.object(kde_config, "open", create=True, wraps=open) as spy:
                parser = kde_config.read(path)
        self.assertEqual(spy.call_args.kwargs.get("encoding"), "utf-8")
        self.assertEqual(parser.get("Desktop Entry", "Name"), "Caf\u00e9")


if __name__ == "__main__":
    unittest.main()
