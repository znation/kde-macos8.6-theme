"""Put the repository root on ``sys.path`` for the test suite.

The test modules import the ``tools/`` package by its dotted name, which needs
the repository root on ``sys.path``; ``unittest discover -s tests`` puts only
``tests/`` there. This module finds the root from its own location and puts it
on ``sys.path`` when it is imported, so a test module or a helper that reaches
into ``tools`` starts with ``from support import repo_root`` instead of
repeating the setup. The insertion is idempotent: the root is added only when it
is not already present.

``ROOT`` itself comes from ``tools.repo_root``, the one production source: the
bootstrap needs its own location only long enough to import that module, and
every tool, test and fixture then names the same value.
"""

from __future__ import annotations

import sys
from pathlib import Path


_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[2]

if str(_BOOTSTRAP_ROOT) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP_ROOT))

from tools.repo_root import ROOT  # noqa: E402  (needs the path inserted above)
