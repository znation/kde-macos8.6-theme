"""Rect and circle geometry readers for the SVG test helpers.

Turn an SVG document's id-bearing rects and its circles into numeric geometry,
naming the element and attribute in a diagnostic when one is malformed.
"""

from __future__ import annotations

from .tree import _numeric_attribute, local_name

def _rect_dimension(element, rect_id, name):
    """Return *element*'s integer *name* attribute, naming the rect when invalid.

    ElementTree hands back ``None`` for an attribute the rect omits, and the
    geometry helpers convert each value with ``int()``; a bare None would
    surface as a TypeError and a present non-integer (``x="4px"``) as a bare
    ``int()`` ValueError, neither naming which rect or attribute is malformed.
    Reject both here, naming the rect, the attribute and the value.
    """
    return _numeric_attribute(
        element, name,
        where=f"rect {rect_id!r}",
        cast=int,
        kind="integer",
        missing="an id-bearing rect must declare x, y, width and height",
        invalid=(
            "an id-bearing rect must declare x, y, width and height "
            "as integers"
        ),
    )

def rect_geometry(tree):
    """Return {id: (x, y, width, height)} for every id-bearing <rect>.

    KSvg reads a nine-slice hint rect's geometry to size the widget, so the
    ids the contract tests pin are not enough: a margin rect naming the wrong
    tile size or border lays the widget out wrong. The artwork rects in these
    nine-slice SVGs live inside id-bearing <g> elements, so the only
    id-bearing rects are the hints and this is each SVG's full hint geometry.

    Raise ValueError, naming the rect and the attribute, when an id-bearing
    rect omits one of the four or declares a non-integer value; the layout
    guards convert these values with ``int()``, so an unnamed None would read
    as a bare TypeError and a non-integer one as a bare ``int()`` ValueError.
    """
    geometry = {}
    for element in tree.iter():
        if local_name(element) == "rect" and element.get("id"):
            rect_id = element.get("id")
            geometry[rect_id] = tuple(
                _rect_dimension(element, rect_id, name)
                for name in ("x", "y", "width", "height")
            )
    return geometry

def _circle_dimension(element, name):
    """Return *element*'s *name* attribute, naming the circle when invalid.

    ElementTree hands back ``None`` for an attribute the circle omits, and
    `circle_geometry` converts each value with ``float()``; a bare None would
    surface as a TypeError and a present non-number (``r="3px"``) as a bare
    ``float()`` ValueError, neither naming which circle or attribute is
    malformed. Reject both here, naming the circle, the attribute and the
    value. An anonymous circle -- the radiobutton face and checkmarks dot
    carry no id of their own -- is named generically instead.
    """
    circle_id = element.get("id")
    where = f"circle {circle_id!r}" if circle_id else "circle"
    return _numeric_attribute(
        element, name,
        where=where,
        cast=float,
        kind="numeric",
        missing="a circle must declare cx, cy and r",
        invalid="a circle must declare cx, cy and r as numbers",
    )

def circle_geometry(element):
    """Return *element*'s circle geometry as ``(cx, cy, r)`` floats.

    KSvg reads a circle hint's centre and radius to size and place the widget,
    so a circle nudged off-centre or resized lays the widget out wrong even
    while its id and fill pass the contract tests. ElementTree hands the
    attributes back as strings; convert the three numeric ones here. Raise
    ValueError, naming the circle and the attribute, when one of the three is
    absent or not a number; the callers convert these values with ``float()``,
    so an unnamed None would read as a bare TypeError and a non-number as a
    bare ``float()`` ValueError.
    """
    return tuple(
        float(_circle_dimension(element, name))
        for name in ("cx", "cy", "r")
    )

def circle_geometry_and_fill(element):
    """Return *element*'s circle geometry followed by its ``fill`` attribute.

    The radiobutton and checkmarks tests pin a circle's centre, radius and
    fill together, because a face swapped between black and white or a dot
    nudged off-centre lays the widget out wrong even while each value alone
    passes. The fill is returned exactly as ElementTree hands it back -- the
    attribute string, or None when the circle omits it -- so a caller compares
    one tuple.
    """
    return circle_geometry(element) + (element.get("fill"),)
