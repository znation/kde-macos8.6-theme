"""Minimal CSS selector matching for test-side element fixtures.

The sheet tests usually assert a rule's selector text and declarations. A
selector can still be too broad for the elements it is meant to paint, so a
scope test builds a small element tree and asks this module whether the sheet's
selector would match each representative element.

Only the subset the sheet's scope tests use is supported: descendant and
child (``>``) combinators separating compound selectors made of an element
name, ``#id``, ``.class``, ``[attribute]``/``[attribute="value"]``, ``:hover``
and ``:not(...)`` (whose argument may itself be a selector). A sibling
combinator (``+`` or ``~``) or any other pseudo-class or pseudo-element is
outside that subset and makes its selector match no element -- including a
pseudo-class inside ``:not(...)``, which must not be read as false and invert
the negation into a match for every element. An element
is a mapping with ``tag``, ``id``, ``classes``, ``attrs``, ``hover`` and
``parent`` keys; ``parent`` is another element or ``None``. ``:hover`` is true
only when the element's ``hover`` flag is true.
"""

from __future__ import annotations

import re


_ID = re.compile(r"#([-\w]+)")
_CLASS = re.compile(r"\.([-\w]+)")
_TAG = re.compile(r"^([-\w]+|\*)")
_NOT = re.compile(r":not\(([^)]*)\)")
_HOVER = re.compile(r":hover(?![-\w])")
_ATTRIBUTE = re.compile(
    r"\[([-\w]+)(?:=(?:\"([^\"]*)\"|'([^']*)'|([^\]]+)))?\]"
)


def _compound_matches(compound, element):
    for negated in _NOT.findall(compound):
        if matches(negated, element):
            return False
    compound = _NOT.sub("", compound)
    if ":hover" in compound:
        if not element["hover"]:
            return False
        compound = compound.replace(":hover", "")
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
    for match in _ATTRIBUTE.finditer(compound):
        name, double_quoted, single_quoted, unquoted = match.groups()
        if name not in element["attrs"]:
            return False
        value = double_quoted or single_quoted or unquoted
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
    """
    compounds = []
    combinators = []
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
            if compounds:
                pending = char
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
    return compounds, combinators


def _compound_is_supported(compound):
    """Return whether *compound* uses only the matcher's supported subset.

    ``:hover`` and a flat ``:not(...)`` are supported; every other
    pseudo-class or pseudo-element is not, wherever it appears. The negated
    selectors are checked recursively because :func:`_compound_matches` strips
    them before testing for a leftover ``:``: an unsupported pseudo-class
    inside ``:not(...)`` would otherwise be read as false, and negating a gap
    would silently turn the selector into one that matches every element.
    """
    negated_selectors = _NOT.findall(compound)
    remainder = _NOT.sub("", compound)
    remainder = _HOVER.sub("", remainder)
    if ":" in remainder:
        return False
    return all(
        _selector_is_supported(negated_selector)
        for negated_selector in negated_selectors
    )


def _selector_is_supported(selector):
    """Return whether *selector* stays inside the matcher's supported subset."""
    compounds, combinators = _split_selector(selector)
    return (
        bool(compounds)
        and all(combinator in (" ", ">") for combinator in combinators)
        and all(_compound_is_supported(compound) for compound in compounds)
    )


def matches(selector, element):
    """Return True when *selector* matches *element* in its fixture tree.

    A selector using a sibling combinator (``+``/``~``) or an unsupported
    pseudo-class (even inside ``:not(...)``) is outside the supported subset
    and matches nothing, so its over-broad reading cannot pass a scope
    assertion.
    """
    compounds, combinators = _split_selector(selector)
    if not compounds:
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
