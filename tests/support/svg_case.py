"""Shared parse-once base for tests that read a shipped SVG file.

A widget test that pins one SVG parses it in every method that reads it; this
mixin parses `SVG_PATH` once per test in `setUp` and exposes the tree as
`self.tree`, so the methods share one parse and one attribute name. It is a
plain mixin, not a `TestCase`, so importing it does not collect an
unconfigured base.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from support import containment
from support.repo_root import ROOT


def parse_svg(path):
    """Parse the SVG at *path*, refusing a symlink that escapes the repository.

    A shipped SVG is contributor-supplied, and a checked-in symlink at its
    path can point at a private file; `ET.parse` reads the target, and the
    widget assertions echo attribute values (a fill, a path's `d`) into a
    failing test's diagnostic, so following such a symlink would leak that
    file's content. A path that resolves outside the repository is refused
    before it is opened. The Kvantum SVG tests parse through here, and
    `SvgCase.setUp` calls it, so this is the one guard those paths share.
    """
    containment.require_within_repo(path, ROOT)
    return ET.parse(path)


class SvgCase:
    """Mixin: parse `SVG_PATH` once per test into `self.tree`.

    Subclasses set `SVG_PATH` to the SVG file they pin and list `SvgCase`
    before `unittest.TestCase` in their bases.
    """

    SVG_PATH = None

    def setUp(self):
        self.tree = parse_svg(self.SVG_PATH)
