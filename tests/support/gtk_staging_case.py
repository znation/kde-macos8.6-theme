"""Shared base for the GTK staging suites (``tests/test_gtk_staging*.py``).

Holds the temp root and the staging and backup name helpers that the
staging, commit and backup-sibling tests all use.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from support.tmp_dir import make_tmp_dir


class StagingTestCase(unittest.TestCase):
    """Base with a temp root and the staging-name helper."""

    def setUp(self):
        self.root = make_tmp_dir(self)

    def staging_of(self, target: Path) -> Path:
        """Return the ``.staging`` sibling ``_stage`` uses for *target*."""
        return target.with_name(f".{target.name}.staging")

    def backups_of(self, target: Path) -> list[Path]:
        """Return the ``.backup`` siblings ``commit`` may use for *target*."""
        return list(target.parent.glob(f".{target.name}.*.backup"))

    def fail_the_staged_rename(self, target: Path):
        """Return an ``os.replace`` stand-in that refuses to publish *target*.

        The staged file's rename onto *target* raises ``OSError``; every
        other rename goes to the real ``os.replace``.
        """
        real_replace = os.replace

        def replace(source, destination, *args, **kwargs):
            if str(source).endswith(".staging") and Path(destination) == target:
                raise OSError("injected rename failure")
            return real_replace(source, destination, *args, **kwargs)

        return replace
