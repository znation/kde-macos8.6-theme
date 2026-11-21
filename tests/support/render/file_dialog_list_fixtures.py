"""Measured list fixtures for the KIO file-dialog gate.

The pixel maps and row geometry were measured from the host's 2026-11-11
KIO chooser session. Their owning assertions remain in
``tests/test_render_file_dialog.py``.
"""

# Measured in the 2026-11-11 KIO chooser capture. The fallback document glyph's
# fold shading blends against each row's own face colour, so its maps differ.
DOC_ICON_ON_WHITE = (
    ("#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#7F7F7F", "#FFFFFF", "#FFFFFF"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#AFAFAF", "#DDDDDD", "#DDDDDD", "#FFFFFF"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#AFAFAF", "#DDDDDD", "#7F7F7F"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#AFAFAF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#999999", "#999999", "#999999", "#999999", "#999999", "#999999", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#999999", "#999999", "#999999", "#999999", "#999999", "#999999", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#999999", "#999999", "#999999", "#999999", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"),
)
DOC_ICON_ON_GREY = (
    ("#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#777777", "#EEEEEE", "#EEEEEE"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#AFAFAF", "#DDDDDD", "#DDDDDD", "#EEEEEE"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#AFAFAF", "#DDDDDD", "#777777"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#AFAFAF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#999999", "#999999", "#999999", "#999999", "#999999", "#999999", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#999999", "#999999", "#999999", "#999999", "#999999", "#999999", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#999999", "#999999", "#999999", "#999999", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
    ("#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"),
)
RTF_ICON = (
    ("#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"),
    ("#FFFFFF",) * 12,
    ("#FFFFFF",) * 12,
    ("#0C2D63",) * 12,
    ("#FFFFFF",) * 12,
    ("#FFFFFF",) * 12,
    ("#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"),
    ("#FFFFFF",) * 12,
    ("#0C2D63",) * 12,
    ("#FFFFFF",) * 12,
    ("#FFFFFF",) * 12,
    ("#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#FFFFFF", "#FFFFFF", "#FFFFFF"),
)
ICON_CELLS = ((173, 126, 10, 13, DOC_ICON_ON_WHITE), (173, 146, 10, 13, DOC_ICON_ON_GREY), (172, 167, 12, 12, RTF_ICON))
# The three seeded rows begin at these coordinates and span 20 rows each.
# Each rectangle is measured live ink (icon, name, size) omitted from the face
# comparison; the clock-dependent date column x=395..473 is likewise excluded
# from exact face pins and checked for live ink by the owning gate.
# The size-text rectangles were re-derived 2026-11-11 after the Name column
# widened by 7px. Empty rows below the seeded listing stay flat white.
ROW_BANDS = (
    (123, "#FFFFFF", ((173, 182, 126, 138), (191, 241, 128, 139), (375, 393, 128, 137))),
    (143, "#EEEEEE", ((173, 182, 146, 158), (191, 241, 148, 157), (375, 393, 148, 157))),
    (163, "#FFFFFF", ((172, 183, 167, 178), (191, 241, 168, 178), (375, 393, 168, 177))),
)
ROW_BAND_HEIGHT = 20
ROW_TEXT_BANDS = ((191, 241), (375, 393), (395, 473))
EMPTY_ROWS = (183, 251)
