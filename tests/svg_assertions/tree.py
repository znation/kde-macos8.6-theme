"""Tree traversal and attribute reading for the SVG test helpers.

The lowest layer of the ``svg_assertions`` package: it parses no file itself,
but names an element, reads its attributes, indexes elements by id and reads a
validated numeric attribute. The renderer, geometry helpers and document-safety
guards all build on it, so it imports nothing from its siblings.
"""

from __future__ import annotations

SLICE_IDS = [
    "center", "top", "bottom", "left", "right",
    "topleft", "topright", "bottomleft", "bottomright",
]

def local_name(element):
    """Return *element*'s tag without its `{namespace}` prefix.

    Each SVG declares the default SVG namespace, so ElementTree reports a tag
    as `{http://www.w3.org/2000/svg}rect`; these tests match on the local name.
    """
    return element.tag.rsplit("}", 1)[-1]

def attribute_values(tree, name):
    """Return the set of *name* values across every element in *tree*.

    An element that omits *name* contributes nothing, so the set holds exactly
    the values present in the parsed SVG. The contract tests read the artwork's
    ids, fills and strokes through this set rather than searching the raw file,
    whose comments name those values too.
    """
    return {element.get(name) for element in tree.iter() if element.get(name)}

def assert_ids_present(case, tree, names):
    """Assert every id in *names* is present in *tree*.

    The contract tests read an SVG's ids through `attribute_values` and pin
    that each id the artwork must declare is there; *case* is the calling
    ``unittest.TestCase``, so a missing id fails against the right test and
    names itself.
    """
    ids = attribute_values(tree, "id")
    for name in names:
        case.assertIn(name, ids, name)

def assert_slice_ids_present(case, tree, prefixes, hint_aliases=None):
    """Assert each state's nine-slice, margin-hint and centre ids are present.

    *prefixes* lists each state prefix in *tree* -- ``("plain", "raised",
    "sunken")`` for frame, ``["base"]`` for lineedit, ``[""]`` for an
    unprefixed SVG. Every state must carry all nine ``SLICE_IDS``; the shared
    ``hint-tile-center`` is checked once. Unless *hint_aliases* exempts it, a
    state must also carry the four margin hints KSvg reads to size the
    nine-slice. *hint_aliases* maps a prefix that declares no margin hints of
    its own to the prefix whose hints it reuses (KSvg then falls back to the
    aliased element sizes); pass ``None`` (the default) when every state
    declares its own hints. *case* is the calling ``unittest.TestCase``.
    """
    ids = attribute_values(tree, "id")
    aliases = hint_aliases or {}
    for prefix in prefixes:
        sep = "-" if prefix else ""
        for name in SLICE_IDS:
            case.assertIn(f"{prefix}{sep}{name}", ids, name)
        if prefix in aliases:
            continue
        for side in ("top", "bottom", "left", "right"):
            case.assertIn(f"{prefix}{sep}hint-{side}-margin", ids, side)
    case.assertIn("hint-tile-center", ids)

def groups_with_id(tree):
    """Yield each id-bearing `<g>` element in *tree*.

    Every nine-slice slice and focus group is a `<g id=...>`; the hints are
    separate elements rather than groups. The group-only filter lives here
    for `render_slices` and `tile_origins`, which composite and place whole
    groups; `elements_by_id` is the general id map for callers that must
    reach a non-`<g>` element.
    """
    for element in tree.iter():
        if local_name(element) == "g" and element.get("id"):
            yield element

def elements_by_id(tree):
    """Return {id: element} for every id-bearing element in *tree*.

    Unlike `groups_with_id`, this keeps non-`<g>` elements, so a caller can
    read a `<circle>` or `<path>` by id -- radiobutton's selection dot and
    hint circle, checkmarks' glyphs. The ids in these SVGs are unique; if two
    elements shared one, the later in document order would win.
    """
    return {
        element.get("id"): element
        for element in tree.iter()
        if element.get("id")
    }

def children_named(element, tag):
    """Return *element*'s direct children whose local tag is *tag*.

    A nine-slice group holds the rects and paths that paint it, and an item's
    glyphs sit directly under its group, so the artwork a test reads is one
    level down: this returns a group's own rects, paths or circles without
    re-filtering ``local_name`` at every call site.
    """
    return [child for child in element if local_name(child) == tag]

def _numeric_attribute(element, name, *, where, cast, kind, missing, invalid):
    """Return *element*'s *name* attribute text, naming it when absent or malformed.

    ElementTree hands back ``None`` for an omitted attribute and the raw text
    otherwise, so a caller that converts with ``int()``/``float()`` would
    surface a missing attribute as a bare TypeError and a malformed one as a
    bare ValueError naming neither the element nor the attribute. *where*
    names the element in the message, *cast* is the converter the text must
    satisfy, *kind* is the expected type as it reads in the error
    (``"integer"``/``"numeric"``), and *missing*/*invalid* are the contract
    clauses that follow the two failures. The raw text is returned so the
    caller decides how to convert it.
    """
    value = element.get(name)
    if value is None:
        raise ValueError(f"{where} has no {name!r} attribute: {missing}")
    try:
        cast(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{where} has a non-{kind} {name!r} of {value!r}: {invalid}"
        ) from None
    return value
