"""The repository root every ``tools/`` module works from.

The command-line tools read shipped files and write generated artifacts relative
to the repository they live in. Each used to derive that root itself with
``Path(__file__).resolve().parents[1]``, which silently names the wrong
directory for a helper moved into a subpackage such as ``tools/png/``. The
derivation lives here once; the test bootstrap ``tests/support/repo_root.py``
also re-exports this value after putting the repository on ``sys.path``, so the
tools, the suite and their fixtures all name the same root.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
