"""The Platinum cursor set's build and install modules, grouped in one package.

``tools/cursor/art.py`` holds the X names, aliases and palette of the cursor
set, with the grids in ``tools/cursor/art_pointers.py``,
``tools/cursor/art_resize.py`` and ``tools/cursor/art_drag.py``, and the
antialiased rasterizer in ``tools/cursor/vector.py``. ``tools/cursor/checks.py``
validates the set, ``tools/cursor/config.py`` reads the KDE cursor setting,
``tools/cursor/link.py`` installs and removes the ``$HOME/.icons`` link,
``tools/cursor/selection.py`` runs the selector and ``tools/cursor/workflow.py``
sequences them for ``tools/apply_cursor.py``.

The package has no re-exports: a consumer imports the submodule it needs, so
each name is defined in exactly one place.
"""
