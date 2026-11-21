"""Tests for the package's engine-copy manifest against the KWin engine files.

The KWin/Decoration package under theme/kwin-decoration/ copies the Aurorae
engine QML components from `/usr/share/kwin/aurorae/` (upstream KWin 6.3.6):
byte-equal where the engine file references no auroraeTheme, rename-only where
it does, and gated on window activity where it draws a button hit cell. The
manifest and expected texts live in tests/support/kwin_decoration_copies.py.
The pins skip when the engine directory is absent, like
tests/test_aurorae_buttons.py presents its reference-set skips.
"""

from __future__ import annotations

import os
import unittest

from support.kwin_decoration_copies import (
    BYTE_EQUAL_COPIES,
    ENGINE_DIR,
    GATED_COPIES,
    PACKAGE_DIR,
    RENAMED_COPIES,
    RENAMED_GATED_COPIES,
    read_text,
)


class TestCopies(unittest.TestCase):
    """The package copies as the engine files spell them."""

    @unittest.skipUnless(
        os.path.isdir(ENGINE_DIR), "needs /usr/share/kwin/aurorae/"
    )
    def test_byte_equal_copies_match_the_engine_files(self):
        for name in BYTE_EQUAL_COPIES:
            with open(f"{ENGINE_DIR}/{name}", "rb") as engine_handle:
                engine = engine_handle.read()
            with open(f"{PACKAGE_DIR}/contents/ui/{name}", "rb") as copy_handle:
                copy = copy_handle.read()
            self.assertEqual(copy, engine, name)

    @unittest.skipUnless(
        os.path.isdir(ENGINE_DIR), "needs /usr/share/kwin/aurorae/"
    )
    def test_renamed_copies_replace_only_the_theme_token(self):
        for engine_name, copy_name in RENAMED_COPIES:
            engine = read_text(f"{ENGINE_DIR}/{engine_name}")
            copy = read_text(f"{PACKAGE_DIR}/contents/ui/{copy_name}")
            expected = engine.replace("auroraeTheme.", "AuroraeTheme.")
            if copy_name in RENAMED_GATED_COPIES:
                expectation = RENAMED_GATED_COPIES[copy_name]
                with self.subTest(name=copy_name):
                    self.assertEqual(copy, expectation(engine))
                continue
            self.assertEqual(copy, expected)
            self.assertNotIn("auroraeTheme", copy, engine_name)
            self.assertEqual(
                engine.count("auroraeTheme."),
                copy.count("AuroraeTheme."),
                engine_name,
            )

    @unittest.skipUnless(
        os.path.isdir(ENGINE_DIR), "needs /usr/share/kwin/aurorae/"
    )
    def test_gated_copies_match_the_engine_files_with_their_gate(self):
        # Part 3/3 (2026-11-04): a hit-surface copy equals its engine file plus
        # exactly the dated comment and the window-activity gate, so a dropped
        # gate or an engine byte changed anywhere else fails rather than
        # silently changing what a pressed invisible button does.
        for name, expectation in GATED_COPIES:
            engine = read_text(f"{ENGINE_DIR}/{name}")
            copy = read_text(f"{PACKAGE_DIR}/contents/ui/{name}")
            with self.subTest(name=name):
                self.assertEqual(copy, expectation(engine))


if __name__ == "__main__":
    unittest.main()
