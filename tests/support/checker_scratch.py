"""The scratch repository copy a checker mutation transforms.

``tests/support/invariants_mutations.py`` and
``tests/support/placeholders_mutations.py`` each derive one named mutation per
boundary from a copy of a real register (and a scratch theme root), so
``tests/test_checker_mutations.py`` can apply it and observe the checker's
answer instead of waiting for a reader. This module holds the scratch copy
those two families share: :class:`Scratch`, the :data:`Mutation` record they
build, and the register paths it seeds.
"""

from __future__ import annotations

import os
import shutil
from collections import namedtuple
from pathlib import Path

from support import containment
from support.repo_root import ROOT

INVARIANTS_REGISTER = os.path.join("docs", "invariants.md")
PLACEHOLDERS_REGISTER = "PLACEHOLDERS.md"

# ``apply(scratch)`` mutates the scratch copy; ``diagnostic`` is the substring
# the checker's AssertionError must match (None for an acceptance boundary);
# ``observe(scratch)`` pins the accepted output when there is no diagnostic.
Mutation = namedtuple("Mutation", "name apply diagnostic observe")


def _read_register(relative_path):
    """Return the repository register's text, refusing a symlink escape.

    The two registers are read to seed the scratch copy, and the checker
    echoes a malformed row's line when it rejects it. A checked-in symlink at
    a register path that resolves outside the repository must therefore be
    refused before it is opened, or a private file's line reaches the
    checker's diagnostic through the scratch copy.
    """
    return containment.read_text(ROOT / relative_path, ROOT)


class Scratch:
    """A scratch copy of the shipped repository a mutation transforms.

    ``build`` copies the shipped ``tests/`` tree (so the real register's
    references resolve), creates one empty directory per ``theme/`` subsystem,
    and copies the two shipped registers. ``reset`` restores the registers,
    removes every file or directory a mutation wrote, and restores a file a
    mutation overwrote, so one scratch serves the whole table.
    """

    def __init__(self, root, invariants_text, placeholders_text):
        self.root = Path(root)
        self.invariants_text = invariants_text
        self.placeholders_text = placeholders_text
        self._written = []
        self._directories = []
        self._originals = {}

    @classmethod
    def build(cls, tmp):
        """Copy the shipped tests tree and registers into *tmp*; return it reset."""
        root = Path(tmp)
        shutil.copytree(
            ROOT / "tests",
            root / "tests",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        for name in os.listdir(ROOT / "theme"):
            if os.path.isdir(ROOT / "theme" / name):
                (root / "theme" / name).mkdir(parents=True, exist_ok=True)
        invariants_text = _read_register(INVARIANTS_REGISTER)
        placeholders_text = _read_register(PLACEHOLDERS_REGISTER)
        scratch = cls(root, invariants_text, placeholders_text)
        scratch.reset()
        return scratch

    @property
    def invariants_register(self):
        """Return the scratch copy's invariants-register path."""
        return str(self.root / INVARIANTS_REGISTER)

    @property
    def placeholders_register(self):
        """Return the scratch copy's placeholder-register path."""
        return str(self.root / PLACEHOLDERS_REGISTER)

    def read_invariants(self):
        """Return the scratch invariants register's text."""
        return (self.root / INVARIANTS_REGISTER).read_text(encoding="utf-8")

    def reset(self):
        """Restore the scratch root's seeded files and remove every mutation."""
        for path in self._directories:
            shutil.rmtree(path, ignore_errors=True)
        self._directories = []
        for path in self._written:
            path.unlink(missing_ok=True)
        self._written = []
        for path, data in self._originals.items():
            path.write_bytes(data)
        self._originals = {}
        self._write(INVARIANTS_REGISTER, self.invariants_text)
        self._write(PLACEHOLDERS_REGISTER, self.placeholders_text)

    def write_invariants(self, text):
        """Replace the scratch invariants register with *text*."""
        self._write(INVARIANTS_REGISTER, text)

    def write_placeholders(self, text):
        """Replace the scratch placeholder register with *text*."""
        self._write(PLACEHOLDERS_REGISTER, text)

    def write_repo_file(self, rel, text):
        """Write *text* at the repository-relative *rel* in the scratch root."""
        self._write(rel, text)

    def write_directory(self, rel):
        """Replace *rel* with an empty directory in the scratch root.

        A checker that opens *rel* as a file then hits its ``OSError`` arm;
        ``reset`` removes the directory again.
        """
        path = self.root / rel
        if path.exists() or path.is_symlink():
            path.unlink()
        path.mkdir(parents=True, exist_ok=True)
        self._directories.append(path)

    def write_symlink(self, rel, target):
        """Create a symlink at *rel* pointing at *target* in the scratch root."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)
        self._written.append(path)

    def write_bytes(self, rel, data):
        """Write *data* at *rel*, restoring an overwritten file on ``reset``."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self._originals.setdefault(path, path.read_bytes())
        else:
            self._written.append(path)
        path.write_bytes(data)

    def _write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self._written.append(path)
