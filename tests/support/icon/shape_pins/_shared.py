"""Drawing-element helpers shared by the per-family pin registries.

The blank-document page tuples are the generic document's first three
drawing elements without its text lines; the trash body is the lid and
can the empty and full Trash draw in common. Each family module spreads
these prefixes into its pins, so a shared-art edit lands in one place.
"""


def _shape(tag, **attributes):
    """Return one expected drawing element: its tag and its attributes."""
    return (tag, attributes)


# The blank-document page, one tuple per size, shared by the three blank
# document names. It is the generic document's first three drawing elements
# (the page outline, the white page and the folded corner) without its text
# lines; the page-sharing test in ``test_icon_theme_geometry`` compares it
# with the shipped generic file.
_BLANK_DOCUMENT_16 = (
    _shape("path", d="M3 1 h7 l3 3 v10 H3 Z", fill="#000000"),
    _shape("path", d="M4 2 h5 l3 3 v8 H4 Z", fill="#FFFFFF"),
    _shape("path", d="M9 2 L12 2 L12 5 Z", fill="#DDDDDD"),
)
_BLANK_DOCUMENT_22 = (
    _shape("path", d="M4 1 h10 l4 4 v15 H4 Z", fill="#000000"),
    _shape("path", d="M5 2 h8 l4 4 v13 H5 Z", fill="#FFFFFF"),
    _shape("path", d="M13 2 L17 2 L17 6 Z", fill="#DDDDDD"),
)
_BLANK_DOCUMENT_32 = (
    _shape("path", d="M6 3 h14 l6 6 v20 H6 Z", fill="#000000"),
    _shape("path", d="M7 4 h12 l6 6 v18 H7 Z", fill="#FFFFFF"),
    _shape("path", d="M19 4 L25 4 L25 10 Z", fill="#DDDDDD"),
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

