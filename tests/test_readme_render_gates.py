"""The user docs' dialog-gate prose must name the gates that ship.

Two staleness shapes: a `Test...DialogRender` gate class present in
``tests/test_render_surface.py`` that the user-docs corpus' render prose
omits, and a ``tests/test_render_surface.py::Test...`` token whose class no
longer exists (a renaming or removal that leaves the prose pointing at
nothing). The expectations are derived from the live test module and the
corpus (README plus the guides it links, docs/rendering.md among them), not
copied from either, so prose and code cannot drift in opposite directions.
"""

from __future__ import annotations

import os
import re
import unittest

from support import containment
from support.repo_root import ROOT
from support.user_docs import read_user_docs

# Gate classes ship as top-level definitions, so a class name present
# anywhere in ``tests/test_render_surface.py`` as a definition is the live
# set; a comment or docstring mention alone never defines one.
_GATE_CLASS = re.compile(r"^class (Test\w*DialogRender)\b", re.MULTILINE)

# README names each gate as a fully qualified ``tests/test_render_surface.py
# ::Test<Name>`` token, possibly split across a wrapped line as a bare
# ``::Test<Name>`` continuation of the sentence chain.
_README_TOKEN = re.compile(r"(?:tests/test_render_surface\.py)?::(Test\w+)")


def read(name):
    """Return the UTF-8 text of the repository file at *name*.

    Same containment guard as the sibling README readers: a checked-in
    symlink that resolves outside the repository is refused before it is
    opened.
    """
    return containment.read_text(os.path.join(ROOT, name), ROOT, encoding="utf-8")


def corpus():
    """Return README plus the guides it links, through the containment reader."""
    return read_user_docs(ROOT)


class TestReadmeDialogGateProse(unittest.TestCase):
    def test_readme_names_every_dialog_render_gate(self):
        module = read(os.path.join("tests", "test_render_surface.py"))
        gates = set(_GATE_CLASS.findall(module))
        named = {
            name
            for name in _README_TOKEN.findall(corpus())
            if name.endswith(("DialogRender",))
        }
        self.assertTrue(gates, "test_render_surface defines no dialog gates")
        self.assertEqual(
            gates,
            named,
            "README's dialog-gate tokens and the shipped Test...DialogRender "
            "classes disagree",
        )

    def test_readme_does_not_call_the_menu_gate_unpinned(self):
        # The menu item-view's gate landed; the prose that once said the pin
        # was missing must not return, and the dialog-render summary paragraph
        # must keep naming the menu gate beside the two older ones.
        text = corpus()
        self.assertNotIn("no gate compares", text)
        self.assertNotIn("BUGS.md tracks adding that pin", text)
        summary = next(
            block
            for block in text.split("\n\n")
            if "TestCheckboxDialogRender" in block and "suite runs" in block
        )
        self.assertIn("TestMenuDialogRender", summary)
        bullet = next(
            block
            for block in text.split("\n\n")
            if "GenericFrame" in block and "--menu-dialog" in block
        )
        self.assertIn("TestMenuDialogRender", bullet)

    def test_readme_documents_the_decoration_selection_equality(self):
        # The shipped selection renders in every capture: README names the
        # pair the scratch home takes from the look-and-feel defaults and
        # points at the session-level A/B equality evidence recorded in
        # docs/invariants.md.
        text = corpus()
        paragraph = next(
            block
            for block in text.split("\n\n")
            if "scratch data home" in block and "byte-identical" in block
        )
        self.assertIn("theme=org.macos8.desktop", paragraph)
        self.assertIn("library=org.kde.kwin.aurorae", paragraph)
        self.assertIn("__aurorae__svg__org.macos8.desktop", paragraph)
        self.assertIn("## kwin-decoration", paragraph)
        self.assertIn("invariants.md", paragraph)


if __name__ == "__main__":
    unittest.main()
