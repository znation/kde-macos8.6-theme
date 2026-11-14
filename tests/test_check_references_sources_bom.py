"""BOM handling of sources.txt in tools/reference_sources.py's record reader.

sources.txt is contributor-supplied UTF-8 that an editor may save with a
leading byte-order mark. The record reader decodes it with ``utf-8-sig``, so
the BOM is not part of the first declared filename: a BOM-prefixed record
with a valid declaration reports nothing, and a missing declared file is
named without a BOM glued to it.
"""
import unittest

from support.check_references_fixtures import (
    CheckerTestCase,
    reference_set,
)
from tools.image_format import PNG_MAGIC, TERMINAL_PNG

BOM = "\ufeff"


class TestBomPrefixedSources(CheckerTestCase):
    """A sources.txt that starts with a UTF-8 BOM is read like one without."""

    def test_bom_prefixed_record_with_a_valid_declaration_is_clean(self):
        module = self.checker
        record = (
            BOM + "good.png | https://example.test/g.png | label\n"
        ).encode("utf-8")
        with reference_set(
            module, record, {"good.png": PNG_MAGIC + TERMINAL_PNG}
        ) as root:
            problems = module.check_references(root)
        self.assertEqual([], problems)

    def test_bom_is_not_glued_to_the_first_declared_filename(self):
        module = self.checker
        record = (
            BOM + "missing.png | https://example.test/m.png | label\n"
        ).encode("utf-8")
        with reference_set(module, record) as root:
            problems = module.check_references(root)
        self.assertTrue(
            any("missing.png" in line for line in problems), problems
        )
        self.assertFalse(
            any(BOM in line for line in problems), problems
        )


if __name__ == "__main__":
    unittest.main()
