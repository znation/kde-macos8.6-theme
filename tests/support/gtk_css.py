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
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")


def strip_comments(text):
    """Return *text* with each ``/* ... */`` comment removed.

    The matching regular expression (``/\\*.*?\\*/`` with ``DOTALL``) is
    quadratic on a contributor-supplied sheet with many comment starts and no
    end: the lazy body rescans to the end from every start, so a 24 KB run of
    ``/*a`` takes seconds and a 1 MiB sheet stalls the suite for minutes. This
    scanner consumes each comment and scans the text between comments once,
    and keeps an unterminated ``/*`` (with the rest of the text) in place, as
    the regular expression did.
    """
    parts = []
    position = 0
    while True:
        start = text.find("/*", position)
        if start == -1:
            parts.append(text[position:])
            return "".join(parts)
        end = text.find("*/", start + 2)
        if end == -1:
            parts.append(text[position:])
            return "".join(parts)
        parts.append(text[position:start])
        position = end + 2


def _rule_blocks(text):
    """Yield each ``(selectors, body)`` pair from a stylesheet body.

    This is the linear equivalent of the removed
    ``(?P<selectors>[^{}]+)\\{(?P<body>[^{}]*)\\}`` regular expression. That
    expression is quadratic on a run of text with no brace, because at every
    starting position its selector body rescans to the end looking for ``{``;
    a 20 KB unbraced run took seconds. The scanner keeps the run of non-brace
    characters since the last brace as the pending selector or body, so it
    walks the text once. A nested ``{`` replaces the pending selector, which
    is the inner-block match the expression made (``a{b{c}d}`` yields ``b`` /
    ``c``), and a ``}`` that closes no block is skipped, as the expression's
    search would also skip it.
    """
    selectors = None
    buffer = []
    for char in text:
        if char == "{":
            candidate = "".join(buffer)
            buffer = []
            selectors = candidate or None
        elif char == "}":
            if selectors is not None:
                yield selectors, "".join(buffer)
            selectors = None
            buffer = []
        else:
            buffer.append(char)


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
    text = strip_comments(text)
    definitions = {
        match.group("name"): match.group("value")
        for match in DEFINE_COLOR.finditer(text)
    }
    rules = {}
    selectors = []
    without_definitions = DEFINE_COLOR.sub("", text)
    for selector_text, body in _rule_blocks(without_definitions):
        declarations = {}
        for chunk in body.split(";"):
            if ":" not in chunk:
                continue
            name, value = chunk.split(":", 1)
            declarations[" ".join(name.split())] = " ".join(value.split())
        group = [
            " ".join(selector.split())
            for selector in selector_text.split(",")
        ]
        for selector in group:
            selectors.append(selector)
            rules.setdefault(selector, {}).update(declarations)
    return definitions, rules, selectors
