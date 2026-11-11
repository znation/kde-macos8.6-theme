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
_CSS_WHITESPACE = " \t\n\r\f"
_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def _hex_digits_end(text, index):
    """Return the index past the hex digits opening at *index*, or ``None``.

    At most six hexadecimal digits are consumed from *index* onward.
    """
    end = index
    while end < len(text) and end - index < 6 and text[end] in "0123456789abcdefABCDEF":
        end += 1
    return None if end == index else end


def _decode_css_escape(text, index):
    """Decode the CSS escape whose backslash sits at *index* in *text*.

    Returns ``(decoded, end)``: *decoded* is the escaped character and *end*
    the index past it, where a hex escape's digits may be followed by the
    one whitespace character that belongs to the escape (an escaped ``\r\n``
    pair counts as one). An escape that is not a hex escape decodes the
    character after the backslash itself. ``None`` stands for a malformed
    escape: a backslash at the end of the text or one escaping a newline.
    """
    index += 1
    if index == len(text) or text[index] in "\n\r\f":
        return None
    digits_end = _hex_digits_end(text, index)
    if digits_end is None:
        return text[index], index + 1
    codepoint = int(text[index:digits_end], 16)
    decoded = "\ufffd" if (codepoint == 0 or codepoint > 0x10FFFF
                           or 0xD800 <= codepoint <= 0xDFFF) else chr(codepoint)
    return decoded, _whitespace_end(text, digits_end)


def _important_suffix_matches(suffix):
    """Decode the priority identifier's CSS escapes and compare its spelling."""
    if not suffix.startswith("!"):
        return False
    index = 1
    while index < len(suffix) and suffix[index] in _CSS_WHITESPACE:
        index += 1
    decoded = []
    while index < len(suffix):
        char = suffix[index]
        if char in _CSS_WHITESPACE:
            break
        if char != "\\":
            decoded.append(char)
            index += 1
            continue
        escape = _decode_css_escape(suffix, index)
        if escape is None:
            return False
        decoded_char, index = escape
        decoded.append(decoded_char)
    while index < len(suffix) and suffix[index] in _CSS_WHITESPACE:
        index += 1
    return index == len(suffix) and "".join(decoded).translate(_ASCII_LOWER) == "important"


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
    return suffix_start is not None and _important_suffix_matches(value[suffix_start:])


def _define_color_matches(text):
    """Yield each ``@define-color`` rule outside a quoted string.

    ``DEFINE_COLOR`` scans the whole sheet, so on its own it read a
    declaration value such as ``content: "@define-color x #123456;"`` as a
    definition: the colour was invented and its text was then removed from
    inside the string. A quoted string is a token here, as it is for the
    comment and block scanners, and a backslash keeps the character after it
    inside the string. Function contents are also tokens: definitions inside
    balanced parentheses remain part of the surrounding value, and so are
    definitions inside a rule block: unquoted, unescaped braces outside
    parentheses track nonnegative block depth, so a stray ``}`` cannot hide
    a following top-level definition.
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



def _unquoted_url_end(text, index):
    """Return the index past an unquoted ``url(...)`` body at *index*.

    *index* names the opening ``u``. Whitespace after ``url(`` and the body
    up to its closing parenthesis belong to the token, and the returned
    index is past the ``)`` (or the end of the text when no ``)`` closes
    the body). A body opening with a quote is not a match: the caller's
    string tracking keeps the quotes and their contents literal, as it
    does for any other quoted string. An escaped character is two
    characters of the body and cannot close it.
    """
    url_start = index + 4
    while url_start < len(text) and text[url_start] in " \t\n\r\f":
        url_start += 1
    if url_start >= len(text) or text[url_start] in "\"'":
        return None
    position = url_start
    while position < len(text):
        if text[position] == "\\":
            position += 2
        elif text[position] == ")":
            return position + 1
        else:
            position += 1
    return position


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
        if char in "uU" and (index == 0 or not (
            text[index - 1].isalnum() or text[index - 1] in "_-\\"
            or not text[index - 1].isascii()
        )) and text[index:index + 3].translate(_ASCII_LOWER) == "url" and index + 3 < len(text) and text[index + 3] == "(":
            end = _unquoted_url_end(text, index)
            if end is not None:
                index = end
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
    inside the string. Parentheses group values such as unquoted ``url(...)``
    and square brackets group custom-property tokens, so braces inside either
    group are text. Unmatched closing parentheses and brackets are not tracked
    (as in ``_split_declarations``), so neither can hide a later delimiter.
    """
    selectors = None
    buffer = []
    quote = None
    depth = 0
    bracket_depth = 0
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
        elif char == "[":
            bracket_depth += 1
        elif char == "]" and bracket_depth:
            bracket_depth -= 1
        elif char == "{" and not depth and not bracket_depth:
            selectors = "".join(buffer) or None
            buffer = []
            continue
        elif char == "}" and not depth and not bracket_depth:
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


def _whitespace_end(text, index):
    """Return the index past the one whitespace character at *index*, if any.

    A hex escape's digits may be followed by one whitespace character that
    belongs to the escape; an escaped ``\r\n`` pair counts as one.
    """
    if index >= len(text) or text[index] not in _CSS_WHITESPACE:
        return index
    if text[index] == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
        return index + 2
    return index + 1


def _hex_escape_end(text, index):
    """Return the index past the hex escape opening at *index*, or ``None``.

    At most six hexadecimal digits follow the backslash, and one whitespace
    character after the digits belongs to the escape (an escaped ``\r\n``
    pair counts as one), so the escaped text can be copied whole. Fewer
    than one digit is no escape, and the caller then treats the backslash
    by its own rules.
    """
    digits_end = _hex_digits_end(text, index + 1)
    if digits_end is None:
        return None
    return _whitespace_end(text, digits_end)


def _append_text(parts, text, pending_space, chunk):
    """Append *chunk* to *parts*, collapsing a pending space before it.

    A pending space is dropped before the first chunk and kept as one
    space between chunks, so a run of whitespace outside quotes collapses
    to one space. Returns ``False`` because the chunk consumes the pending
    space.
    """
    if pending_space and parts:
        parts.append(" ")
    parts.append(chunk)
    return False


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
    pending_space = False
    index = 0
    while index < len(text):
        char = text[index]
        if quote is None and char == "\\":
            end = _hex_escape_end(text, index)
            if end is not None:
                pending_space = _append_text(parts, text, pending_space,
                                             text[index:end])
                index = end
                continue
        if quote is None and char in "\"'":
            quote = char
        elif quote is not None:
            if char == "\\" and index + 1 < len(text):
                pending_space = _append_text(parts, text, pending_space,
                                             text[index:index + 2])
                index += 2
                continue
            if char == quote:
                quote = None
        elif char == "\\":
            pending_space = _append_text(parts, text, pending_space, char)
            index += 1
            if index < len(text):
                parts.append(text[index])
                index += 1
            continue
        elif char in " \t\n\r\f":
            pending_space = True
            index += 1
            continue
        if pending_space:
            if parts:
                parts.append(" ")
            pending_space = False
        parts.append(char)
        index += 1
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


def _canonicalize_declaration_name(name):
    """Decode CSS escapes in property names; fold ASCII case for ordinary names only."""
    decoded = []
    index = 0
    while index < len(name):
        char = name[index]
        if char != "\\":
            decoded.append(char)
            index += 1
            continue
        escape = _decode_css_escape(name, index)
        if escape is None:
            return name
        decoded_char, index = escape
        decoded.append(decoded_char)
    canonical = "".join(decoded)
    if canonical.startswith("--"):
        return canonical
    return canonical.translate(_ASCII_LOWER)


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


def _parsed_declarations(body, label, source):
    """Return *body*'s ``(name, value, important)`` declarations.

    A malformed declaration -- no unescaped ``:``, or an empty property name
    or value (except an empty value on a named custom property) -- raises
    ``ValueError`` instead of being dropped silently. Empty custom-property
    values are retained as empty strings. A typo in a contributor-supplied
    sheet names itself rather than surfacing later as a missing key.
    """
    declarations = []
    for chunk in _split_declarations(body):
        declaration = chunk.strip(' \t\n\r\f')
        if not declaration:
            continue
        split = _split_property_value(chunk)
        if split is not None:
            name, value = split
            name = _canonicalize_declaration_name(_collapse_whitespace(name))
            value = _collapse_whitespace(value)
        else:
            name = value = ""
        if not name or (not value and not (name.startswith("--") and len(name) > 2)):
            raise ValueError(
                f"{source or '<stylesheet>'}: malformed declaration in "
                f"selector {label!r}: {declaration!r} "
                "(expected 'property: value')"
            )
        declarations.append((name, value, _is_important(value)))
    return declarations


def _store_group_rules(rules, priorities, declarations):
    """Store *declarations* under one selector, important beating normal.

    Later declarations win ties: an important declaration overwrites a normal
    one, and a later important one overwrites an earlier important one.
    """
    for name, value, important in declarations:
        if important or not priorities.get(name, False):
            rules[name] = value
            priorities[name] = important


def parse_css(text, source=None):
    """Return the ``@define-color`` map, selector declarations and selector list.

    A selector that appears in more than one block keeps every declaration;
    important declarations beat normal ones, and later declarations win ties.
    Comments are removed first so a
    colour named in the header cannot stand in for a rule's value, and a
    ``@define-color`` inside a quoted value is text rather than a definition
    (and is left in the value), as it is for the other scanners.

    A malformed declaration -- no unescaped ``:``, or an empty property name
    or value (except an empty value on a named custom property) -- raises
    ``ValueError`` instead of being dropped silently. Empty custom-property
    values are retained as empty strings. A typo in a contributor-supplied
    sheet names itself rather than surfacing later as a missing key. *source*
    (usually the sheet's repository path) prefixes that diagnostic. Repeated
    or trailing ``;`` separators are not malformed, and a ``;`` inside a
    quoted string or parentheses is part of the value.
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
        declarations = _parsed_declarations(body, label, source)
        group = [
            _collapse_whitespace(selector)
            for selector in _split_selector_list(selector_text)
        ]
        for selector in group:
            selectors.append(selector)
            selector_rules = rules.setdefault(selector, {})
            priorities = rule_priorities.setdefault(selector, {})
            _store_group_rules(selector_rules, priorities, declarations)
    return definitions, rules, selectors


def inline_link_state_selectors(roots, state="", prefix=""):
    """Expand inline-link selectors across base, hover and active states.

    Each root of *roots* is kept in order and becomes ``prefix + root
    + state + suffix`` for the base, ``:hover`` and ``:active`` suffixes.
    The GTK 3 and GTK 4 inline-link suites' root-built selector sets go
    through this helper: the GTK 4 suite passes the state inside its
    roots and leaves *state* untouched, the GTK 3 suite passes the focus
    or backdrop state separately and prefixes the ancestor ``:selected``
    forms with ``":selected "``.
    """
    return tuple(
        prefix + root + state + suffix
        for root in roots
        for suffix in ("", ":hover", ":active")
    )
