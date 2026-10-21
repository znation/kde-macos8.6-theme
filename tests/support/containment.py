"""Test-side name for the shared containment guard.

The guard itself lives in :mod:`tools.containment`, the one module both the
``tools/`` scripts and the test suite can import. This module keeps the
``support.containment`` name the test helpers already use and re-exports the
guard's functions, so there is a single implementation. Importing
:mod:`support.repo_root` first puts the repository root on ``sys.path`` so
``tools.containment`` resolves even when the suite runs from ``tests/``.
"""

from __future__ import annotations

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.containment import (  # noqa: F401
    is_within,
    open_regular_binary,
    read_bytes,
    read_text,
    require_within_repo,
    resolves_within,
)

__all__ = [
    "is_within",
    "open_regular_binary",
    "read_bytes",
    "read_text",
    "require_within_repo",
    "resolves_within",
]
