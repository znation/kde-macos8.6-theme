"""Minimal CSS selector matching for test-side element fixtures.

The sheet tests usually assert a rule's selector text and declarations. A
selector can still be too broad for the elements it is meant to paint, so a
scope test builds a small element tree and asks this module whether the sheet's
selector would match each representative element.

Only the subset the sheet's scope tests use is supported: descendant
combinators separating compound selectors made of an element name, ``#id``,
``.class``, ``[attribute]``/``[attribute="value"]``, ``:hover`` and
``:not(...)`` (whose argument may itself be a descendant selector). An element
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


def _descendant_compounds(selector):
    """Split *selector* at whitespace outside parentheses and brackets."""
    compounds = []
    current = []
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
            depth += 1
            current.append(char)
        elif char in ")]":
            depth -= 1
            current.append(char)
        elif char.isspace() and not depth:
            if current:
                compounds.append("".join(current))
                current = []
        else:
            current.append(char)
    if current:
        compounds.append("".join(current))
    return compounds


def matches(selector, element):
    """Return True when *selector* matches *element* in its fixture tree."""
    compounds = _descendant_compounds(selector)
    if not compounds or not _compound_matches(compounds[-1], element):
        return False
    ancestor = element["parent"]
    for compound in reversed(compounds[:-1]):
        while ancestor is not None and not _compound_matches(compound, ancestor):
            ancestor = ancestor["parent"]
        if ancestor is None:
            return False
        ancestor = ancestor["parent"]
    return True
