"""The session stub the render writer suites share.

The ``tools/render`` writer functions (``settle_scripts.py``'s script
writers and ``window_rules.py``'s ``write_window_rules``) read only the
session's config and scratch homes, so the suites pin them against this
stub instead of a real session. Its two call sites are
``tests/test_render_settle_scripts.py`` and
``tests/test_render_window_rules.py``.
"""

from __future__ import annotations

from pathlib import Path


class FakeSession:
    """The attributes the writers read: the config and scratch homes."""

    def __init__(self, config: Path, root: Path | None = None):
        self.config = config
        self.root = root if root is not None else config
