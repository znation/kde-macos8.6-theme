"""Tests for the inactive-dialog render's forced-geometry window rules.

``tools/render_window_rules.py`` writes the scratch session's
``kwinrulesrc``: exactly two rules, one per fixed client title, each
forcing both position and size so the two ``kdialog --msgbox`` windows of
the ``--inactive-dialog`` render stand side by side, fully inside the
480x360 dialog capture. The file is pinned byte for byte here, and the
session workflow calls the writer only for the mode that names the file.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import render_dialogs
from tools.render_window_rules import (
    FOCUSED_GEOMETRY,
    FOCUSED_TITLE,
    INACTIVE_GEOMETRY,
    INACTIVE_TITLE,
    RULES_FILE,
    rules_text,
    write_window_rules,
)


class _FakeSession:
    """The one attribute the writer reads: the scratch config home."""

    def __init__(self, config: Path):
        self.config = config


class TestWindowRules(unittest.TestCase):
    def test_the_rules_file_is_the_kwin_rules_store_name(self):
        # The workflow matches the mode's extra_config_files entry against
        # this name, and KWin reads its rule book from kwinrulesrc.
        self.assertEqual("kwinrulesrc", RULES_FILE)

    def test_the_rules_hold_exactly_two_forced_geometry_rules(self):
        # Byte-for-byte: the match criteria (the exact client titles) and
        # the forced settings are the contract KWin reads, so a wrong key,
        # a missing rule or an extra entry would change which window draws
        # where without any test failing here. The grammar keys were probed
        # against the installed KWin 6.3.6 (libkwin.so.6's RuleSettings
        # diagnostics name setTitlematch, setSizerule and setPositionrule;
        # kcm_kwinrules's comboboxes list Unimportant/Exact match/Substring
        # match/Regular expression and Do not affect/Apply initially/
        # Remember/Force/Apply now/Force temporarily): titlematch 1 = exact
        # match, positionrule/sizerule 3 = force. The first measured
        # inactive-dialog render on this host (2026-11-11) applied every
        # forced value to the pixel: the left frame measured
        # (4,8)-(227,351) and the right one (252,8)-(475,351), the two
        # standing non-overlapping inside the 480x360 capture with a 24px
        # black desktop band between them, the left one drawn with the
        # inactive art (flat #DDDDDD bar, #777777 title ink, no button
        # boxes) and the right one with the active art.
        self.assertEqual(
            "[General]\n"
            "count=2\n"
            "\n"
            "[1]\n"
            "Description=forced geometry for Inactive window\n"
            "title=Inactive window\n"
            "titlematch=1\n"
            "position=4,8\n"
            "positionrule=3\n"
            "size=224,344\n"
            "sizerule=3\n"
            "\n"
            "[2]\n"
            "Description=forced geometry for Focused window\n"
            "title=Focused window\n"
            "titlematch=1\n"
            "position=252,8\n"
            "positionrule=3\n"
            "size=224,344\n"
            "sizerule=3\n",
            rules_text(),
        )

    def test_the_two_titles_are_distinct_exact_matches(self):
        # KWin activates the newest window, so the rules must tell the two
        # kdialog windows apart by exact title: the inactive one spawns
        # first, the focused one last, and the client wrapper (the
        # inactive_dialog_client factory in tools/render_clients.py) opens
        # them with these titles. A shared title would rule-match both
        # windows and leave the pair's placement to ordering alone.
        self.assertNotEqual(INACTIVE_TITLE, FOCUSED_TITLE)

    def test_both_windows_stand_inside_the_dialog_capture_side_by_side(self):
        # Each rule forces the window fully inside the 480x360 dialog
        # capture, and the two forced rectangles do not overlap: the pair
        # (validated by the first measured render recorded in the bytes
        # test above) must never clip at the capture edge or stack, or the
        # inactive-window gate's left-window crop would lose the bar.
        (ix, iy), (iw, ih) = INACTIVE_GEOMETRY
        (fx, fy), (fw, fh) = FOCUSED_GEOMETRY
        self.assertGreaterEqual(ix, 0)
        self.assertGreaterEqual(iy, 0)
        self.assertLessEqual(ix + iw, 480)
        self.assertLessEqual(iy + ih, 360)
        self.assertGreaterEqual(fx, 0)
        self.assertGreaterEqual(fy, 0)
        self.assertLessEqual(fx + fw, 480)
        self.assertLessEqual(fy + fh, 360)
        self.assertLess(ix + iw, fx, "the windows must not overlap")

    def test_write_window_rules_writes_the_store_into_the_config_home(self):
        import tempfile

        with tempfile.TemporaryDirectory() as root:
            config = Path(root)
            write_window_rules(_FakeSession(config))
            self.assertEqual(
                rules_text().encode("utf-8"),
                (config / RULES_FILE).read_bytes(),
            )

    def test_only_the_inactive_mode_names_the_rules_file(self):
        # The workflow writes kwinrulesrc only where a mode's
        # extra_config_files names it, so no other mode's session may carry
        # the two-window rules.
        named = [
            mode.attr
            for mode in render_dialogs.DIALOG_MODES
            if RULES_FILE in mode.extra_config_files
        ]
        self.assertEqual(["inactive_dialog"], named)


if __name__ == "__main__":
    unittest.main()
