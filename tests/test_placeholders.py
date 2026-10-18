"""Keep PLACEHOLDERS.md and the shipped theme's placeholder markers in step.

The user answered 2026-10-18 that the theme's own artwork was to ship as
placeholders for now and that every one must be tracked "so we don't forget to
replace them all eventually". A placeholder asset carries the literal token
``PLACEHOLDER:`` in a comment in its own file format, naming what it stands in
for; the register ``PLACEHOLDERS.md`` holds one table row per asset.
:func:`markers` reads the markers under ``theme/`` and :func:`register_entries`
reads the register, and the tests cross-check the two sets so a new placeholder
added without a row (or a stale row whose file is gone or unmarked) fails
``make check``.
"""

from __future__ import annotations

import os
import re
import unittest

from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir

TOKEN = "PLACEHOLDER:"
REGISTER = os.path.join(ROOT, "PLACEHOLDERS.md")
THEME_DIR = "theme"
# The text formats a placeholder asset can use. Binary assets (the ``.png``
# wallpapers, the gzipped ``.svgz`` decoration) cannot carry a comment marker.
TEXT_EXTENSIONS = (
    ".svg",
    ".qml",
    ".colors",
    ".theme",
    ".desktop",
    ".desktoprc",
    ".json",
    ".js",
    ".kvconfig",
)
TEXT_NAMES = ("index.theme", "defaults")

# One register table row: ``| `path` | what it stands in for |``.
ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*$")


def _is_text_asset(filename):
    """Return True when *filename* is a text format that can hold a marker."""
    return filename in TEXT_NAMES or filename.endswith(TEXT_EXTENSIONS)


def _marker_text(path):
    """Return the text after the ``PLACEHOLDER:`` token in *path*, or None.

    The marker is the token plus what it stands in for, in a comment in the
    file's own format; a trailing SVG comment terminator (``-->``) is dropped
    so the returned text is the description alone.
    """
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            index = line.find(TOKEN)
            if index == -1:
                continue
            text = line[index + len(TOKEN):].strip()
            if text.endswith("-->"):
                text = text[:-3].strip()
            return text
    return None


def markers(root):
    """Return ``{relative path: marker text}`` for the placeholders under *root*.

    Walks ``<root>/theme`` for text assets and returns one entry per file that
    carries the ``PLACEHOLDER:`` token; a file without the token is not a
    placeholder and is omitted. ``PLACEHOLDERS.md`` is skipped so the register
    itself is never mistaken for a placeholder asset.
    """
    found = {}
    for dirpath, _, filenames in os.walk(os.path.join(root, THEME_DIR)):
        for filename in filenames:
            if filename == "PLACEHOLDERS.md" or not _is_text_asset(filename):
                continue
            path = os.path.join(dirpath, filename)
            text = _marker_text(path)
            if text is not None:
                found[os.path.relpath(path, root)] = text
    return found


def register_entries(path):
    """Return ``{asset path: what it stands in for}`` from the register table."""
    entries = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            match = ROW.match(line)
            if match:
                entries[match.group(1)] = match.group(2)
    return entries


def cross_check(root, register):
    """Assert *register* and the markers under *root* name the same assets.

    Returns ``(markers, entries)`` so a caller can assert more; raises
    :class:`AssertionError` naming the first disagreement: a marked file with
    no row, a row whose path is missing, or a row whose file carries no marker.
    """
    found = markers(root)
    entries = register_entries(register)
    for asset in sorted(found):
        if asset not in entries:
            raise AssertionError(
                f"{asset} carries a {TOKEN} marker but has no row in {register}"
            )
    for asset in sorted(entries):
        if not os.path.isfile(os.path.join(root, asset)):
            raise AssertionError(f"{register} lists {asset}, which does not exist")
        if asset not in found:
            raise AssertionError(
                f"{register} lists {asset}, which carries no {TOKEN} marker"
            )
    return found, entries


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

    def test_register_entries_parses_the_table(self):
        tmp = make_tmp_dir(self)
        register = self._write_register(tmp, {os.path.join("theme", "a.svg"): "an a"})
        self.assertEqual(register_entries(register), {os.path.join("theme", "a.svg"): "an a"})

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
        # The register may be empty: the icon theme's five icons are now final
        # art, so `found` and `entries` are both empty. The cross-check still
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
