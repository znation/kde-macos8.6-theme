"""The prose that counts the dialog gates must track the shipped gates.

Prose counts the dialog render gates in words: ``docs/invariants.md``'s
skip-guard and software-renderer rows, ``tests/test_ci_workflow.py``'s
workflow-install comment, and the skip-guard comments and gate-scaffold
docstrings the capture suites carry. Those files count the kdialog modes too.
When a dialog gate lands (as the color gate did), those words must move with it:
a count that lags the code quietly under-reports the gates the shared skip guard
covers. The shift to the color gate left the defining suite's own
comment and docstring stale, so the defining files are scanned beside the surfaces
that describe them.
The expected gate count derives from the live ``Test...DialogRender`` gate
classes in the render capture suites, never from the prose, so the
two cannot drift in opposite directions.
The kdialog-mode count derives from the live ``DIALOG_MODES`` table in
``tools/render_dialogs.py``, not from the gate classes: a mode can land before
its gate (the file-dialog series' part 1/2 added the mode, part 2/2 its gate),
and the words that say how many kdialog clients the render CLI demands must
track the CLI's table from the moment the mode exists, not wait for the gate.
``tests/test_render_dialogs.py``'s table docstring counts the dialog modes
beside the table it describes, so its word is pinned here too.
"""

from __future__ import annotations

import os
import re
import unittest

from support import containment
from support.repo_root import ROOT
from tools import render_dialogs

# Gate classes ship as top-level definitions, so a class name defined
# anywhere in the render capture suites is the live set; a mention
# in a comment or docstring alone never defines one.
_GATES = re.compile(r"^class (Test\w*DialogRender)\b", re.MULTILINE)
_GATE_FILES = (
    "tests/test_render_surface.py",
    "tests/test_render_dialog_gates.py",
    "tests/test_render_file_dialog.py",
)
_DIALOG_GATE_COUNT = re.compile(r"[Tt]he (\w+) dialog(?: render)? gates")
_KDIALOG_MODE_COUNT = re.compile(r"[Tt]he (\w+) kdialog modes")
_MODE_COUNT = re.compile(r"render CLI's (\w+) dialog\s+modes")
# The prose spells its counts; ``other`` is the one non-numeric word the
# shipped prose uses in the same position ("the other dialog gates").
_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14,
}
_NON_NUMERIC = frozenset({"other"})


def read(name):
    """Return the UTF-8 text of the repository file at *name*.

    Same containment guard as the sibling prose readers: a checked-in
    symlink that resolves outside the repository is refused before it is
    opened.
    """
    return containment.read_text(os.path.join(ROOT, name), ROOT, encoding="utf-8")


class TestDialogGateCountProse(unittest.TestCase):
    def test_the_count_words_match_the_counts_derived_from_the_gate_classes(
        self,
    ):
        gates = set()
        for name in _GATE_FILES:
            gates.update(_GATES.findall(read(name)))
        self.assertTrue(gates, "the render capture suites define no dialog gates")
        # The kdialog-mode count comes from the live CLI table, not from
        # the gate classes: a mode without its gate yet (file-dialog, whose
        # part 2/2 gate is still planned) would make the gate-derived
        # derivation under-count the clients the CLI already demands.
        kdialog_modes = sum(
            1 for mode in render_dialogs.DIALOG_MODES
            if mode.client_tool == "kdialog"
        )
        for pattern, expected, names in (
            (_DIALOG_GATE_COUNT, len(gates), (
                "docs/invariants.md",
                "tests/test_ci_workflow.py",
                "tests/test_render_dialog_gates.py",
                "tests/support/render_gates.py",
            )),
            (_KDIALOG_MODE_COUNT, kdialog_modes, (
                "docs/invariants.md",
                "tests/test_ci_workflow.py",
                "tests/test_render_dialog_gates.py",
            )),
            (_MODE_COUNT, len(render_dialogs.DIALOG_MODES), (
                "tests/test_render_dialogs.py",
            )),
        ):
            for name in names:
                self._assert_file_spells_its_counts(pattern, expected, name)

    def _assert_file_spells_its_counts(self, pattern, expected, name):
        for word in pattern.findall(read(name)):
            with self.subTest(file=name, word=word):
                if word in _NON_NUMERIC:
                    continue
                self.assertIn(
                    word,
                    _WORDS,
                    f"{name} counts its dialog gates with a word "
                    "the number map does not spell; teach the map",
                )
                self.assertEqual(
                    expected,
                    _WORDS[word],
                    f"{name}'s count prose lags the "
                    f"{expected} the live code counts",
                )


if __name__ == "__main__":
    unittest.main()
