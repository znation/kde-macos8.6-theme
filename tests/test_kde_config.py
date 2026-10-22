"""The KDE INI reader must match Plasma's own config semantics.

`test_colorscheme`, `test_lookandfeel` and `test_desktoptheme` parse theme
files through `kde_config.read`, but they exercise only a few of its settings.
The tests below pin the reader's `configparser` deviations from the defaults —
`%` is literal, key names keep their case, and each line is trimmed so leading
whitespace never starts a value continuation — and that the file is explicitly
decoded as UTF-8 with a leading BOM stripped.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import kde_config
from support import snippet_child
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
        # to the containment reader instead. utf-8-sig is utf-8 plus BOM
        # stripping.
        path = make_tmp_dir(self) / "theme.ini"
        path.write_text("[Desktop Entry]\nName=Caf\u00e9\n", encoding="utf-8")
        reader = kde_config.containment.read_text
        with mock.patch.object(
            kde_config.containment, "read_text", wraps=reader
        ) as spy:
            parser = kde_config.read(path)
        self.assertEqual(spy.call_args.kwargs.get("encoding"), "utf-8-sig")
        self.assertEqual(parser.get("Desktop Entry", "Name"), "Caf\u00e9")

    def test_strips_a_leading_utf8_bom(self):
        # Qt's reader strips a UTF-8 BOM before parsing, so a theme file an
        # editor saved with a BOM still loads in Plasma. Decoded as plain
        # utf-8 the BOM stays in the first line, so configparser finds no
        # section header and raises MissingSectionHeaderError; the reader must
        # strip it.
        path = make_tmp_dir(self) / "theme.ini"
        path.write_bytes(b"\xef\xbb\xbf[General]\nColorScheme=MacOS8\n")
        parser = kde_config.read(path)
        self.assertEqual(parser.get("General", "ColorScheme"), "MacOS8")

    def test_reads_a_mid_file_indented_section_header(self):
        # KDE trims each line before parsing it, so an indented `[General]`
        # after another section's key still opens `[General]`. configparser
        # reads the indented line as a continuation of the previous value, so
        # without the reader's per-line lstrip the `[General]` heading and its
        # key are folded into `[Other]` and the live selection is missed.
        parser = self._read(
            "[Other]\nName=x\n  [General]\nColorScheme=MacOS8\n"
        )
        self.assertEqual(parser.get("General", "ColorScheme"), "MacOS8")
        self.assertEqual(parser.get("Other", "Name"), "x")
        self.assertNotIn("[General]", parser.get("Other", "Name"))

    def test_reads_an_indented_key_after_another_key(self):
        # The same trim makes an indented key a key, not a continuation of the
        # value above it. Without the reader's lstrip, `ColorScheme` is folded
        # into `Name` and the reader reports no ColorScheme at all.
        parser = self._read("[General]\nName=x\n  ColorScheme=MacOS8\n")
        self.assertEqual(parser.get("General", "ColorScheme"), "MacOS8")
        self.assertEqual(parser.get("General", "Name"), "x")

    def test_a_semicolon_prefix_is_not_a_comment(self):
        # KConfig treats only a leading '#' as a comment. A line beginning
        # with ';' is a key whose name includes the ';', so the reader must
        # keep it (configparser's default comment_prefixes would drop it) and
        # it must not become the `ColorScheme` selection.
        parser = self._read(
            "[General]\n;ColorScheme=BreezeLight\nColorScheme=MacOS8\n"
        )
        self.assertEqual(parser.get("General", ";ColorScheme"), "BreezeLight")
        self.assertEqual(parser.get("General", "ColorScheme"), "MacOS8")

    def test_a_key_before_the_first_heading_is_the_root_group(self):
        # KConfig files a key before any group header in its <default> root
        # group (`kreadconfig6 --group '<default>'`), not as an invalid entry;
        # the reader must keep it rather than drop it.
        parser = self._read(
            "ColorScheme=BreezeLight\n[General]\nColorScheme=MacOS8\n"
        )
        self.assertEqual(parser.get("<default>", "ColorScheme"), "BreezeLight")
        self.assertEqual(parser.get("General", "ColorScheme"), "MacOS8")

    def test_an_empty_group_header_does_not_join_the_previous_group(self):
        # KConfig accepts `[]` as a header for an empty-named group; a key
        # after it belongs there, not to [General]. configparser has no empty
        # section name, so the reader must not hand it the `[]` line (which
        # would raise) nor leave the following key in the open group.
        parser = self._read(
            "[General]\nColorScheme=BreezeLight\n[]\nColorScheme=MacOS8\n"
        )
        self.assertEqual(parser.get("General", "ColorScheme"), "BreezeLight")

    def test_refuses_a_fifo_instead_of_blocking(self):
        # `contents/defaults` and every theme INI are read through this helper;
        # a FIFO at one of those paths would block open() forever. The read
        # must refuse it by name. Run in a child so the pre-fix hang is a
        # bounded timeout, not a stalled suite.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        path = make_tmp_dir(self) / "defaults"
        os.mkfifo(path)
        child = snippet_child.run(
            [
                "from pathlib import Path; import sys; "
                "from support.kde_config import read; read(Path(sys.argv[1]))",
                str(path),
            ],
            cwd=Path(__file__).resolve().parent,
            timeout=10,
        )
        self.assertNotEqual(0, child.returncode, child.stdout + child.stderr)
        self.assertIn("not a regular file", child.stderr)
        self.assertIn(str(path), child.stderr)


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
