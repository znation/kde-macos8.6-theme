"""Guard the desktop-theme package's deliberate legacy default-theme omission.

The package ships 31 of the stock default theme's 43 ``widgets/`` stems and
deliberately leaves twelve of them unshipped: no installed Plasma 6 shell,
plasmoid or desktop QML requests one, so each element keeps the stock default
theme's art. This module registers the policy: no package file may carry a
legacy stem's name, the shipped set may not drift beyond the tracked closed
set, and the docs must name the same twelve stems this module names.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import unittest

from support.desktoptheme_paths import PACKAGE
from support.repo_root import ROOT
from support.shipped_files import shipped_files
from support.user_docs import read_user_docs

LEGACY_STEMS = (
    "analog_meter",
    "bar_meter_vertical",
    "branding",
    "calendar",
    "configuration-icons",
    "dragger",
    "glowbar",
    "media-delegate",
    "monitor",
    "picker",
    "plot-background",
    "scrollwidget",
)

INVARIANTS_MD = os.path.join(ROOT, "docs", "invariants.md")
README_ANCHOR = (
    "The package carries no art for the twelve legacy "
    "default-theme widget names"
)
README_GUARD_MENTION = "tests/test_desktoptheme_legacy.py"

_CODE_SPAN = re.compile(r"`([^`]+)`")
_STEM_SPAN = re.compile(r"[a-z]+(?:[_-][a-z]+)*")


def stem_spans(text):
    """Return the stem-shaped backticked spans *text* spells, in spell order.

    A span is a stem name when it is code-quoted and spells only lower-case
    words joined by ``_`` or ``-`` prose-free, so paths, ``metadata.json`` and
    plain prose words never register as stems.
    """
    return [
        span
        for span in (match.group(1).strip() for match in _CODE_SPAN.finditer(text))
        if _STEM_SPAN.fullmatch(span)
    ]


def shipped_package_files(root=PACKAGE):
    """Return the files *root* ships, package-relative, links refused."""
    return shipped_files(root, suffix=None)


def legacy_named(files):
    """Return the sorted *files* whose base name is a legacy stem."""
    return sorted(
        path
        for path in files
        if os.path.splitext(os.path.basename(path))[0] in LEGACY_STEMS
    )


class TestDesktopThemeLegacy(unittest.TestCase):
    """The shipped package carries no legacy default-theme widget art."""

    def test_no_legacy_default_theme_art_ships(self):
        files = shipped_package_files()
        self.assertEqual(
            legacy_named(files),
            [],
            "the package ships art named with a legacy default-theme stem",
        )
        svg = {path for path in files if path.endswith(".svg")}
        self.assertEqual(
            files - svg,
            {"metadata.json"},
            "the package ships a regular file beyond the closed set",
        )
        widgets = {path for path in svg if path.startswith("widgets" + os.sep)}
        # The widget facet's closed-set equality is the existing registry test's
        # job (TestSvgRootCanvas); this counts the facet so a member lost or
        # added fails naming every name the tree holds.
        self.assertEqual(len(widgets), 31, sorted(svg))
        self.assertEqual(
            svg - widgets,
            {
                "dialogs/background.svg",
                "solid/widgets/panel-background.svg",
                "solid/widgets/tooltip.svg",
            },
        )

    def test_a_stubbed_legacy_named_file_fails_the_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = os.path.join(tmp, "org.macos8.desktop")
            shutil.copytree(PACKAGE, copy)
            with open(
                os.path.join(copy, "widgets", "plot-background.svg"),
                "w",
                encoding="utf-8",
            ):
                pass
            self.assertEqual(
                legacy_named(shipped_package_files(copy)),
                [os.path.join("widgets", "plot-background.svg")],
            )

    def test_policy_registers_the_same_stems(self):
        with open(INVARIANTS_MD, encoding="utf-8") as handle:
            invariants = handle.read()
        section = invariants.split("## desktoptheme", 1)[1].split("\n## ", 1)[0]
        rows = [
            line
            for line in section.splitlines()
            if any(token in LEGACY_STEMS for token in stem_spans(line))
        ]
        self.assertEqual(len(rows), 1, "one desktoptheme row may name the stems")
        self.assertEqual(
            stem_spans(rows[0]),
            list(LEGACY_STEMS),
            "the invariant row names a different stem set or order",
        )

        corpus = read_user_docs()
        start = corpus.find(README_ANCHOR)
        self.assertGreater(
            start,
            corpus.find("translucent rounded rectangle"),
            "the corpus sentence sits after the anchor surface",
        )
        guard = corpus.find(README_GUARD_MENTION, start)
        self.assertEqual(
            stem_spans(corpus[start:guard]),
            list(LEGACY_STEMS),
            "the corpus sentence names a different stem set or order",
        )
        self.assertGreater(
            corpus.find("The window decoration ships", start),
            guard,
            "the corpus sentence sits after the window-decoration paragraph",
        )


if __name__ == "__main__":
    unittest.main()
