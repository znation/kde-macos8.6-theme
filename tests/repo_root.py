"""Put the repository root on ``sys.path`` for the test suite.

The test modules import the ``tools/`` package by its dotted name, which needs
the repository root on ``sys.path``; ``unittest discover -s tests`` puts only
``tests/`` there. This module computes that root once from its own location
and puts it on ``sys.path`` when it is imported, so a test module or a helper
that reaches into ``tools`` starts with ``import repo_root`` instead of
repeating the setup. The insertion is idempotent: the root is added only when
it is not already present.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
