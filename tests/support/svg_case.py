"""Shared parse-once base for tests that read a shipped SVG file.

A widget test that pins one SVG parses it in every method that reads it; this
mixin parses `SVG_PATH` once per test in `setUp` and exposes the tree as
`self.tree`, so the methods share one parse and one attribute name. It is a
plain mixin, not a `TestCase`, so importing it does not collect an
unconfigured base.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET

from support import containment
from support.repo_root import ROOT

# Parsed SVG trees, keyed by absolute path. A widget suite parses its SVG in
# every test method, the desktop-theme registry parses every shipped SVG, and
# a Kvantum pixel test parses the same file from each of its classes, so an
# unchanged file keeps one tree. The fingerprint (inode, size, mtime and
# ctime) makes a rewritten or replaced file reparse instead of serving stale
# artwork; a failed read or parse is never cached. Callers treat the tree as
# read-only, and `render_slices` caches its pixels against the same identity.
_TREE_CACHE = {}


def _fingerprint(path):
    """Return *path*'s stat fingerprint, or None when it cannot be read.

    A failed stat is not cached, so the caller's `ET.parse` still reports the
    missing or unreadable path the way it did before.
    """
    try:
        stat = os.stat(path)
    except OSError:
        return None
    return (stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


def parse_svg(path):
    """Parse the SVG at *path*, refusing a symlink that escapes the repository.

    A shipped SVG is contributor-supplied, and a checked-in symlink at its
    path can point at a private file; `ET.parse` reads the target, and the
    widget assertions echo attribute values (a fill, a path's `d`) into a
    failing test's diagnostic, so following such a symlink would leak that
    file's content. A path that resolves outside the repository is refused
    before it is opened. The Kvantum SVG tests parse through here, and
    `SvgCase.setUp` calls it, so this is the one guard those paths share.

    The containment check runs on every call, before the cache is consulted,
    so a path that is swapped for an escaping symlink after an earlier parse
    is still refused. Only an unchanged file's tree is reused.
    """
    containment.require_within_repo(path, ROOT)
    key = os.path.abspath(path)
    fingerprint = _fingerprint(path)
    cached = _TREE_CACHE.get(key)
    if cached is not None and cached[0] == fingerprint:
        return cached[1]
    tree = ET.parse(path)
    if fingerprint is not None:
        _TREE_CACHE[key] = (fingerprint, tree)
    return tree


class SvgCase:
    """Mixin: parse `SVG_PATH` once per test into `self.tree`.

    Subclasses set `SVG_PATH` to the SVG file they pin and list `SvgCase`
    before `unittest.TestCase` in their bases.
    """

    SVG_PATH = None

    def setUp(self):
        self.tree = parse_svg(self.SVG_PATH)
