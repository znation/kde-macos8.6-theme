"""Tests for the global defaults reader and its config writer."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fifo_fixtures import assert_read_refused_in_child
from support.symlink_fixtures import symlinked_repo
from support.tmp_dir import make_tmp_dir
from tools import theme_defaults  # noqa: E402


class TestDefaultsGroups(unittest.TestCase):
    def test_reads_the_decoration_and_desktop_theme_from_the_global_theme(self):
        groups = theme_defaults.defaults_groups()
        decoration = groups[("kwinrc", "org.kde.kdecoration2")]
        self.assertEqual("org.macos8.desktop", decoration["theme"])
        self.assertEqual("org.macos8.desktop", groups[("plasmarc", "Theme")]["name"])

    def test_skips_sections_that_name_no_config_file(self):
        groups = theme_defaults.defaults_groups()
        self.assertNotIn("Wallpaper", {group for _, group in groups})

    def test_merges_a_repeated_file_group_heading(self):
        # A contributor can extend an existing section by repeating its
        # heading rather than moving the new keys into the first occurrence.
        # The second heading must continue the same group instead of starting
        # an empty one, or the keys unique to the first occurrence vanish from
        # the config the theme writes.
        # A key repeated within the continued section keeps its later value,
        # the ordinary within-section assignment semantics.
        path = make_tmp_dir(self) / "defaults"
        path.write_text(
            "[kwinrc][Theme]\nfirst=1\n[kwinrc][Theme]\nsecond=2\nfirst=3\n",
            encoding="utf-8",
        )
        self.assertEqual(
            {("kwinrc", "Theme"): {"first": "3", "second": "2"}},
            theme_defaults.defaults_groups(path),
        )

    def test_a_repeated_key_keeps_the_later_value(self):
        # The docstring promises the later value wins, whether the repeat
        # sits in the same occurrence of a heading or in a second one. A
        # key line before any heading belongs to no group and is dropped
        # rather than attached to the first heading that follows.
        path = make_tmp_dir(self) / "defaults"
        path.write_text(
            "orphan=0\n[a][B]\nk=1\nk=2\n[a][B]\nk=3\nother=4\n",
            encoding="utf-8",
        )
        self.assertEqual(
            {("a", "B"): {"k": "3", "other": "4"}},
            theme_defaults.defaults_groups(path),
        )

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

    def test_recognizes_an_indented_section_heading(self):
        # KDE trims each line before parsing it, so a `[file][group]` heading
        # with leading whitespace still opens its section -- the same
        # trim-before-parse invariant the `make uninstall` warning was fixed
        # to honour. Without the reader's `line = raw.strip()`, an indented
        # heading starts with whitespace, so it matches neither heading
        # pattern and its keys are silently dropped from the written config.
        path = make_tmp_dir(self) / "defaults"
        path.write_text(
            "  [kwinrc][org.kde.kdecoration2]\ntheme=x\n"
            "[plasmarc][Theme]\nname=y\n"
            "  [plasmarc][KDE]\nwidgetStyle=kvantum\n",
            encoding="utf-8",
        )
        self.assertEqual(
            {
                ("kwinrc", "org.kde.kdecoration2"): {"theme": "x"},
                ("plasmarc", "Theme"): {"name": "y"},
                ("plasmarc", "KDE"): {"widgetStyle": "kvantum"},
            },
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

    def test_a_unicode_line_separator_stays_inside_the_value(self):
        # Only CR, LF and CRLF end a line in this INI-shaped file; the rest of
        # a value is data. ``str.splitlines`` also breaks on U+2028, so a
        # filter or label containing one would be cut in two: the remainder
        # is dropped (it has no ``=``), writing a config with a truncated
        # value and no diagnostic.
        path = make_tmp_dir(self) / "defaults"
        path.write_text(
            "[kwinrc][Theme]\nname=Mac OS 8.6\u2028Platinum\n",
            encoding="utf-8",
        )
        self.assertEqual(
            {("kwinrc", "Theme"): {"name": "Mac OS 8.6\u2028Platinum"}},
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

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        # ``contents/defaults`` is contributor-supplied, and a checked-in
        # symlink can point at a private file. The reader echoes an offending
        # line in its ValueError, so following such a symlink would leak that
        # file's content into the diagnostic. A path that resolves outside the
        # repository must be refused before it is opened.
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp,
                "defaults",
                "[kwinrc][org.kde.kdecoration2]\ntheme=leaked\n",
            )
            with mock.patch.object(theme_defaults, "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    theme_defaults.defaults_groups(link)
        self.assertIn("symlink escape", str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp,
                "link",
                "[kwinrc][org.kde.kdecoration2]\ntheme=x\n",
                target="theme/defaults",
            )
            with mock.patch.object(theme_defaults, "ROOT", root):
                groups = theme_defaults.defaults_groups(link)
        self.assertEqual(
            {"theme": "x"}, groups[("kwinrc", "org.kde.kdecoration2")]
        )

    def test_rejects_a_heading_with_no_closing_bracket(self):
        # A heading whose closing bracket is missing (``[kwinrc``) matches
        # neither heading pattern. Before the guard widened to every line
        # that opens a bracket, such a line fell through as a bare line: its
        # keys were attached to the previous section and the intended section
        # silently vanished from the written config. It must be rejected by
        # name instead.
        path = make_tmp_dir(self) / "defaults"
        path.write_text(
            "[plasmarc][Theme]\nname=y\n[kwinrc\ntheme=x\n",
            encoding="utf-8",
        )
        with self.assertRaises(ValueError) as caught:
            theme_defaults.defaults_groups(path)
        self.assertIn("malformed section heading", str(caught.exception))
        self.assertIn("[kwinrc", str(caught.exception))

    def test_rejects_a_heading_with_whitespace_inside_a_bracket_pair(self):
        # A padded name (``[kwinrc ][Theme]``) matches the ``[file][group]``
        # pattern, but its file is the distinct string ``'kwinrc '``. The
        # written config filters sections by exact file name, so the padded
        # section would be dropped from ``kwinrc`` with no diagnostic -- the
        # silent loss this reader's malformed-heading guard exists to prevent.
        # It must be rejected by name instead.
        for heading in ("[kwinrc ][Theme]", "[kwinrc][Theme ]"):
            with self.subTest(heading=heading):
                path = make_tmp_dir(self) / "defaults"
                path.write_text(
                    f"{heading}\ntheme=x\n",
                    encoding="utf-8",
                )
                with self.assertRaises(ValueError) as caught:
                    theme_defaults.defaults_groups(path)
                self.assertIn("malformed section heading", str(caught.exception))
                self.assertIn(heading, str(caught.exception))

    def test_rejects_a_defaults_file_larger_than_the_limit(self):
        # ``contents/defaults`` is contributor-supplied. A multi-gigabyte file
        # (a checked-in blob, or an LFS smudge gone wrong) read whole would
        # allocate it and raise MemoryError, which the render's handler
        # (OSError/UnicodeDecodeError/ValueError) does not catch, so the run
        # would abort with a traceback instead of a diagnostic. The reader
        # bounds the read and names the limit.
        path = make_tmp_dir(self) / "defaults"
        path.write_bytes(b"x" * (theme_defaults._MAX_DEFAULTS_BYTES + 1))
        with self.assertRaises(ValueError) as caught:
            theme_defaults.defaults_groups(path)
        self.assertIn("byte limit", str(caught.exception))
        self.assertIn(
            str(theme_defaults._MAX_DEFAULTS_BYTES), str(caught.exception)
        )

    def test_a_defaults_file_exactly_at_the_cap_is_parsed_not_refused(self):
        # The cap is inclusive: a defaults file of exactly
        # _MAX_DEFAULTS_BYTES bytes is a valid file, not an oversize one.
        # Nothing pinned the accepted side, so a `>=` in the shared reader's
        # cap check (tools/config_read.py) would have turned every legal
        # at-cap file into the oversize refusal with no failing test.
        path = make_tmp_dir(self) / "defaults"
        heading = "[kwinrc][Theme]\n"
        filler = b"k=0\n" * (
            (theme_defaults._MAX_DEFAULTS_BYTES - len(heading.encode())) // 4
        )
        path.write_bytes(heading.encode() + filler)
        self.assertEqual(theme_defaults._MAX_DEFAULTS_BYTES, path.stat().st_size)
        self.assertEqual(
            {("kwinrc", "Theme"): {"k": "0"}},
            theme_defaults.defaults_groups(path),
        )

    def test_rejects_a_defaults_file_that_is_not_valid_utf8(self):
        # A contributor-supplied defaults file that is not valid UTF-8 would
        # otherwise raise UnicodeDecodeError, which the render's handler does
        # catch but with a low-level message. The reader names the file and
        # the decode failure instead.
        path = make_tmp_dir(self) / "defaults"
        path.write_bytes(b"\xff\xfe[kwinrc][org.kde.kdecoration2]\ntheme=x\n")
        with self.assertRaises(ValueError) as caught:
            theme_defaults.defaults_groups(path)
        self.assertIn("not valid UTF-8", str(caught.exception))
        self.assertIn(str(path), str(caught.exception))

    def test_refuses_a_fifo_instead_of_blocking(self):
        # contents/defaults is opened before the size cap is applied, and a
        # FIFO with no writer blocks open() forever; the render has no timeout
        # around this read, so one stray pipe would stall it silently. Refuse
        # the path by name in a child process instead.
        path = make_tmp_dir(self) / "defaults"
        assert_read_refused_in_child(
            self,
            path,
            "from pathlib import Path; import sys; "
            "from tools.theme_defaults import defaults_groups; "
            "defaults_groups(Path(sys.argv[1]))",
            str(path),
            cwd=repo_root.ROOT,
        )


class TestWriteConfigs(unittest.TestCase):
    def test_rejects_non_path_config_home(self):
        with self.assertRaises(ValueError):
            theme_defaults.write_configs("/tmp", ("kwinrc",))

    def test_rejects_a_single_string_instead_of_a_sequence(self):
        directory = make_tmp_dir(self)
        with self.assertRaises(ValueError) as raised:
            theme_defaults.write_configs(directory, "kwinrc")
        self.assertIn("sequence", str(raised.exception))
        self.assertEqual(set(), set(os.listdir(directory)))

    def test_rejects_non_iterable_names_with_a_clear_error(self):
        directory = make_tmp_dir(self)
        with self.assertRaises(ValueError) as raised:
            theme_defaults.write_configs(directory, 42)
        self.assertIn("iterable of config filenames", str(raised.exception))
        self.assertIn("int", str(raised.exception))
        self.assertEqual(set(), set(os.listdir(directory)))

    def test_rejects_names_that_escape_the_config_home(self):
        base = make_tmp_dir(self)
        directory = base / "config"
        directory.mkdir()
        for name in ("../escape", "/escape", "sub/kwinrc", "..", ""):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    theme_defaults.write_configs(directory, ("kwinrc", name))
                self.assertEqual(set(), set(os.listdir(directory)))
        self.assertFalse((base / "escape").exists())

    def test_rejects_a_non_str_name(self):
        directory = make_tmp_dir(self)
        with self.assertRaises(ValueError):
            theme_defaults.write_configs(directory, (b"kwinrc",))
        self.assertEqual(set(), set(os.listdir(directory)))

    def test_rejects_a_name_with_a_nul_byte(self):
        directory = make_tmp_dir(self)
        with self.assertRaises(ValueError):
            theme_defaults.write_configs(directory, ("kwinrc", "bad\0name"))
        self.assertEqual(set(), set(os.listdir(directory)))

    def test_accepts_an_empty_sequence_without_writing(self):
        directory = make_tmp_dir(self)
        theme_defaults.write_configs(directory, ())
        self.assertEqual(set(), set(os.listdir(directory)))

    def test_refuses_to_write_a_config_the_defaults_do_not_define(self):
        # A defaults file truncated after one section (or emptied by a failed
        # write) would otherwise make write_configs publish an empty file for
        # the missing name, silently dropping the theme settings the render
        # needs. Every name is checked before the first file is written, so a
        # missing section leaves the config home untouched.
        for label, text in (
            ("empty", ""),
            ("truncated", "[plasmarc][Theme]\nname=x\n"),
        ):
            self._assert_defaults_refused(text, label)

    def _assert_defaults_refused(self, text, label):
        """Pin a defaults file missing sections refused, config untouched."""
        with self.subTest(defaults=label):
            defaults = make_tmp_dir(self) / "defaults"
            defaults.write_text(text, encoding="utf-8")
            directory = make_tmp_dir(self)
            with mock.patch.object(theme_defaults, "DEFAULTS", defaults):
                with self.assertRaises(ValueError) as caught:
                    theme_defaults.write_configs(
                        directory, ("kwinrc", "plasmarc")
                    )
            self.assertIn("kwinrc", str(caught.exception))
            self.assertIn(str(defaults), str(caught.exception))
            self.assertEqual(set(), set(os.listdir(directory)))

    def test_written_configs_follow_the_defaults(self):
        directory = make_tmp_dir(self)
        theme_defaults.write_configs(directory, ("kwinrc", "plasmarc"))
        kwinrc = (directory / "kwinrc").read_text(encoding="utf-8")
        plasmarc = (directory / "plasmarc").read_text(encoding="utf-8")
        self.assertEqual({"kwinrc", "plasmarc"}, set(os.listdir(directory)))
        self.assertIn("[org.kde.kdecoration2]\n", kwinrc)
        self.assertIn("theme=org.macos8.desktop\n", kwinrc)
        self.assertIn("[Theme]\nname=org.macos8.desktop\n", plasmarc)
        self.assertNotIn("ColorScheme", kwinrc + plasmarc)


if __name__ == "__main__":
    unittest.main()
