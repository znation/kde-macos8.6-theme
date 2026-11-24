"""Drawing-element helpers shared by the per-family pin registries.

The page tuples are the page outline, white face and folded corner the
blank-document names draw whole and the other page-backed pins spread as
their prefix; the trash body is the lid and can the empty and full Trash
draw in common. Each family module spreads these prefixes into its pins,
so a shared-art edit lands in one place.
"""


def _shape(tag, **attributes):
    """Return one expected drawing element: its tag and its attributes."""
    return (tag, attributes)


# The page: the generic document's first three drawing elements (the black
# outline, the white page and the folded corner), one tuple per size. The
# mimetypes registry is the only user: it maps the three blank-document
# names straight onto the tuple and spreads it as the prefix of the other
# nine page-backed pins per size, so a page edit lands in one place and
# every page-backed pin stays in step; the pins test in
# ``test_icon_theme_geometry`` still compares each pin with its shipped
# file element by element.
_PAGE_16 = (
    _shape("path", d="M3 1 h7 l3 3 v10 H3 Z", fill="#000000"),
    _shape("path", d="M4 2 h5 l3 3 v8 H4 Z", fill="#FFFFFF"),
    _shape("path", d="M9 2 L12 2 L12 5 Z", fill="#DDDDDD"),
)
_PAGE_22 = (
    _shape("path", d="M4 1 h10 l4 4 v15 H4 Z", fill="#000000"),
    _shape("path", d="M5 2 h8 l4 4 v13 H5 Z", fill="#FFFFFF"),
    _shape("path", d="M13 2 L17 2 L17 6 Z", fill="#DDDDDD"),
)
_PAGE_32 = (
    _shape("path", d="M6 3 h14 l6 6 v20 H6 Z", fill="#000000"),
    _shape("path", d="M7 4 h12 l6 6 v18 H7 Z", fill="#FFFFFF"),
    _shape("path", d="M19 4 L25 4 L25 10 Z", fill="#DDDDDD"),
)

def _raised_panel(x, y, w, h):
    """Return the six shapes of one raised panel: the recipe the devices
    pins repeat for every case, bezel and plate they draw. A black outline
    rect at ``x, y, w, h`` carries a ``#DDDDDD`` face one pixel in, the
    face's top and left rows stay ``#FFFFFF`` and its bottom and right rows
    ``#999999``, in that element order; spreading the returned tuple into a
    pin keeps the pin's element list exactly what the shipped SVG draws.
    Panels whose bevel deviates from this recipe (thicker highlight rows,
    different shadow geometry) keep their explicit shapes.
    """
    return (
        _shape("rect", x=str(x), y=str(y), width=str(w), height=str(h), fill="#000000"),
        _shape("rect", x=str(x + 1), y=str(y + 1), width=str(w - 2), height=str(h - 2), fill="#DDDDDD"),
        _shape("rect", x=str(x + 1), y=str(y + 1), width=str(w - 2), height="1", fill="#FFFFFF"),
        _shape("rect", x=str(x + 1), y=str(y + 1), width="1", height=str(h - 2), fill="#FFFFFF"),
        _shape("rect", x=str(x + 1), y=str(y + h - 2), width=str(w - 2), height="1", fill="#999999"),
        _shape("rect", x=str(x + w - 2), y=str(y + 1), width="1", height=str(h - 2), fill="#999999"),
    )


# The trash body: the lid and can the empty and full Trash draw in common,
# one tuple per size. Each Trash pin below is its own head (the empty one's
# lid-top rects, the full one's waste-bag paths) followed by this body, so a
# body edit lands in one place per size and both pins stay in step; the
# pins test in ``test_icon_theme_geometry`` still compares each pin with
# its shipped file element by element.
_TRASH_BODY_32 = (
    _shape("rect", x="6", y="8", width="20", height="5", fill="#000000"),
    _shape("rect", x="7", y="9", width="18", height="4", fill="#DDDDDD"),
    _shape("rect", x="7", y="9", width="18", height="1", fill="#FFFFFF"),
    _shape("rect", x="7", y="12", width="18", height="1", fill="#999999"),
    _shape("path", d="M9 13 h14 l-2 16 H11 Z", fill="#000000"),
    _shape("path", d="M10 14 h12 l-2 14 H12 Z", fill="#DDDDDD"),
    _shape("rect", x="13", y="16", width="1", height="10", fill="#999999"),
    _shape("rect", x="14", y="16", width="1", height="10", fill="#FFFFFF"),
    _shape("rect", x="17", y="16", width="1", height="10", fill="#999999"),
    _shape("rect", x="18", y="16", width="1", height="10", fill="#FFFFFF"),
)
_TRASH_BODY_22 = (
    _shape("rect", x="4", y="4", width="14", height="4", fill="#000000"),
    _shape("rect", x="5", y="5", width="12", height="3", fill="#DDDDDD"),
    _shape("rect", x="5", y="5", width="12", height="1", fill="#FFFFFF"),
    _shape("rect", x="5", y="7", width="12", height="1", fill="#999999"),
    _shape("path", d="M6 8 h10 l-1 12 H7 Z", fill="#000000"),
    _shape("path", d="M7 9 h8 l-1 10 H8 Z", fill="#DDDDDD"),
    _shape("rect", x="9", y="11", width="1", height="8", fill="#999999"),
    _shape("rect", x="10", y="11", width="1", height="8", fill="#FFFFFF"),
    _shape("rect", x="12", y="11", width="1", height="8", fill="#999999"),
    _shape("rect", x="13", y="11", width="1", height="8", fill="#FFFFFF"),
)
_TRASH_BODY_16 = (
    _shape("rect", x="3", y="3", width="10", height="3", fill="#000000"),
    _shape("rect", x="4", y="4", width="8", height="2", fill="#DDDDDD"),
    _shape("rect", x="4", y="4", width="8", height="1", fill="#FFFFFF"),
    _shape("rect", x="4", y="5", width="8", height="1", fill="#999999"),
    _shape("path", d="M5 6 h6 l-1 9 H6 Z", fill="#000000"),
    _shape("path", d="M6 7 h4 l-1 7 H7 Z", fill="#DDDDDD"),
    _shape("rect", x="7", y="8", width="1", height="5", fill="#999999"),
    _shape("rect", x="8", y="8", width="1", height="5", fill="#FFFFFF"),
)

