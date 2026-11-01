"""Shared reader and parser for the standalone Platinum sheets.

The GTK 3, GTK 4 and Firefox sheet tests read their stylesheet into the same
``@define-color`` map, selector declarations and selector list with
:func:`parse_css`, so a change to the parsing rules is checked against all
three rather than re-derived in each. The suites that assert the shipped
``-gtk-icon-source`` glyph assets also load them through gdk-pixbuf's
sniffer-sensitive order via :func:`assert_svg_root_first`.
"""

from __future__ import annotations

import re

from support import containment
from support.repo_root import ROOT


DEFINE_COLOR = re.compile(
    r"@define-color[ \t\n\r\f]+(?P<name>[-A-Za-z0-9_]+)"
    r"[ \t\n\r\f]+(?P<value>#[0-9A-Fa-f]{6})[ \t\n\r\f]*;"
)
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
_IMPORTANT_SUFFIX = re.compile(
    r"![ \t\n\r\f]*important[ \t\n\r\f]*\Z", re.IGNORECASE | re.ASCII
)
_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def _is_important(value):
    """Return whether *value* ends in a top-level CSS priority token."""
    quote = None
    depth = 0
    suffix_start = None
    index = 0
    while index < len(value):
        char = value[index]
        if char == "\\":
            index += 2
            continue
        if quote is not None:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        elif char == "!" and depth == 0:
            suffix_start = index
        index += 1
    return suffix_start is not None and bool(_IMPORTANT_SUFFIX.fullmatch(value[suffix_start:]))


def _define_color_matches(text):
    """Yield each ``@define-color`` rule outside a quoted string.

    ``DEFINE_COLOR`` scans the whole sheet, so on its own it read a
    declaration value such as ``content: "@define-color x #123456;"`` as a
    definition: the colour was invented and its text was then removed from
    inside the string. A quoted string is a token here, as it is for the
    comment and block scanners, and a backslash keeps the character after it
    inside the string. Function contents are also tokens: definitions inside
    balanced parentheses remain part of the surrounding value.
    """
    index = 0
    quote = None
    depth = 0
    brace_depth = 0
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if quote is not None:
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            index += 1
            continue
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        elif char == "{" and depth == 0:
            brace_depth += 1
        elif char == "}" and depth == 0 and brace_depth:
            brace_depth -= 1
        elif char == "@" and depth == 0 and brace_depth == 0:
            match = DEFINE_COLOR.match(text, index)
            if match is not None:
                yield match
                index = match.end()
                continue
        index += 1



def strip_comments(text):
    """Return *text* with each ``/* ... */`` comment removed.

    The matching regular expression (``/\\*.*?\\*/`` with ``DOTALL``) is
    quadratic on a contributor-supplied sheet with many comment starts and no
    end: the lazy body rescans to the end from every start, so a 24 KB run of
    ``/*a`` takes seconds and a 1 MiB sheet stalls the suite for minutes. This
    scanner consumes each comment and scans the text between comments once,
    and keeps an unterminated ``/*`` (with the rest of the text) in place, as
    the regular expression did.

    A quoted string is a token, so ``/*`` and ``*/`` inside one are literal
    text; a backslash keeps the character after it inside the string, so an
    escaped quote does not end it early. Comment markers in a string were
    removed along with the text they surround, which rewrote the value.
    """
    parts = []
    position = 0
    index = 0
    quote = None
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if quote is not None:
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            index += 1
            continue
        if text.startswith("/*", index):
            parts.append(text[position:index])
            end = text.find("*/", index + 2)
            if end == -1:
                parts.append(text[index:])
                return "".join(parts)
            index = end + 2
            position = index
            continue
        index += 1
    parts.append(text[position:])
    return "".join(parts)


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
    search would also skip it. A brace inside a quoted string is text, not a
    block delimiter: treating it as one cut a declaration in two and reported
    the quoted text as a selector. A backslash keeps the character after it
    inside the string. Parentheses group values such as an unquoted
    ``url(...)``, whose tokens may hold braces, so a brace inside any
    ``(...)`` is text as well; an unmatched ``)`` is not tracked (as in
    ``_split_declarations``), so it cannot hide a later block delimiter.
    """
    selectors = None
    buffer = []
    quote = None
    depth = 0
    escaped = False
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
        elif char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        elif char == "{":
            if not depth:
                candidate = "".join(buffer)
                buffer = []
                selectors = candidate or None
                continue
        elif char == "}":
            if not depth:
                if selectors is not None:
                    yield selectors, "".join(buffer)
                selectors = None
                buffer = []
                continue
        buffer.append(char)


def _split_declarations(body):
    """Yield *body*'s declarations, split on ``;`` outside quotes, ``()`` and ``[]``.

    A quoted string and a ``url(...)`` value may both carry a semicolon that is
    part of the value rather than a separator. Splitting on every semicolon cut
    ``url("data:image/svg+xml;base64,...")`` in two and reported the second
    half as malformed.
    """
    declaration = []
    quote = None
    depth = 0
    bracket_depth = 0
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
        elif char == "[":
            bracket_depth += 1
        elif char == "]" and bracket_depth:
            bracket_depth -= 1
        elif char == ";" and not depth and not bracket_depth:
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
        elif char in " \t\n\r\f":
            pending_space = True
            continue
        if pending_space:
            if parts:
                parts.append(" ")
            pending_space = False
        parts.append(char)
    return "".join(parts)


def _split_property_value(declaration):
    """Split at the first colon not escaped by a backslash."""
    index = 0
    while index < len(declaration):
        char = declaration[index]
        if char == "\\":
            index += 2
            continue
        if char == ":":
            return declaration[:index], declaration[index + 1:]
        index += 1
    return None


def assert_svg_root_first(test, path):
    """Assert *path* puts its SVG root before any provenance comment.

    GTK loads a ``-gtk-icon-source`` SVG through gdk-pixbuf, whose sniffer
    only recognizes a file whose ``<svg`` root sits near the start; a comment
    before the root leaves the glyph blank. An XML declaration is optional
    and accepted, but the provenance comment belongs inside the root. The
    asset is contributor-supplied, and ``assertRegex`` echoes the text it was
    given when it fails, so the file is read through the shared guarded
    reader: a checked-in symlink that escapes the repository is refused
    before its private target's text reaches the diagnostic.
    """
    test.assertRegex(
        read_theme_text(path),
        r"^\s*(?:<\?xml[^>]*\?>\s*)?<svg\b",
    )


def parse_css(text, source=None):
    """Return the ``@define-color`` map, selector declarations and selector list.

    A selector that appears in more than one block keeps every declaration;
    important declarations beat normal ones, and later declarations win ties.
    Comments are removed first so a
    colour named in the header cannot stand in for a rule's value, and a
    ``@define-color`` inside a quoted value is text rather than a definition
    (and is left in the value), as it is for the other scanners.

    A malformed declaration -- no ``:``, or an empty property name or value --
    raises ``ValueError`` instead of being dropped silently, so a typo in a
    contributor-supplied sheet names itself rather than surfacing later as a
    missing key. *source* (usually the sheet's repository path) prefixes that
    diagnostic. Repeated or trailing ``;`` separators are not malformed, and a
    ``;`` inside a quoted string or parentheses is part of the value.
    """
    text = strip_comments(text)
    definitions = {}
    without_definitions = []
    position = 0
    for match in _define_color_matches(text):
        definitions[match.group("name")] = match.group("value")
        without_definitions.append(text[position:match.start()])
        position = match.end()
    without_definitions.append(text[position:])
    without_definitions = "".join(without_definitions)
    rules = {}
    rule_priorities = {}
    selectors = []
    for selector_text, body in _rule_blocks(without_definitions):
        label = _collapse_whitespace(selector_text)
        declarations = []
        for chunk in _split_declarations(body):
            declaration = chunk.strip(' \t\n\r\f')
            if not declaration:
                continue
            split = _split_property_value(chunk)
            if split is not None:
                name, value = split
                name = _collapse_whitespace(name)
                if not name.startswith("--"):
                    name = name.translate(_ASCII_LOWER)
                value = _collapse_whitespace(value)
            else:
                name = value = ""
            if not name or not value:
                raise ValueError(
                    f"{source or '<stylesheet>'}: malformed declaration in "
                    f"selector {label!r}: {declaration!r} "
                    "(expected 'property: value')"
                )
            declarations.append((name, value, _is_important(value)))
        group = [
            _collapse_whitespace(selector)
            for selector in _split_selector_list(selector_text)
        ]
        for selector in group:
            selectors.append(selector)
            selector_rules = rules.setdefault(selector, {})
            priorities = rule_priorities.setdefault(selector, {})
            for name, value, important in declarations:
                if important or not priorities.get(name, False):
                    selector_rules[name] = value
                    priorities[name] = important
    return definitions, rules, selectors
