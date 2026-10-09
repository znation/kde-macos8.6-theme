"""Shared parse-once base for tests that read a shipped SVG file.

A widget test that pins one SVG parses it in every method that reads it; this
mixin parses `SVG_PATH` once per test in `setUp` and exposes the tree as
`self.tree`, so the methods share one parse and one attribute name. It is a
plain mixin, not a `TestCase`, so importing it does not collect an
unconfigured base.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET


class SvgCase:
    """Mixin: parse `SVG_PATH` once per test into `self.tree`.

    Subclasses set `SVG_PATH` to the SVG file they pin and list `SvgCase`
    before `unittest.TestCase` in their bases.
    """

    SVG_PATH = None

    def setUp(self):
        self.tree = ET.parse(self.SVG_PATH)
