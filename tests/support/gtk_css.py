"""Shared reader and parser for the standalone Platinum sheets.

The GTK 3, GTK 4 and Firefox sheet tests read their stylesheet into the same
``@define-color`` map, selector declarations and selector list with
:func:`parse_css`, so a change to the parsing rules is checked against all
three rather than re-derived in each.
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


def _split_declarations(body):
    """Yield *body*'s declarations, split on ``;`` outside quotes and ``()``.

    A quoted string and a ``url(...)`` value may both carry a semicolon that is
    part of the value rather than a separator. Splitting on every semicolon cut
    ``url("data:image/svg+xml;base64,...")`` in two and reported the second
    half as malformed.
    """
    declaration = []
    quote = None
    depth = 0
    escaped = False
    for char in body:
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif quote is not None:
            if char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        elif char == ";" and not depth:
            yield "".join(declaration)
            declaration = []
            continue
        declaration.append(char)
    yield "".join(declaration)


def _split_selector_list(selector_text):
    """Split *selector_text* at commas outside parentheses, brackets and quotes.

    A comma inside ``:not(.a, .b)`` separates that pseudo-class's arguments,
    not two selectors of the group. A comma inside an attribute selector's
    brackets -- quoted or not -- is part of its value, as is one inside a
    quoted string, so splitting there is wrong: ``[title="a,b"]`` used to
    become the two fragments ``[title="a`` and ``b"]``, neither of which named
    a rule. A backslash-escaped quote stays inside the value.
    """
    depth = 0
    bracket_depth = 0
    quote = None
    escaped = False
    start = 0
    for index, char in enumerate(selector_text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char == "[":
            bracket_depth += 1
        elif char == "]" and bracket_depth:
            bracket_depth -= 1
        elif char == "(" and not bracket_depth:
            depth += 1
        elif char == ")" and not bracket_depth and depth:
            depth -= 1
        elif char == "," and not depth and not bracket_depth:
            yield selector_text[start:index]
            start = index + 1
    yield selector_text[start:]


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


def _collapse_whitespace(text):
    """Return *text* with each whitespace run outside quotes collapsed to one space.

    Whitespace between a selector's tokens is insignificant -- a run of spaces
    is one descendant combinator -- and a declaration's value is normalized
    the same way. Whitespace inside a quoted string is part of its value, so
    ``[title="a  b"]`` must not become ``[title="a b"]`` (a different
    selector) and ``content: "a  b"`` must not lose a space. A backslash
    keeps the character after it inside the string, including a quote.
    """
    parts = []
    quote = None
    escaped = False
    pending_space = False
    for char in text:
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif quote is not None:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char.isspace():
            pending_space = True
            continue
        if pending_space:
            if parts:
                parts.append(" ")
            pending_space = False
        parts.append(char)
    return "".join(parts)


def parse_css(text, source=None):
    """Return the ``@define-color`` map, selector declarations and selector list.

    A selector that appears in more than one block keeps every declaration,
    with a later block's declaration replacing an earlier one, which is how the
    cascade resolves the same declaration. Comments are removed first so a
    colour named in the header cannot stand in for a rule's value.

    A malformed declaration -- no ``:``, or an empty property name or value --
    raises ``ValueError`` instead of being dropped silently, so a typo in a
    contributor-supplied sheet names itself rather than surfacing later as a
    missing key. *source* (usually the sheet's repository path) prefixes that
    diagnostic. Repeated or trailing ``;`` separators are not malformed, and a
    ``;`` inside a quoted string or parentheses is part of the value.
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
        label = _collapse_whitespace(selector_text)
        declarations = {}
        for chunk in _split_declarations(body):
            declaration = chunk.strip()
            if not declaration:
                continue
            if ":" in declaration:
                name, value = declaration.split(":", 1)
                name = _collapse_whitespace(name)
                value = _collapse_whitespace(value)
            else:
                name = value = ""
            if not name or not value:
                raise ValueError(
                    f"{source or '<stylesheet>'}: malformed declaration in "
                    f"selector {label!r}: {declaration!r} "
                    "(expected 'property: value')"
                )
            declarations[name] = value
        group = [
            _collapse_whitespace(selector)
            for selector in _split_selector_list(selector_text)
        ]
        for selector in group:
            selectors.append(selector)
            rules.setdefault(selector, {}).update(declarations)
    return definitions, rules, selectors
