"""Drive ``tests/placeholders.py``'s marker and register cross-check.

A placeholder asset carries the literal token ``PLACEHOLDER:`` in a comment in
its own file format, and the register ``PLACEHOLDERS.md`` holds one table row
per asset. ``tests/placeholders.py`` reads the markers under ``theme/`` and the
register rows and cross-checks the two sets; this module drives those checks,
first against a synthetic theme root (``TestHelpers``) and then against the
shipped register (``TestRepositoryRegister``), so a new placeholder added
without a row (or a stale row whose file is gone or unmarked) fails
``make check``.
"""

from __future__ import annotations

import os
import unittest

from placeholders import (
    REGISTER,
    TOKEN,
    cross_check,
    markers,
    register_entries,
)
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir


class TestHelpers(unittest.TestCase):
    """Pin the marker/register readers on a synthetic theme root."""

    def _write_marker(self, root, rel, text):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">\n'
            f"  <!-- {TOKEN} {text} -->\n"
            "</svg>\n",
            encoding="utf-8",
        )

    def _write_register(self, root, entries):
        rows = "".join(
            f"| `{asset}` | {text} |\n" for asset, text in entries.items()
        )
        register = root / "PLACEHOLDERS.md"
        register.write_text(
            "# Placeholders\n\n"
            "| Placeholder | Stands in for |\n"
            "| --- | --- |\n"
            f"{rows}",
            encoding="utf-8",
        )
        return str(register)

    def test_markers_finds_a_marker_in_a_temp_theme_root(self):
        tmp = make_tmp_dir(self)
        self._write_marker(tmp, os.path.join("theme", "places", "folder.svg"), "a folder icon")
        self.assertEqual(
            markers(tmp), {os.path.join("theme", "places", "folder.svg"): "a folder icon"}
        )

    def test_markers_omits_text_without_the_token(self):
        tmp = make_tmp_dir(self)
        path = tmp / "theme" / "index.theme"
        path.parent.mkdir(parents=True)
        path.write_text("[Icon Theme]\nName=x\n", encoding="utf-8")
        self.assertEqual(markers(tmp), {})

    def test_markers_finds_markers_in_every_text_format_the_theme_ships(self):
        # The shipped theme carries a JavaScript layout (`.js`), an Aurorae
        # decoration config (`.desktoprc`) and a Kvantum widget style
        # (`.kvconfig`), alongside its SVG, QML, palette, theme, desktop and
        # JSON files and its `index.theme` and extensionless `defaults`; a
        # placeholder in any of them must be tracked, so each is a text asset.
        tmp = make_tmp_dir(self)
        cases = {
            os.path.join("art", "thing.svg"): "<!-- {token} stands in -->",
            os.path.join("art", "thing.qml"): "// {token} stands in",
            os.path.join("schemes", "thing.colors"): "# {token} stands in",
            os.path.join("art", "thing.theme"): "# {token} stands in",
            os.path.join("aurorae", "theme.desktop"): "# {token} stands in",
            os.path.join("aurorae", "theme.desktoprc"): "# {token} stands in",
            os.path.join("meta", "thing.json"): '{{"note": "{token} stands in"}}',
            os.path.join("layouts", "layout.js"): "// {token} stands in",
            os.path.join("kvantum", "style.kvconfig"): "# {token} stands in",
            os.path.join("icons", "index.theme"): "# {token} stands in",
            os.path.join("look-and-feel", "defaults"): "# {token} stands in",
        }
        expected = {}
        for rel, template in cases.items():
            path = tmp / "theme" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(template.format(token=TOKEN) + "\n", encoding="utf-8")
            # An SVG's marker drops its comment terminator; a JSON marker keeps
            # the closing quote of the string it lives in.
            expected[os.path.join("theme", rel)] = (
                'stands in"}' if rel.endswith(".json") else "stands in"
            )
        self.assertEqual(markers(tmp), expected)

    def test_markers_rejects_a_non_utf8_asset(self):
        # A text asset committed with a stray byte (a binary file under an SVG
        # name, an editor writing Latin-1) is not valid UTF-8. Decoding it must
        # fail as the checker's own AssertionError naming the asset, not escape
        # as a codec UnicodeDecodeError that names neither the checker nor it.
        tmp = make_tmp_dir(self)
        path = tmp / "theme" / "a.svg"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"\xff\xfe<svg/>\n")
        with self.assertRaisesRegex(AssertionError, "not valid UTF-8"):
            markers(tmp)

    def test_markers_rejects_a_symlink_out_of_the_theme_root(self):
        # theme/ is contributor-supplied, so a checked-in symlink can point
        # anywhere on the machine. Reading through it would pull a private
        # file's lines into the marker map (and, when the token appears there,
        # into a failing assertion's diagnostic), so the read must stay inside
        # theme/.
        tmp = make_tmp_dir(self)
        outside = tmp / "outside.txt"
        outside.write_text(f"{TOKEN} a private file\n", encoding="utf-8")
        path = tmp / "theme" / "link.svg"
        path.parent.mkdir(parents=True)
        path.symlink_to(outside)
        with self.assertRaisesRegex(AssertionError, "symlink escape"):
            markers(tmp)

    def test_markers_rejects_a_dangling_symlink_within_the_theme_root(self):
        # A symlink whose target lies inside theme/ passes the escape guard,
        # but a target that does not exist makes open() raise
        # FileNotFoundError. The checker must report the unreadable asset as
        # its own AssertionError naming the path, not abort the run with a bare
        # OSError traceback.
        tmp = make_tmp_dir(self)
        path = tmp / "theme" / "link.svg"
        path.parent.mkdir(parents=True)
        path.symlink_to(tmp / "theme" / "missing.svg")
        with self.assertRaisesRegex(AssertionError, "cannot be read"):
            markers(tmp)

    def test_register_entries_parses_the_table(self):
        tmp = make_tmp_dir(self)
        register = self._write_register(tmp, {os.path.join("theme", "a.svg"): "an a"})
        self.assertEqual(register_entries(register), {os.path.join("theme", "a.svg"): "an a"})

    def test_register_entries_rejects_a_non_utf8_register(self):
        tmp = make_tmp_dir(self)
        asset = os.path.join("theme", "a.svg")
        register = tmp / "PLACEHOLDERS.md"
        register.write_bytes(f"| `{asset}` | an a |\n".encode("utf-8") + b"\xff")
        with self.assertRaisesRegex(AssertionError, "not valid UTF-8"):
            register_entries(str(register))

    def test_register_entries_rejects_an_unreadable_register(self):
        # PLACEHOLDERS.md is read with open(); a missing or unreadable register
        # makes that raise OSError, which names neither the checker nor the
        # register's role. The checker must report it as its own AssertionError
        # instead, matching `_marker_text`'s handling of an unreadable asset.
        tmp = make_tmp_dir(self)
        with self.assertRaisesRegex(AssertionError, "cannot be read"):
            register_entries(str(tmp / "PLACEHOLDERS.md"))

    def test_cross_check_accepts_a_matching_register(self):
        tmp = make_tmp_dir(self)
        self._write_marker(tmp, os.path.join("theme", "a.svg"), "an a")
        register = self._write_register(tmp, {os.path.join("theme", "a.svg"): "an a"})
        found, entries = cross_check(tmp, register)
        self.assertEqual(found, entries)

    def test_cross_check_rejects_a_marker_missing_from_the_register(self):
        tmp = make_tmp_dir(self)
        self._write_marker(tmp, os.path.join("theme", "a.svg"), "an a")
        register = self._write_register(tmp, {})
        with self.assertRaisesRegex(AssertionError, "has no row"):
            cross_check(tmp, register)

    def test_cross_check_rejects_a_register_path_with_no_marker(self):
        tmp = make_tmp_dir(self)
        self._write_marker(tmp, os.path.join("theme", "a.svg"), "an a")
        unmarked = tmp / "theme" / "b.svg"
        unmarked.write_text("<svg/>\n", encoding="utf-8")
        register = self._write_register(
            tmp, {os.path.join("theme", "a.svg"): "an a", os.path.join("theme", "b.svg"): "a b"}
        )
        with self.assertRaisesRegex(AssertionError, "carries no"):
            cross_check(tmp, register)

    def test_cross_check_rejects_a_register_path_that_is_gone(self):
        tmp = make_tmp_dir(self)
        register = self._write_register(tmp, {os.path.join("theme", "a.svg"): "an a"})
        with self.assertRaisesRegex(AssertionError, "does not exist"):
            cross_check(tmp, register)


class TestRepositoryRegister(unittest.TestCase):
    """Cross-check the shipped theme against its register."""

    def test_register_and_markers_name_the_same_assets(self):
        # The register may be empty: the icon theme's art is now final, so
        # `found` and `entries` are both empty. The cross-check still
        # fails if a new placeholder appears without a row (or vice versa).
        found, entries = cross_check(ROOT, REGISTER)
        self.assertEqual(set(found), set(entries))

    def test_marker_text_matches_the_register_description(self):
        found, entries = cross_check(ROOT, REGISTER)
        for asset, text in found.items():
            with self.subTest(asset=asset):
                self.assertEqual(text, entries[asset])


if __name__ == "__main__":
    unittest.main()
