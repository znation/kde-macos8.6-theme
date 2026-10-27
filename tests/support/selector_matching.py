"""Minimal CSS selector matching for test-side element fixtures.

The sheet tests usually assert a rule's selector text and declarations. A
selector can still be too broad for the elements it is meant to paint, so a
scope test builds a small element tree and asks this module whether the sheet's
selector would match each representative element.

Only the subset the sheet's scope tests use is supported: descendant and
child (``>``) combinators separating compound selectors made of an element
name, ``#id``, ``.class``, ``[attribute]``/``[attribute="value"]``, ``:hover``
and ``:not(...)`` (whose argument may itself be a single selector). A sibling
combinator (``+`` or ``~``), a selector list (a comma outside an attribute
selector, as in ``:not(.a, .b)`` or the top-level ``.a, .b``) or any other
pseudo-class or pseudo-element is outside that subset and makes its selector
match no element -- including a pseudo-class inside ``:not(...)``, which must
not be read as false and invert the negation into a match for every element.
An unbalanced parenthesis is malformed, outside the subset, and matches no
element: it cannot be paired with a combinator step, so it must not crash the
matcher or be read as part of a compound. A combinator with no compound on one
side (leading, trailing or doubled) is malformed in the same way and matches
nothing. An element
is a mapping with ``tag``, ``id``, ``classes``, ``attrs``, ``hover`` and
``parent`` keys; ``parent`` is another element or ``None``. ``:hover`` is true
only when the element's ``hover`` flag is true. Text inside a quoted attribute
value is literal: ``[title=":hover"]`` is an attribute test, not a hover test.
"""

from __future__ import annotations

import re


_ID = re.compile(r"#([-\w]+)")
_CLASS = re.compile(r"\.([-\w]+)")
_TAG = re.compile(r"^([-\w]+|\*)")
_HOVER = re.compile(r":hover(?![-\w])")
_ATTRIBUTE = re.compile(
    r"\[([-\w]+)(?:=(?:\"([^\"]*)\"|'([^']*)'|([^\]]+)))?\]"
)


def element(tag, identifier=None, classes=(), attrs=None, hover=False,
            parent=None):
    """Build one fixture element with the keys :func:`matches` reads."""
    return {
        "tag": tag,
        "id": identifier,
        "classes": set(classes),
        "attrs": dict(attrs or {}),
        "hover": hover,
        "parent": parent,
    }


def _attribute_spans(compound):
    """Return the spans of *compound*'s own ``[...]`` selectors.

    A bracket inside a ``:not(...)`` argument belongs to the negated selector
    and a bracket inside a quoted value belongs to the value, so neither is
    the compound's own attribute. Later callers blank these spans before
    looking for pseudo-classes: ``[title=":hover"]`` must not require the
    hover flag, and ``[title="a:b"]`` must not look unsupported.
    """
    spans = []
    depth = 0
    parentheses = 0
    quote = None
    start = None
    for index, char in enumerate(compound):
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
            continue
        if char == "(":
            parentheses += 1
            continue
        if char == ")":
            parentheses = max(0, parentheses - 1)
            continue
        if parentheses:
            continue
        if char == "[":
            if depth == 0:
                start = index
            depth += 1
        elif char == "]":
            if depth:
                depth -= 1
                if depth == 0 and start is not None:
                    spans.append((start, index + 1))
                    start = None
    return spans


def _mask_attributes(compound, spans):
    """Return *compound* with each attribute span replaced by ``[]``."""
    if not spans:
        return compound
    parts = []
    position = 0
    for start, end in spans:
        parts.append(compound[position:start])
        parts.append("[]")
        position = end
    parts.append(compound[position:])
    return "".join(parts)


def _blank_spans(compound, spans):
    """Return *compound* with each ``(start, end, ...)`` span removed."""
    if not spans:
        return compound
    parts = []
    position = 0
    for start, end, *_ in spans:
        parts.append(compound[position:start])
        position = end
    parts.append(compound[position:])
    return "".join(parts)


def _not_spans(compound):
    """Return ``(start, end, argument)`` for each ``:not(...)`` in *compound*.

    Quoted text and attribute selectors are skipped, so a ``:not(`` inside
    ``[title=":not(.a)"]`` is part of the value, not a negation. Parentheses
    are balanced, so a quoted ``)`` inside the argument does not end it early.
    """
    spans = []
    index = 0
    bracket_depth = 0
    quote = None
    while index < len(compound):
        char = compound[index]
        if quote is not None:
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            index += 1
            continue
        if char == "[":
            bracket_depth += 1
            index += 1
            continue
        if char == "]":
            bracket_depth = max(0, bracket_depth - 1)
            index += 1
            continue
        if bracket_depth or not compound.startswith(":not(", index):
            index += 1
            continue
        start = index
        depth = 1
        end = index + len(":not(")
        inner_quote = None
        inner_bracket = 0
        while end < len(compound) and depth:
            char = compound[end]
            if inner_quote is not None:
                if char == inner_quote:
                    inner_quote = None
            elif char in "\"'":
                inner_quote = char
            elif char == "[":
                inner_bracket += 1
            elif char == "]":
                inner_bracket = max(0, inner_bracket - 1)
            elif not inner_bracket:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
            end += 1
        if depth:
            index += len(":not(")
            continue
        spans.append((start, end, compound[start + len(":not("):end - 1]))
        index = end
    return spans


def _compound_matches(compound, element):
    spans = _attribute_spans(compound)
    attributes = [compound[start:end] for start, end in spans]
    compound = _mask_attributes(compound, spans)
    negations = _not_spans(compound)
    for _, _, negated in negations:
        if matches(negated, element):
            return False
    compound = _blank_spans(compound, negations)
    if _HOVER.search(compound):
        if not element["hover"]:
            return False
        compound = _HOVER.sub("", compound)
    if ":" in compound:
        return False
    tag = _TAG.match(compound)
    if tag and tag.group(1) != "*" and tag.group(1) != element["tag"]:
        return False
    for identifier in _ID.findall(compound):
        if identifier != element["id"]:
            return False
    for class_name in _CLASS.findall(compound):
        if class_name not in element["classes"]:
            return False
    for attribute in attributes:
        for match in _ATTRIBUTE.finditer(attribute):
            name, double_quoted, single_quoted, unquoted = match.groups()
            if name not in element["attrs"]:
                return False
            # An empty quoted value is a value test, not presence: test the
            # groups against None rather than using ``or``, which made
            # ``[title=""]`` match any element carrying ``title``.
            if double_quoted is not None:
                value = double_quoted
            elif single_quoted is not None:
                value = single_quoted
            else:
                value = unquoted
            if value is not None and element["attrs"][name] != value:
                return False
    return True


def _split_selector(selector):
    """Split *selector* into compounds and the combinators between them.

    Whitespace outside parentheses and brackets separates compounds with a
    descendant combinator; ``>`` separates them with a child combinator, and
    ``+`` and ``~`` are kept as their own (unsupported) combinators so a
    sibling selector cannot be read as a chain of compounds. Whitespace on
    either side of a combinator belongs to it rather than adding a descendant
    step of its own.

    Return ``(compounds, combinators, misplaced)``. *misplaced* is true when a
    combinator has no compound on one side (leading, trailing or doubled), so
    the selector cannot be paired into combinator steps.
    """
    compounds = []
    combinators = []
    misplaced = False
    current = []
    pending = None
    depth = 0
    quote = None
    for char in selector:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
            current.append(char)
        elif char in "([":
            if not current and compounds and pending is not None:
                combinators.append(pending)
                pending = None
            depth += 1
            current.append(char)
        elif char in ")]":
            depth -= 1
            current.append(char)
        elif depth == 0 and char in ">+~":
            if current:
                compounds.append("".join(current))
                current = []
            if compounds and pending not in (">", "+", "~"):
                pending = char
            else:
                misplaced = True
        elif depth == 0 and char.isspace():
            if current:
                compounds.append("".join(current))
                current = []
                if pending is None:
                    pending = " "
        else:
            if not current and compounds and pending is not None:
                combinators.append(pending)
                pending = None
            current.append(char)
    if current:
        compounds.append("".join(current))
    if pending in (">", "+", "~"):
        misplaced = True
    return compounds, combinators, misplaced


def _has_selector_list_comma(selector):
    """Return whether *selector* holds a comma outside attribute brackets.

    A comma outside attribute brackets separates a selector list, so
    ``:not(.a, .b)`` negates either class rather than naming the descendant
    chain ``.a .b``. :func:`_split_selector` has no list combinator, so such a
    selector is outside the supported subset and must match nothing. A comma
    inside ``[title="a,b"]`` is inside the brackets (and quotes) and stays
    supported.
    """
    quote = None
    bracket_depth = 0
    for char in selector:
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth = max(0, bracket_depth - 1)
        elif char == "," and not bracket_depth:
            return True
    return False


def _parentheses_are_balanced(selector):
    """Return whether *selector*'s parentheses all close in order.

    Parentheses inside a quoted value or an attribute selector are text, not
    grouping, so ``[title="("]`` is balanced. An unmatched ``(`` or ``)``
    makes the selector malformed; :func:`_split_selector` cannot pair it with
    a combinator step, which used to crash or read the text as a compound.
    """
    quote = None
    bracket_depth = 0
    depth = 0
    for char in selector:
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth = max(0, bracket_depth - 1)
        elif not bracket_depth:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    return False
    return depth == 0


def _compound_is_supported(compound):
    """Return whether *compound* uses only the matcher's supported subset.

    ``:hover`` and a flat ``:not(...)`` are supported; every other
    pseudo-class or pseudo-element is not, wherever it appears. The negated
    selectors are checked recursively because :func:`_compound_matches` strips
    them before testing for a leftover ``:``: an unsupported pseudo-class
    inside ``:not(...)`` would otherwise be read as false, and negating a gap
    would silently turn the selector into one that matches every element.
    A bracket or quote left outside the attribute spans is malformed and is
    rejected rather than dropped, which would leave a universal match.
    """
    negations = _not_spans(compound)
    remainder = _blank_spans(compound, negations)
    spans = _attribute_spans(remainder)
    if any(char in "[]\"'" for char in _blank_spans(remainder, spans)):
        return False
    for start, end in spans:
        if not _ATTRIBUTE.fullmatch(remainder[start:end]):
            return False
    compound = _mask_attributes(remainder, spans)
    compound = _HOVER.sub("", compound)
    if ":" in compound:
        return False
    return all(
        not _not_spans(negated_selector)
        and _selector_is_supported(negated_selector)
        for _, _, negated_selector in negations
    )


def _selector_is_supported(selector):
    """Return whether *selector* stays inside the matcher's supported subset."""
    if _has_selector_list_comma(selector) or not _parentheses_are_balanced(
        selector
    ):
        return False
    compounds, combinators, misplaced = _split_selector(selector)
    return (
        bool(compounds)
        and not misplaced
        and all(combinator in (" ", ">") for combinator in combinators)
        and all(_compound_is_supported(compound) for compound in compounds)
    )


def matches(selector, element):
    """Return True when *selector* matches *element* in its fixture tree.

    A selector using a sibling combinator (``+``/``~``), a selector list (a
    comma outside an attribute selector), an unsupported pseudo-class (even
    inside ``:not(...)``) or a malformed combinator or parenthesis is outside
    the supported subset and matches nothing, so its over-broad reading cannot
    pass a scope assertion.
    """
    compounds, combinators, misplaced = _split_selector(selector)
    if (
        not compounds
        or misplaced
        or _has_selector_list_comma(selector)
        or not _parentheses_are_balanced(selector)
    ):
        return False
    if any(combinator not in (" ", ">") for combinator in combinators):
        return False
    if not all(_compound_is_supported(compound) for compound in compounds):
        return False

    def match_from(index, current):
        if not _compound_matches(compounds[index], current):
            return False
        if index == 0:
            return True
        parent = current["parent"]
        if combinators[index - 1] == ">":
            return parent is not None and match_from(index - 1, parent)
        while parent is not None:
            if match_from(index - 1, parent):
                return True
            parent = parent["parent"]
        return False

    return match_from(len(compounds) - 1, element)
