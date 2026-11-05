"""Static pins over the shipped decoration package's hit surfaces.

The package copies the engine's QML components, and the 2026-11-04
part 3/3 plan added one behavior to three of them: every interactive hit
area is additionally enabled only while `decoration.client.active`, so a
click on an unfocused window's flat buttonless bar falls through to the
title bar's activation instead of pressing an invisible close, maximize or
menu button (Platinum is active=frontmost, per the 2026-11-04 direction).
These pins are parse/grep-level statements about the shipped copies in the
style of the splash QML pins; they need no reference image and no engine
render. The landed aurorae button SVG art stays byte-identical -- the pin
is a digest set, the same content pin `tests/test_fonts.py` spells -- so
any art change fails here beside the paintless `inactive-center` pins in
`tests/test_aurorae_buttons.py`, which they keep true.
"""

from __future__ import annotations

import hashlib
import re
import unittest

from support.aurorae_fixtures import AURORAE_ID
from support.repo_root import ROOT

PACKAGE_UI = f"{ROOT}/theme/kwin-decoration/{AURORAE_ID}/contents/ui"
BUTTON_SVG_DIR = f"{ROOT}/theme/aurorae/themes/{AURORAE_ID}"

# The landed button art set, re-digested 2026-11-05 after each button's
# `inactive-center` group gained the paintless full-canvas path that makes
# `supportsInactive` resolve true (an empty group drew the active box on
# unfocused bars); the gating edits only QML.
LANDED_SVG_DIGESTS = {
    "close.svg": "50bb86821206753fa1c7410a411ed1cce2d51012b2c7c097df26102bb1a7d592",
    "maximize.svg": "7c8f955bc3aeb032655c1128ca6cc1d4a68009e1feff09e614caa9628c05dc82",
    "restore.svg": "1552ce5806120f8e1273c70108567451a89f6f40015df2c20d7b2f7e7177d76e",
    "shade.svg": "8fc57a040f09d96d606c5b498c0073cf729981983e550131f2e7e1ea7d62c8eb",
}


def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def object_blocks(text, head_re):
    """Return every block matching head_re, each closed by its matching '}'.

    A QML object or binding is a `{ head ... }` span; brace matching serves
    the shipped copies, which put no brace inside a string literal.
    """
    blocks = []
    for match in re.finditer(head_re, text, re.MULTILINE):
        open_index = text.index("{", match.start())
        depth = 0
        for index in range(open_index, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[open_index : index + 1])
                    break
    return blocks


class TestHitSurfaces(unittest.TestCase):
    """Every interactive hit area is disabled on an unfocused client."""

    def test_the_base_item_binding_guards_window_activity(self):
        # `DecorationButton.qml` is `AuroraeButton`'s base type and
        # `AppMenuButton`'s child type, so the item-level `enabled` guard
        # disables those buttons' MouseAreas with the one below it.
        text = read_text(f"{PACKAGE_UI}/DecorationButton.qml")
        self.assertEqual(len(object_blocks(text, r"^\s*MouseArea \{$")), 1)
        blocks = object_blocks(text, r"^\s*enabled: \{$")
        self.assertEqual(len(blocks), 1, "one item-level enabled block")
        enabled = blocks[0]
        # The guard sits ahead of the switch stock gates capability with, so
        # an unfocused client disables the Item before any case runs.
        self.assertIn("if (!decoration.client.active) {", enabled)
        self.assertIn("return false;", enabled)
        self.assertLess(
            enabled.index("if (!decoration.client.active)"),
            enabled.index("switch (button.buttonType)"),
            "the guard must precede the capability switch",
        )

    def test_both_gated_mouseareas_bind_activity_alone(self):
        for name in ("MenuButton.qml", "AuroraeMaximizeButton.qml"):
            with self.subTest(copy=name):
                text = read_text(f"{PACKAGE_UI}/{name}")
                areas = object_blocks(text, r"^\s*MouseArea \{$")
                self.assertEqual(len(areas), 1, name)
                self.assertIn("enabled: decoration.client.active", areas[0], name)
                # One conjunct, not a compound: art and geometry must not ride
                # this binding.
                self.assertEqual(
                    areas[0].count("decoration.client.active"), 1, name
                )

    def test_no_copy_escapes_the_gate_through_inheritance(self):
        # Both remaining button types ride DecorationButton's guarded item
        # `enabled`; if one gains its own ungated MouseArea, the counts below
        # name it instead of letting an invisible button press again.
        aurorae_button = read_text(f"{PACKAGE_UI}/AuroraeButton.qml")
        self.assertIn("\nDecorationButton {\n", aurorae_button)
        self.assertLessEqual(
            len(object_blocks(aurorae_button, r"^DecorationButton \{$")), 1,
            "the DecorationButton head is the root object",
        )
        self.assertEqual(
            object_blocks(aurorae_button, r"^\s*MouseArea \{$"), [],
            "AuroraeButton rides its base type's guarded MouseArea",
        )
        app_menu = read_text(f"{PACKAGE_UI}/AppMenuButton.qml")
        self.assertIn("DecorationButton {", app_menu)
        self.assertEqual(app_menu.count("MouseArea {"), 0, "AppMenuButton.qml")
        self.assertEqual(
            read_text(f"{PACKAGE_UI}/AuroraeButtonGroup.qml").count("MouseArea {"),
            0,
            "AuroraeButtonGroup.qml",
        )

    def test_independent_button_art_went_untouched(self):
        for name, digest in LANDED_SVG_DIGESTS.items():
            with open(f"{BUTTON_SVG_DIR}/{name}", "rb") as handle:
                self.assertEqual(
                    hashlib.sha256(handle.read()).hexdigest(), digest, name
                )


if __name__ == "__main__":
    unittest.main()
