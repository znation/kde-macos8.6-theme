"""Validate the vendored Lato body font and its install lifecycle.

This is part 1/3 of the UI-font series: the package ships Lato Regular and
Bold, the SIL OFL 1.1 licence and a provenance record. It installs the family
under ``$XDG_DATA_HOME/fonts/org.macos8.desktop``; the global theme's
defaults select the family. Lato substitutes for Charcoal; it is not sampled from a
reference screenshot.
"""

from __future__ import annotations

import hashlib
import os
import struct
import unittest

from support import containment
from support.install_lifecycle_cases import InstallLifecycleCases
from support.installed_paths import (
    installed_font_package,
    installed_fonts_dir,
)
from support.process_assertions import assert_succeeded
from support.repo_root import ROOT
from support.theme_install import (
    installed_destdir,
    uninstall,
)

FONT_ID = "org.macos8.desktop"
PACKAGE_DIR = os.path.join(ROOT, "theme", "fonts", FONT_ID)
REGULAR = os.path.join(PACKAGE_DIR, "Lato-Regular.ttf")
BOLD = os.path.join(PACKAGE_DIR, "Lato-Bold.ttf")
LICENSE = os.path.join(PACKAGE_DIR, "LICENSE-Lato.txt")
PROVENANCE = os.path.join(PACKAGE_DIR, "PROVENANCE.md")

INSTALLED_FILES = (
    "Lato-Regular.ttf",
    "Lato-Bold.ttf",
    "LICENSE-Lato.txt",
    "PROVENANCE.md",
)

# The byte-for-byte source files these copies came from. Pinning both the font
# and the licence digest makes a changed byte, a renamed family or an appended
# newline fail before the name-table or licence checks run.
DIGESTS = {
    REGULAR: "6f6940be0835c3ddec9199e5fc42be4cbc61ebcfd58c623fdf719366253f1780",
    BOLD: "bf1b8130069b44b9148eeece35e5423bedac49777ba746615b826b8276574a7b",
    LICENSE: "1e6ccc54aa0b0aa4188cda121174f17cf1c28bac9734749bbe1128bb6dd89a97",
}

# Name IDs 1 and 2 of the sfnt `name` table.
FAMILY_NAME_ID = 1
SUBFAMILY_NAME_ID = 2


def _utf16be(raw):
    return raw.decode("utf-16-be")


def _mac_roman(raw):
    return raw.decode("mac_roman")


def _name_table(path):
    """Return the sfnt ``name`` table's {name ID: [decoded values]}.

    The two faces are TrueType ``sfnt`` files, so the table directory at offset
    12 names each table's offset and length. Only the platform records whose
    text is unambiguous are kept: Windows records are UTF-16BE and Macintosh
    records are Mac Roman. A record is decoded and collected, not compared to a
    hardcoded offset, so the helper reads whatever the shipped file contains.
    """
    data = containment.read_bytes(path, ROOT)
    if len(data) < 12:
        raise ValueError(f"{path}: too short for an sfnt header")
    table_count = struct.unpack(">H", data[4:6])[0]
    name = None
    for index in range(table_count):
        record = 12 + 16 * index
        if record + 16 > len(data):
            raise ValueError(f"{path}: truncated table directory")
        tag = data[record:record + 4]
        offset, length = struct.unpack(">II", data[record + 8:record + 16])
        if tag == b"name":
            name = (offset, length)
            break
    if name is None:
        raise ValueError(f"{path}: no sfnt name table")

    offset, length = name
    if offset + length > len(data) or length < 6:
        raise ValueError(f"{path}: truncated name table")
    _, count, string_offset = struct.unpack(
        ">HHH", data[offset:offset + 6]
    )
    names = {}
    for index in range(count):
        record = offset + 6 + 12 * index
        if record + 12 > offset + length:
            raise ValueError(f"{path}: truncated name records")
        platform, _, _, name_id, size, string = struct.unpack(
            ">HHHHHH", data[record:record + 12]
        )
        start = offset + string_offset + string
        raw = data[start:start + size]
        if len(raw) != size:
            raise ValueError(f"{path}: truncated name string")
        if platform == 3:
            text = _utf16be(raw)
        elif platform == 1:
            text = _mac_roman(raw)
        else:
            continue
        names.setdefault(name_id, []).append(text)
    return names


class TestFontFiles(unittest.TestCase):
    def test_fonts_name_the_lato_family_and_subfamily(self):
        for path, subfamily in ((REGULAR, "Regular"), (BOLD, "Bold")):
            with self.subTest(font=os.path.basename(path)):
                names = _name_table(path)
                # A face whose family or subfamily record is absent (or only on
                # a platform this helper does not decode) must fail here by
                # name; `names[...]` would raise a bare `KeyError: 1` that
                # names neither the font nor the missing record.
                self.assertEqual(
                    set(names.get(FAMILY_NAME_ID, ())), {"Lato"}, path
                )
                self.assertEqual(
                    set(names.get(SUBFAMILY_NAME_ID, ())), {subfamily}, path
                )

    def test_files_and_provenance_pin_the_same_digests(self):
        provenance = containment.read_text(PROVENANCE, ROOT)
        for path, digest in DIGESTS.items():
            with self.subTest(file=os.path.basename(path)):
                actual = hashlib.sha256(
                    containment.read_bytes(path, ROOT)
                ).hexdigest()
                self.assertEqual(actual, digest, path)
                self.assertIn(digest, provenance, PROVENANCE)

    def test_licence_is_the_source_file_without_a_trailing_newline(self):
        data = containment.read_bytes(LICENSE, ROOT)
        self.assertNotEqual(data[-1:], b"\n", LICENSE)
        text = data.decode("utf-8")
        self.assertIn("License: OFL-1.1", text)
        self.assertIn("(c) 2010-2011, Łukasz Dziedzic", text)
        self.assertIn("PERMISSION & CONDITIONS", text)


class TestFontsInstall(InstallLifecycleCases, unittest.TestCase):
    PACKAGE_ID = FONT_ID
    MAKE_PACKAGES = "fonts"
    PACKAGE_DIR = PACKAGE_DIR
    INSTALLED_FILES = INSTALLED_FILES

    def installed_parent(self, tmp):
        """Return the directory holding the installed font packages."""
        return installed_fonts_dir(tmp)

    def installed_package_dir(self, tmp):
        """Return the installed font package's own directory."""
        return installed_font_package(tmp, self.PACKAGE_ID)

    def test_uninstall_leaves_a_sibling_font_family(self):
        with installed_destdir(self, packages=self.MAKE_PACKAGES) as tmp:
            sibling = os.path.join(installed_fonts_dir(tmp), "other-family")
            os.makedirs(sibling)
            marker = os.path.join(sibling, "Other.ttf")
            with open(marker, "wb") as handle:
                handle.write(b"not our package")

            removed = uninstall(tmp)
            assert_succeeded(self, removed)
            self.assertFalse(
                os.path.exists(self.installed_package_dir(tmp)),
                self.installed_package_dir(tmp),
            )
            self.assertTrue(os.path.isdir(sibling), sibling)
            self.assertTrue(os.path.isfile(marker), marker)


if __name__ == "__main__":
    unittest.main()
