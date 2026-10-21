"""Shared reader and parser for the standalone GTK 3 and GTK 4 Platinum sheets.

Both sheet tests read their stylesheet into the same ``@define-color`` map,
selector declarations and selector list with :func:`parse_css`, so a change to
the parsing rules is checked against both sheets rather than re-derived in each.
"""

from __future__ import annotations

import re

from support import containment
from support.repo_root import ROOT


DEFINE_COLOR = re.compile(
    r"@define-color\s+(?P<name>[-A-Za-z0-9_]+)\s+(?P<value>#[0-9A-Fa-f]{6})\s*;"
)
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
RULE = re.compile(r"(?P<selectors>[^{}]+)\{(?P<body>[^{}]*)\}")
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")


def read_theme_text(path):
    """Return *path*'s text, refusing a symlink that escapes the repository.

    A GTK theme's ``index.theme`` and ``gtk.css`` are contributor-supplied, and
    a checked-in symlink at either path can point at a private file. The
    standalone-sheet assertions echo the stylesheet (``assertNotIn`` prints the
    whole container) and configparser echoes the line it rejects, so following
    such a symlink would leak that file's content into a failing test's
    diagnostic. The shared reader also refuses a FIFO or device instead of
    blocking and bounds the file size instead of loading it whole.
    """
    return containment.read_text(path, ROOT, encoding="utf-8")


def parse_css(text):
    """Return the ``@define-color`` map, selector declarations and selector list.

    A selector that appears in more than one block keeps every declaration,
    with a later block's declaration replacing an earlier one, which is how the
    cascade resolves the same declaration. Comments are removed first so a
    colour named in the header cannot stand in for a rule's value.
    """
    text = COMMENT.sub("", text)
    definitions = {
        match.group("name"): match.group("value")
        for match in DEFINE_COLOR.finditer(text)
    }
    rules = {}
    selectors = []
    without_definitions = DEFINE_COLOR.sub("", text)
    for block in RULE.finditer(without_definitions):
        declarations = {}
        for chunk in block.group("body").split(";"):
            if ":" not in chunk:
                continue
            name, value = chunk.split(":", 1)
            declarations[" ".join(name.split())] = " ".join(value.split())
        group = [
            " ".join(selector.split())
            for selector in block.group("selectors").split(",")
        ]
        for selector in group:
            selectors.append(selector)
            rules.setdefault(selector, {}).update(declarations)
    return definitions, rules, selectors
