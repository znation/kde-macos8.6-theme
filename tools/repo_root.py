"""The repository root every ``tools/`` module works from.

The command-line tools read shipped files and write generated artifacts relative
to the repository they live in. Deriving that root per module with
``Path(__file__).resolve().parents[1]`` silently names the wrong directory for
a helper placed in a subpackage such as ``tools/png/``. The derivation lives
here once; the test bootstrap ``tests/support/repo_root.py``
also re-exports this value after putting the repository on ``sys.path``, so the
tools, the suite and their fixtures all name the same root.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
