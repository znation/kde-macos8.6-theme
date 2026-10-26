"""Shared parse-once base for tests that read a shipped SVG file.

A widget test that pins one SVG parses it in every method that reads it; this
mixin parses `SVG_PATH` once per test in `setUp` and exposes the tree as
`self.tree`, so the methods share one parse and one attribute name. It is a
plain mixin, not a `TestCase`, so importing it does not collect an
unconfigured base.
"""

from __future__ import annotations

import io
import os
import xml.etree.ElementTree as ET

from support import containment
from support.file_identity import fingerprint_or_none
from support.repo_root import ROOT

# XML's markup declarations are ASCII, but an XML document may be encoded as
# UTF-16 as well as UTF-8 (and ASCII-compatible encodings such as Latin-1 keep
# the same bytes). These are the only spellings a document expat can expand:
# a DTD or entity declaration in any supported encoding matches one of them.
_DTD_MARKERS = tuple(
    marker
    for text in ("<!DOCTYPE", "<!ENTITY")
    for encoding in ("ascii", "utf-16-le", "utf-16-be")
    for marker in (text.encode(encoding),)
)

# Parsed SVG trees, keyed by absolute path. A widget suite parses its SVG in
# every test method, the desktop-theme registry parses every shipped SVG, and
# a Kvantum pixel test parses the same file from each of its classes, so an
# unchanged file keeps one tree. The fingerprint (inode, size, mtime and
# ctime) makes a rewritten or replaced file reparse instead of serving stale
# artwork; a failed read or parse is never cached. Callers treat the tree as
# read-only, and `render_slices` caches its pixels against the same identity.
_TREE_CACHE = {}


def parse_svg(path):
    """Parse the SVG at *path*, refusing a symlink that escapes the repository.

    A shipped SVG is contributor-supplied, and a checked-in symlink at its
    path can point at a private file; `ET.parse` reads the target, and the
    widget assertions echo attribute values (a fill, a path's `d`) into a
    failing test's diagnostic, so following such a symlink would leak that
    file's content. A path that resolves outside the repository is refused
    before it is opened. `ET.parse` also blocks forever on a FIFO and can
    stream a device without end, so the file is opened through
    `containment.open_regular_binary`, which refuses a non-regular file by
    name instead. The Kvantum SVG tests parse through here, and
    `SvgCase.setUp` calls it, so this is the one guard those paths share.

    The containment check runs on every call, before the cache is consulted,
    so a path that is swapped for an escaping symlink after an earlier parse
    is still refused. Only an unchanged file's tree is reused.

    The bytes are read through the shared containment reader, which bounds
    them at its contributor-file cap, so a multi-gigabyte SVG cannot be loaded
    whole. A DTD or entity declaration is refused before the parser sees it:
    expat expands internal entities, so a sub-megabyte document can otherwise
    allocate many times its size and exhaust memory even below the byte cap.
    """
    containment.require_within_repo(path, ROOT)
    key = os.path.abspath(path)
    fingerprint = fingerprint_or_none(path)
    cached = _TREE_CACHE.get(key)
    if cached is not None and cached[0] == fingerprint:
        return cached[1]
    data = containment.read_bytes(path, ROOT)
    if any(marker in data for marker in _DTD_MARKERS):
        raise ValueError(
            f"{path!r} declares a DTD or entity; refusing to parse it"
        )
    tree = ET.parse(io.BytesIO(data))
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
