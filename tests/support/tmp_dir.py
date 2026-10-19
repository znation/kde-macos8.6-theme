"""A temp directory that a test case removes when its test ends."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


def make_tmp_dir(case: unittest.TestCase) -> Path:
    """Return a fresh temp dir that *case* removes when its test ends."""
    tmp = tempfile.TemporaryDirectory()
    case.addCleanup(tmp.cleanup)
    return Path(tmp.name)
