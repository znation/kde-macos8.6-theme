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

from support import kde_config
from support.tmp_dir import make_tmp_dir


class TestReadKdeConfig(unittest.TestCase):
    def _read(self, text):
        path = make_tmp_dir(self) / "theme.ini"
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
        path = make_tmp_dir(self) / "theme.ini"
        path.write_text("[Desktop Entry]\nName=Caf\u00e9\n", encoding="utf-8")
        with mock.patch.object(kde_config, "open", create=True, wraps=open) as spy:
            parser = kde_config.read(path)
        self.assertEqual(spy.call_args.kwargs.get("encoding"), "utf-8")
        self.assertEqual(parser.get("Desktop Entry", "Name"), "Caf\u00e9")

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        # A theme INI is contributor-supplied, and a checked-in symlink can
        # point at a private file; configparser's errors echo the offending
        # line, so following it would leak that file's content into a failing
        # test's diagnostic. A path that resolves outside the repository must
        # be refused before it is opened.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret"
            secret.write_text("[General]\nsecret = leaked\n", encoding="utf-8")
            link = root / "MacOS8.colors"
            link.symlink_to(secret)
            with mock.patch.object(kde_config, "ROOT", root, create=True):
                with self.assertRaises(ValueError) as caught:
                    kde_config.read(link)
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # that happens to be reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            (root / "theme").mkdir(parents=True)
            target = root / "theme" / "MacOS8.colors"
            target.write_text(
                "[General]\nColorScheme=MacOS8\n", encoding="utf-8"
            )
            link = root / "link.ini"
            link.symlink_to(target)
            with mock.patch.object(kde_config, "ROOT", root, create=True):
                parser = kde_config.read(link)
        self.assertEqual(parser.get("General", "ColorScheme"), "MacOS8")


if __name__ == "__main__":
    unittest.main()
