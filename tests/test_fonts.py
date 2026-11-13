"""Validate the vendored fonts and their install lifecycle.

The package ships Lato Regular and Bold, the SIL OFL 1.1 licence and a
provenance record, the public-domain ChicagoFLF menu/title face, and the
JetBrains Mono static faces (Regular, Medium and Bold) the user approved for
fixed-width text, with the Debian copyright file as their licence record. It
installs the families under
``$XDG_DATA_HOME/fonts/org.macos8.desktop``; the global theme's defaults select
Lato and ChicagoFLF. Lato substitutes for Charcoal and JetBrains Mono for the
fixed-width role; neither is sampled from a reference screenshot.
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
CHICAGO = os.path.join(PACKAGE_DIR, "ChicagoFLF.ttf")
CHICAGO_README = os.path.join(PACKAGE_DIR, "README.ChicagoFLF")
JBM_REGULAR = os.path.join(PACKAGE_DIR, "JetBrainsMono-Regular.ttf")
JBM_MEDIUM = os.path.join(PACKAGE_DIR, "JetBrainsMono-Medium.ttf")
JBM_BOLD = os.path.join(PACKAGE_DIR, "JetBrainsMono-Bold.ttf")
JBM_LICENSE = os.path.join(PACKAGE_DIR, "LICENSE-JetBrainsMono.txt")
PROVENANCE = os.path.join(PACKAGE_DIR, "PROVENANCE.md")

INSTALLED_FILES = (
    "Lato-Regular.ttf",
    "Lato-Bold.ttf",
    "LICENSE-Lato.txt",
    "ChicagoFLF.ttf",
    "README.ChicagoFLF",
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Medium.ttf",
    "JetBrainsMono-Bold.ttf",
    "LICENSE-JetBrainsMono.txt",
    "PROVENANCE.md",
)

# The byte-for-byte source files these copies came from. Pinning both the font
# and the licence digest makes a changed byte, a renamed family or an appended
# newline fail before the name-table or licence checks run.
DIGESTS = {
    REGULAR: "6f6940be0835c3ddec9199e5fc42be4cbc61ebcfd58c623fdf719366253f1780",
    BOLD: "bf1b8130069b44b9148eeece35e5423bedac49777ba746615b826b8276574a7b",
    LICENSE: "1e6ccc54aa0b0aa4188cda121174f17cf1c28bac9734749bbe1128bb6dd89a97",
    CHICAGO: "b442111f37639e27572d9df0c5190e7480e6a7b01ec768aea47a154efab8d50d",
    CHICAGO_README: "60ca3e47853943cba1792103a1efbbb5b38797e6f249104b0e27b7fdc4943044",
    JBM_REGULAR: "9fd21a629ec73a93d1665b6d8bbb73928040a290b49d2f6772505b8129e68cdc",
    JBM_MEDIUM: "a3735d53e905b3898a23dedb2f118757be11858979e254865dc1b30ea63c0de6",
    JBM_BOLD: "10389fb114512e1df7ca54f791b9f83572e2785e9ff1946c8197d5e5faaafd7a",
    JBM_LICENSE: "af1f9fe50b20580bbe159f3e7f88b0a5a201c2f7f71a0eb61ba6b39b867d1c72",
}

# Name IDs 1 and 2 of the sfnt `name` table.
FAMILY_NAME_ID = 1
SUBFAMILY_NAME_ID = 2


def _utf16be(raw):
    """Decode *raw* as UTF-16-BE."""
    return raw.decode("utf-16-be")


def _mac_roman(raw):
    """Decode *raw* as Mac Roman."""
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


def _is_fixed_pitch(path):
    """Return the sfnt ``post`` table's ``isFixedPitch`` flag.

    The flag sits at offset 12 of the version-3 ``post`` header (version,
    italic angle, underline position and thickness come first). A zero means
    the font admits it is proportionally spaced.
    """
    data = containment.read_bytes(path, ROOT)
    table_count = struct.unpack(">H", data[4:6])[0]
    for index in range(table_count):
        record = 12 + 16 * index
        if record + 16 > len(data):
            raise ValueError(f"{path}: truncated table directory")
        tag = data[record:record + 4]
        offset, length = struct.unpack(">II", data[record + 8:record + 16])
        if tag == b"post":
            if offset + 16 > len(data) or length < 16:
                raise ValueError(f"{path}: truncated post table")
            flag, = struct.unpack(">I", data[offset + 12:offset + 16])
            return flag
    raise ValueError(f"{path}: no sfnt post table")


class TestFontFiles(unittest.TestCase):
    def test_chicago_face_names_its_family_and_public_domain_dedication(self):
        names = _name_table(CHICAGO)
        self.assertEqual(set(names.get(1, ())), {"ChicagoFLF"}, CHICAGO)
        self.assertEqual(set(names.get(2, ())), {"Regular"}, CHICAGO)
        self.assertIn("Public Domain", names.get(13, ()), CHICAGO)

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

    def test_jetbrains_mono_faces_name_their_family_and_subfamily(self):
        # Medium is exposed as its own family name per the OFL naming
        # convention for non-RIBBI weights, so its subfamily stays Regular.
        for path, family, subfamily in (
            (JBM_REGULAR, "JetBrains Mono", "Regular"),
            (JBM_MEDIUM, "JetBrains Mono Medium", "Regular"),
            (JBM_BOLD, "JetBrains Mono", "Bold"),
        ):
            with self.subTest(font=os.path.basename(path)):
                names = _name_table(path)
                self.assertEqual(
                    set(names.get(FAMILY_NAME_ID, ())), {family}, path
                )
                self.assertEqual(
                    set(names.get(SUBFAMILY_NAME_ID, ())), {subfamily}, path
                )

    def test_jetbrains_mono_faces_declare_the_ofl_licence_and_fixed_pitch(self):
        for path in (JBM_REGULAR, JBM_MEDIUM, JBM_BOLD):
            with self.subTest(font=os.path.basename(path)):
                names = _name_table(path)
                self.assertTrue(
                    any(
                        "SIL Open Font License, Version 1.1" in text
                        for text in names.get(13, ())
                    ),
                    path,
                )
                self.assertTrue(
                    any(
                        "https://scripts.sil.org/OFL" in text
                        for text in names.get(14, ())
                    ),
                    path,
                )
                self.assertEqual(_is_fixed_pitch(path), 1, path)

    def test_jetbrains_mono_licence_is_the_debian_copyright_file(self):
        text = containment.read_text(JBM_LICENSE, ROOT)
        self.assertIn(
            "Format: https://www.debian.org/doc/packaging-manuals/"
            "copyright-format/1.0/",
            text,
        )
        self.assertIn("Upstream-Name: JetBrains Mono", text)
        self.assertIn("philipp.nurullin@jetbrains.com", text)
        self.assertIn("Source: https://github.com/JetBrains/JetBrainsMono", text)
        self.assertIn("License: Apache-2", text)
        self.assertIn("License: GPL-3+", text)
        provenance = containment.read_text(PROVENANCE, ROOT)
        self.assertIn("SIL Open Font License 1.1", provenance)
        self.assertIn("dual-licensed", provenance)
        self.assertIn("2.304+ds-5", provenance)
        self.assertIn(
            "fonts-jetbrains-mono_2.304+ds-5_all.deb", provenance
        )


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
