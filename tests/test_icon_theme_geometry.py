"""Pin every shipped icon's drawing elements in document order.

The folder name and every folder alias share one drawing, so each alias must
stay the same art as the folder at every shipped size. The pinned tuples
themselves live in ``support.icon.shape_pins``, beside the inventory they
pin.
"""

import ast
import os
import unittest

from support.invariants import parsed_module
from support.repo_root import ROOT
from support.icon.theme_inventory import (
    BLANK_DOCUMENTS,
    FOLDER_ALIASES,
    PACKAGE,
    SHIPPED_ICONS,
    STANDARD_PLACES,
    USER_PLACES_ICONS,
)
from support.icon.shape_pins import ICON_SHAPES, SHAPE_PIN_FAMILIES
from support.svg_case import parse_svg
from svg_assertions import local_name


def _drawing_elements(tree):
    """Return each of *tree*'s root children as ``(tag, attributes)``.

    In document order, so an added, removed, reordered or re-drawn element
    changes the tuple; the icon art holds only drawing elements, with no
    groups or ids, so every root child is one.
    """
    return tuple(
        (local_name(element), dict(element.attrib))
        for element in tree.getroot()
    )


def _shipped_elements(size, family, name):
    """Return the shipped *family*/*name* icon's drawing elements at *size*.

    The one reader for the shipped files the sharing tests below compare;
    every call site passes the size directory, the family directory and
    the icon name without its ``.svg`` suffix.
    """
    return _drawing_elements(
        parse_svg(os.path.join(PACKAGE, size, family, name + ".svg"))
    )


def _generic_page(size):
    """Return the generic document's page prefix at *size*.

    The first three drawing elements of the shipped ``text-x-generic.svg``
    (the black outline, the white page and the folded corner) that the
    page-sharing tests below compare every page-backed document against.
    """
    return _shipped_elements(size, "mimetypes", "text-x-generic")[:3]


class TestIconGeometry(unittest.TestCase):
    """Pin every shipped icon's drawing elements, in document order."""

    def test_the_geometry_registry_covers_every_shipped_icon(self):
        # The per-icon pins below only visit the icons listed in ICON_SHAPES,
        # so a newly shipped icon that is never added there would silently
        # escape them. Derive the shipped set from the same list TestIndex
        # checks and require the registry to equal it.
        self.assertEqual(set(ICON_SHAPES), set(SHIPPED_ICONS))

    def test_each_family_registry_names_its_files_once_in_its_family(self):
        # Each family registry is a dict literal, and a dict literal that
        # names the same file twice is legal Python that silently keeps the
        # last pin. Every consumer deduplicates -- the coverage test above
        # compares sets and the pin comparison reads the built registry --
        # so a duplicated entry (the classic merge slip when two icon plans
        # append to the same family module on the same day) would leave the
        # discarded pin's elements drifting unobserved. Re-derive each
        # literal key's path in every family module and require the paths
        # to be distinct, and each key to name its own family's directory
        # so a pin filed under the wrong family cannot hide between them.
        # The package __init__ merges the families into ICON_SHAPES, and a
        # literal key appended there reaches the built registry just the
        # same, so visit the merge's literal keys too; a merge literal may
        # pin any family's file but must still name a family directory, and
        # no key may be pinned twice across the modules. The package also
        # replaced the old single-file shape_pins.py, and a pin written into
        # a recreated copy of it would be dead code the guards never see, so
        # require that file to stay gone.
        self.assertFalse(
            os.path.exists(
                os.path.join(ROOT, "tests", "support", "icon", "shape_pins.py")
            )
        )
        registries = [(family, "PINS", family) for family in SHAPE_PIN_FAMILIES]
        registries.append(("__init__", "ICON_SHAPES", None))
        seen = []
        for family, registry_name, expected_family in registries:
            module = parsed_module(
                os.path.join(
                    ROOT, "tests", "support", "icon", "shape_pins", family + ".py"
                ),
                ROOT,
            )
            (literal,) = (
                node.value
                for node in module.body
                if isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == registry_name
                    for target in node.targets
                )
            )
            self.assertIsInstance(literal, ast.Dict)
            # A None key is a ``**family`` merge, not a pinned file.
            paths = [
                eval(compile(ast.Expression(key), "<pin-key>", "eval"), {"os": os})
                for key in literal.keys
                if key is not None
            ]
            self.assertEqual(len(paths), len(set(paths)), family)
            for path in paths:
                named_family = os.path.normpath(path).split(os.sep)[1]
                if expected_family is None:
                    self.assertIn(named_family, SHAPE_PIN_FAMILIES, path)
                else:
                    self.assertEqual(named_family, expected_family, path)
            seen.extend(paths)
        self.assertEqual(len(seen), len(set(seen)))

    def test_each_icon_draws_its_pinned_artwork(self):
        for icon, expected in ICON_SHAPES.items():
            with self.subTest(icon=icon):
                tree = parse_svg(os.path.join(PACKAGE, icon))
                self.assertEqual(_drawing_elements(tree), expected)

    def test_removable_drive_shares_the_hard_disk_body_and_bevel(self):
        # The removable drive is the hard disk with a slot in place of the
        # label plate, so its first six drawing elements (the outline, face
        # and bevel) must be the hard disk's at every size. Compare the
        # shipped files, not the pinned tuples, so a drift in either file
        # fails here as well as in the pins above.
        for size in ("32x32", "22x22", "16x16"):
            disk = _shipped_elements(size, "devices", "drive-harddisk")
            removable = _shipped_elements(size, "devices", "drive-removable-media")
            self.assertEqual(
                removable[:6],
                disk[:6],
                size,
            )
        # The optical drive is also the hard disk's body and bevel holding a
        # centred disc, so its first six drawing elements must be the hard
        # disk's at 22x22 and 32x32. At 16x16 the body is two pixels taller
        # than the hard disk's face so the disc fits inside the bevel, and
        # the sharing check holds by exclusion there.
        for size in ("32x32", "22x22"):
            disk = _shipped_elements(size, "devices", "drive-harddisk")
            optical = _shipped_elements(size, "devices", "drive-optical")
            self.assertEqual(
                optical[:6],
                disk[:6],
                size,
            )

    def test_each_blank_document_shares_the_generic_page(self):
        # The blank-document names draw the generic document's page without
        # its text lines, so at each size each one must equal the first three
        # drawing elements of the shipped `text-x-generic.svg`. Comparing the
        # files catches a path edited in either file and a text line added to
        # a blank document, which would make it four or more elements long.
        for size in ("16x16", "22x22", "32x32"):
            generic = _generic_page(size)
            for name in BLANK_DOCUMENTS:
                with self.subTest(size=size, name=name):
                    drawing = _shipped_elements(size, "mimetypes", name)
                    self.assertEqual(drawing, generic)

    def test_office_document_shares_the_generic_page(self):
        # The office document is the generic document's page (its first
        # three drawing elements: the black outline, the white page and the
        # folded corner) with a heading, body lines and a signature line in
        # place of the generic's text lines, so at each size the shipped
        # `x-office-document.svg`'s first three drawing elements must be the
        # shipped `text-x-generic.svg`'s. Compare the files, so a drift in
        # either file fails both.
        for size in ("16x16", "22x22", "32x32"):
            generic = _generic_page(size)
            office = _shipped_elements(size, "mimetypes", "x-office-document")
            self.assertEqual(office[:3], generic, size)

    def test_office_spreadsheet_shares_the_generic_page(self):
        # The spreadsheet is the generic document's page (its first three
        # drawing elements: the black outline, the white page and the folded
        # corner) with a table grid in place of the generic's text lines, so
        # at each size the shipped `x-office-spreadsheet.svg`'s first three
        # drawing elements must be the shipped `text-x-generic.svg`'s.
        # Compare the files, so a drift in either file fails both.
        for size in ("16x16", "22x22", "32x32"):
            generic = _generic_page(size)
            spreadsheet = _shipped_elements(size, "mimetypes", "x-office-spreadsheet")
            self.assertEqual(spreadsheet[:3], generic, size)

    def test_the_template_document_shares_the_generic_page(self):
        # The template document is the generic document's page (its first
        # three drawing elements: the black outline, the white page and the
        # folded corner) holding a stencil plate in place of the generic's
        # text lines, so at each size the shipped
        # `text-x-generic-template.svg`'s first three drawing elements must
        # be the shipped `text-x-generic.svg`'s. Compare the files, so a
        # drift in either file fails both.
        for size in ("16x16", "22x22", "32x32"):
            generic = _generic_page(size)
            template = _shipped_elements(
                size, "mimetypes", "text-x-generic-template"
            )
            self.assertEqual(template[:3], generic, size)

    def test_the_script_document_shares_the_generic_page(self):
        # The script document is the generic document's page (its first
        # three drawing elements: the black outline, the white page and the
        # folded corner) with angle brackets and code lines in place of the
        # generic's text lines, so at each size the shipped
        # `text-x-script.svg`'s first three drawing elements must be the
        # shipped `text-x-generic.svg`'s. Compare the files, so a drift in
        # either file fails both.
        for size in ("16x16", "22x22", "32x32"):
            generic = _generic_page(size)
            script = _shipped_elements(size, "mimetypes", "text-x-script")
            self.assertEqual(script[:3], generic, size)

    def test_the_font_document_shares_the_generic_page(self):
        # The font document is the generic document's page (its first
        # three drawing elements: the black outline, the white page and the
        # folded corner) holding a capital letter A in place of the
        # generic's text lines, so at each size the shipped
        # `font-x-generic.svg`'s first three drawing elements must be the
        # shipped `text-x-generic.svg`'s. Compare the files, so a drift in
        # either file fails both.
        for size in ("16x16", "22x22", "32x32"):
            generic = _generic_page(size)
            font = _shipped_elements(size, "mimetypes", "font-x-generic")
            self.assertEqual(font[:3], generic, size)

    def test_office_presentation_shares_the_generic_page(self):
        # The presentation is the generic document's page (its first three
        # drawing elements: the black outline, the white page and the folded
        # corner) with a slide in place of the generic's text lines, so at
        # each size the shipped `x-office-presentation.svg`'s first three
        # drawing elements must be the shipped `text-x-generic.svg`'s.
        # Compare the files, so a drift in either file fails both.
        for size in ("16x16", "22x22", "32x32"):
            generic = _generic_page(size)
            presentation = _shipped_elements(
                size, "mimetypes", "x-office-presentation"
            )
            self.assertEqual(presentation[:3], generic, size)

    def test_standard_places_file_names_are_shipped(self):
        # The shared inventory must cover the names the standard places data
        # writes, not just the names KIO's model happens to list. In
        # particular Downloads is `folder-downloads` (plural) in the
        # standard `user-places.xbel` entries, so that shared-folder alias
        # has to be present at every size.
        for name in USER_PLACES_ICONS:
            with self.subTest(name=name):
                self.assertIn(name, STANDARD_PLACES)
                for size in ("16x16", "22x22", "32x32"):
                    self.assertIn(
                        os.path.join(size, "places", name + ".svg"),
                        SHIPPED_ICONS,
                    )

    def test_every_place_alias_shares_the_folder_art(self):
        # Mac OS 8.6 draws one folder shape for the `folder` name and every
        # place alias (`inode-directory`, `user-home`, `user-desktop` and the
        # standard XDG places), so each alias must stay the same drawing at
        # every shipped size; pinning only each one's own elements would let
        # them drift apart.
        for size in ("16x16", "22x22", "32x32"):
            with self.subTest(size=size):
                self._assert_aliases_share_folder_art(size)

    def _assert_aliases_share_folder_art(self, size):
        """Pin every folder alias's drawing to the folder's at *size*."""
        folder = _shipped_elements(size, "places", "folder")
        for alias in FOLDER_ALIASES:
            with self.subTest(size=size, alias=alias):
                drawing = _shipped_elements(size, "places", alias)
                self.assertEqual(drawing, folder)


if __name__ == "__main__":
    unittest.main()
