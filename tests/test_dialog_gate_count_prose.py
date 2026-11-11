"""The prose that counts the dialog gates must track the shipped gates.

Three prose files count the dialog render gates in words: ``docs/invariants.md``'s
skip-guard and software-renderer rows, ``tests/test_ci_workflow.py``'s
workflow-install comment, and ``tests/test_render_surface.py``'s skip-guard
comments and gate-scaffold docstrings. Those files count the kdialog modes too.
When a dialog gate lands (as the color gate did), those words must move with it:
a count that lags the code quietly under-reports the gates the shared skip guard
covers. The shift to the color gate left ``tests/test_render_surface.py``'s own
comment and docstring stale, so the defining file is scanned beside the surfaces
that describe it.
The expected counts derive from the live ``Test...DialogRender`` gate
classes in ``tests/test_render_surface.py``, never from the prose, so the
two cannot drift in opposite directions.
"""

from __future__ import annotations

import os
import re
import unittest

from support import containment
from support.repo_root import ROOT

# Gate classes ship as top-level definitions, so a class name defined
# anywhere in ``tests/test_render_surface.py`` is the live set; a mention
# in a comment or docstring alone never defines one.
_GATES = re.compile(r"^class (Test\w*DialogRender)\b", re.MULTILINE)
_DIALOG_GATE_COUNT = re.compile(r"[Tt]he (\w+) dialog(?: render)? gates")
_KDIALOG_MODE_COUNT = re.compile(r"[Tt]he (\w+) kdialog modes")
# The prose spells its counts; ``other`` is the one non-numeric word the
# shipped prose uses in the same position ("the other dialog gates").
_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12,
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
        gates = set(
            _GATES.findall(read(os.path.join("tests", "test_render_surface.py")))
        )
        self.assertTrue(gates, "test_render_surface defines no dialog gates")
        # TestGtkDialogRender opens zenity; every other dialog gate opens a
        # kdialog client, so the kdialog-mode count is the gate count minus
        # that one.
        kdialog_modes = len(gates) - 1
        for pattern, expected in (
            (_DIALOG_GATE_COUNT, len(gates)),
            (_KDIALOG_MODE_COUNT, kdialog_modes),
        ):
            for name in (
                "docs/invariants.md",
                "tests/test_ci_workflow.py",
                "tests/test_render_surface.py",
            ):
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
                    f"{expected} derived from "
                    "test_render_surface's gate classes",
                )


if __name__ == "__main__":
    unittest.main()
