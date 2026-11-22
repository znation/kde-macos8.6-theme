"""Measured chrome fixtures for the KIO file-dialog gate.

The title bar's window-icon box was measured pixel-exact in the 2026-11-11
KIO chooser session. Its owning assertions remain in
``tests/test_render_file_dialog.py``.
"""

# The title bar's leftmost 13x13 box (window icon box, x=4..16,
# y=7..19): a #888888-outline box with the fallback-theme icon mark
# inside and the #FFFFFF bevel column/row at x=16/y=19, measured
# pixel-exact on the runs named in ``TestFileDialogRender``'s class
# docstring in ``tests/test_render_file_dialog.py``.
ICON_BOX_ROWS = (
    ("#888888", "#888888", "#888888", "#888888", "#888888", "#888888",
     "#888888", "#888888", "#888888", "#888888", "#888888", "#888888",
     "#CCCCCC"),
    ("#888888", "#222222", "#222222", "#222222", "#222222", "#222222",
     "#222222", "#222222", "#222222", "#222222", "#222222", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#FFFFFF", "#CCCCCC", "#CCCCCC", "#CCCCCC",
     "#CCCCCC", "#CCCCCC", "#CCCCCC", "#CCCCCC", "#CCCCCC", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#CCCCCC", "#999999", "#999999", "#AAAAAA",
     "#AAAAAA", "#BBBBBB", "#BBBBBB", "#CCCCCC", "#888888", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#CCCCCC", "#999999", "#AAAAAA", "#AAAAAA",
     "#BBBBBB", "#BBBBBB", "#CCCCCC", "#CCCCCC", "#888888", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#CCCCCC", "#AAAAAA", "#AAAAAA", "#BBBBBB",
     "#BBBBBB", "#CCCCCC", "#CCCCCC", "#DDDDDD", "#888888", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#CCCCCC", "#AAAAAA", "#BBBBBB", "#BBBBBB",
     "#CCCCCC", "#CCCCCC", "#DDDDDD", "#DDDDDD", "#888888", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#CCCCCC", "#BBBBBB", "#BBBBBB", "#CCCCCC",
     "#CCCCCC", "#DDDDDD", "#DDDDDD", "#EEEEEE", "#888888", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#CCCCCC", "#BBBBBB", "#CCCCCC", "#CCCCCC",
     "#DDDDDD", "#DDDDDD", "#EEEEEE", "#EEEEEE", "#888888", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#CCCCCC", "#CCCCCC", "#CCCCCC", "#DDDDDD",
     "#DDDDDD", "#EEEEEE", "#EEEEEE", "#FFFFFF", "#888888", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#CCCCCC", "#888888", "#888888", "#888888",
     "#888888", "#888888", "#888888", "#888888", "#888888", "#222222",
     "#FFFFFF"),
    ("#888888", "#222222", "#222222", "#222222", "#222222", "#222222",
     "#222222", "#222222", "#222222", "#222222", "#222222", "#222222",
     "#FFFFFF"),
    ("#CCCCCC", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
     "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
     "#FFFFFF"),
)
