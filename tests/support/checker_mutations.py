"""Manufacture the malformed inputs the shipped registers never hold.

Each checker enforces a boundary the shipped data happens not to cross:
``tests/invariants.py``'s register parser and reference resolver, and
``tests/test_placeholders.py``'s marker scanner. Twelve Fixed entries share one
mechanism -- a checker silently accepted or dropped a malformed input the
shipped records never contained, so no test or real run could surface the bug.
This module derives one named mutation per boundary from a copy of the real
register (and a scratch theme root), so ``tests/test_checker_mutations.py`` can
apply it and observe the checker's answer instead of waiting for a reader.

A mutation's ``diagnostic`` is the substring the checker's ``AssertionError``
must contain; a mutation with a diagnostic is a rejection boundary and must be
named in the matching checker's ``REJECTION_SHAPES``. ``None`` marks an
acceptance boundary, where the checker must keep or find the input and
``observe`` pins what it must produce -- the escaped pipe and the placeholder
formats are accepted, not rejected, so no diagnostic exists to match.
"""

from __future__ import annotations

import os
import re
import shutil
from collections import namedtuple
from pathlib import Path

from support.repo_root import ROOT

INVARIANTS_REGISTER = os.path.join("docs", "invariants.md")
PLACEHOLDERS_REGISTER = "PLACEHOLDERS.md"
# The shipped files the reference mutations point the register's first row at.
# ``MUTANT_MODULE`` is a fixture, not a test module: unittest collects nothing
# from it, and it holds the class shapes the shipped tests never define.
# ``HARNESS_MODULE`` holds a real collected test case. Both are literal
# repository paths that exist in the tree, so the stage self-check's
# added-nonexistent-path guard sees them and passes on its own terms instead of
# the harness hiding them behind a ``./`` prefix or a runtime join.
MUTANT_MODULE = "tests/support/mutant_module.py"
HARNESS_MODULE = "tests/test_checker_mutations.py"

# ``apply(scratch)`` mutates the scratch copy; ``diagnostic`` is the substring
# the checker's AssertionError must match (None for an acceptance boundary);
# ``observe(scratch)`` pins the accepted output when there is no diagnostic.
Mutation = namedtuple("Mutation", "name apply diagnostic observe")

_REFERENCE = re.compile(r"`([^`]+)`")


def _first_data_row(text):
    """Return the first table row line that carries a test reference."""
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("|") and _REFERENCE.search(line):
            return line
    raise AssertionError("no table row carries a test reference")


def _replace_first_reference(text, reference):
    """Return *text* with the first row's backticked reference replaced."""
    line = _first_data_row(text)
    match = _REFERENCE.search(line)
    mutated = line[: match.start(1)] + reference + line[match.end(1):]
    return text.replace(line, mutated, 1)


def _replace_first_guarantee(text, guarantee):
    """Return *text* with the first row's Guarantee cell replaced."""
    line = _first_data_row(text)
    cells = line.rstrip("\n").split("|")
    cells[1] = f" {guarantee} "
    return text.replace(line, "|".join(cells) + "\n", 1)


def _drop_first_row_cell(text):
    """Return *text* with the first row's Provenance cell removed (two cells)."""
    line = _first_data_row(text)
    cells = line.rstrip("\n").split("|")
    del cells[-2]
    return text.replace(line, "|".join(cells) + "\n", 1)


def _strip_first_row_backticks(text):
    """Return *text* with the first row's backticks removed (no test named)."""
    line = _first_data_row(text)
    return text.replace(line, line.replace("`", ""), 1)


def _append_row(text, asset, description):
    """Return *text* with one ``| `asset` | description |`` register row added."""
    if not text.endswith("\n"):
        text += "\n"
    return text + f"| `{asset}` | {description} |\n"


class Scratch:
    """A scratch copy of the shipped repository a mutation transforms.

    ``build`` copies the shipped ``tests/`` tree (so the real register's
    references resolve), creates one empty directory per ``theme/`` subsystem,
    and copies the two shipped registers. ``reset`` restores the registers and
    removes every file a mutation wrote, so one scratch serves the whole table.
    """

    def __init__(self, root, invariants_text, placeholders_text):
        self.root = Path(root)
        self.invariants_text = invariants_text
        self.placeholders_text = placeholders_text
        self._written = []

    @classmethod
    def build(cls, tmp):
        root = Path(tmp)
        shutil.copytree(
            ROOT / "tests",
            root / "tests",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        for name in os.listdir(ROOT / "theme"):
            if os.path.isdir(ROOT / "theme" / name):
                (root / "theme" / name).mkdir(parents=True, exist_ok=True)
        invariants_text = (ROOT / INVARIANTS_REGISTER).read_text(encoding="utf-8")
        placeholders_text = (ROOT / PLACEHOLDERS_REGISTER).read_text(encoding="utf-8")
        scratch = cls(root, invariants_text, placeholders_text)
        scratch.reset()
        return scratch

    @property
    def invariants_register(self):
        return str(self.root / INVARIANTS_REGISTER)

    @property
    def placeholders_register(self):
        return str(self.root / PLACEHOLDERS_REGISTER)

    def read_invariants(self):
        return (self.root / INVARIANTS_REGISTER).read_text(encoding="utf-8")

    def reset(self):
        for path in self._written:
            path.unlink(missing_ok=True)
        self._written = []
        self._write(INVARIANTS_REGISTER, self.invariants_text)
        self._write(PLACEHOLDERS_REGISTER, self.placeholders_text)

    def write_invariants(self, text):
        self._write(INVARIANTS_REGISTER, text)

    def write_placeholders(self, text):
        self._write(PLACEHOLDERS_REGISTER, text)

    def write_repo_file(self, rel, text):
        """Write *text* at the repository-relative *rel* in the scratch root."""
        self._write(rel, text)

    def _write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self._written.append(path)


def _reference_apply(reference):
    """Return an ``apply`` that points the first register row at *reference*."""

    def apply(scratch):
        scratch.write_invariants(
            _replace_first_reference(scratch.invariants_text, reference)
        )

    return apply


def _apply_malformed_row(scratch):
    scratch.write_invariants(_drop_first_row_cell(scratch.invariants_text))


def _apply_test_cell_without_reference(scratch):
    scratch.write_invariants(_strip_first_row_backticks(scratch.invariants_text))


def _apply_escaped_pipe(scratch):
    scratch.write_invariants(
        _replace_first_guarantee(
            scratch.invariants_text, "The active \\| inactive title-bar boxes hold."
        )
    )


def _observe_escaped_pipe(scratch):
    from invariants import parse_rows

    sections = parse_rows(scratch.read_invariants())
    guarantees = [row.guarantee for rows in sections.values() for row in rows]
    if not any("|" in guarantee for guarantee in guarantees):
        raise AssertionError(
            "escaped-pipe row was dropped: no parsed guarantee kept a literal pipe"
        )


INVARIANTS_MUTATIONS = (
    Mutation(
        "local-base-that-only-looks-like-a-test-case",
        _reference_apply(MUTANT_MODULE + "::TestNotCollected::test_ok"),
        "names a class that is not a test case",
        None,
    ),
    Mutation(
        "reference-outside-repository",
        _reference_apply("../outside/mutant_module.py::TestReal"),
        "outside the repository",
        None,
    ),
    Mutation(
        "method-on-non-test-case-class",
        _reference_apply(MUTANT_MODULE + "::NotATestCase::test_looks_like_a_test"),
        "names a class that is not a test case",
        None,
    ),
    Mutation(
        "reference-to-non-test-case-class",
        _reference_apply(MUTANT_MODULE + "::Helper"),
        "names a class that is not a test case",
        None,
    ),
    Mutation(
        "non-test-method",
        _reference_apply(HARNESS_MODULE + "::TestCheckerMutations::setUpClass"),
        "names a method that is not a test",
        None,
    ),
    Mutation(
        "trailing-segment",
        _reference_apply(
            HARNESS_MODULE + "::TestCheckerMutations::test_invariants_mutations::junk"
        ),
        "names more than a class and method",
        None,
    ),
    Mutation(
        "empty-qualifier",
        _reference_apply(MUTANT_MODULE + "::"),
        "names no class or method",
        None,
    ),
    Mutation("malformed-row", _apply_malformed_row, "malformed table row", None),
    Mutation(
        "test-cell-without-reference",
        _apply_test_cell_without_reference,
        "no test reference",
        None,
    ),
    Mutation("escaped-pipe", _apply_escaped_pipe, None, _observe_escaped_pipe),
)


# Real shipped files the placeholder mutations use. The scratch theme root is
# built from empty subsystem directories, so a mutation can write one of these
# paths, leave it out, or write it unmarked, and the checker's answer is
# observable. Naming a repository path that exists keeps the stage
# self-check's added-nonexistent-path guard satisfied instead of the harness
# hiding the path behind a runtime join.
USER_TRASH_ICON = "theme/icons/org.macos8.desktop/32x32/places/user-trash.svg"
FOLDER_ICON = "theme/icons/org.macos8.desktop/32x32/places/folder.svg"
ABSENT_ICON = "theme/icons/org.macos8.desktop/32x32/places/inode-directory.svg"
KVCONFIG = "theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig"
LAYOUT_JS = "theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js"
AURORAE_DESKTOPRC = "theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc"


def _placeholder_acceptance(asset, description):
    """Return an ``apply`` that adds a marked file *asset* and its register row."""

    def apply(scratch):
        scratch.write_repo_file(asset, f"# PLACEHOLDER: {description}\n")
        scratch.write_placeholders(
            _append_row(scratch.placeholders_text, asset, description)
        )

    return apply


def _observe_placeholder(asset):
    """Return an ``observe`` that the marker scanner found the marked file *asset*."""

    def observe(scratch):
        from test_placeholders import markers

        if asset not in markers(scratch.root):
            raise AssertionError(
                f"{asset} carries a PLACEHOLDER: marker the scanner did not find"
            )

    return observe


def _apply_marker_without_row(scratch):
    scratch.write_repo_file(USER_TRASH_ICON, "<!-- PLACEHOLDER: an orphan -->\n")


def _apply_row_without_file(scratch):
    scratch.write_placeholders(
        _append_row(scratch.placeholders_text, ABSENT_ICON, "an absent icon")
    )


def _apply_row_without_marker(scratch):
    scratch.write_repo_file(FOLDER_ICON, "<svg/>\n")
    scratch.write_placeholders(
        _append_row(scratch.placeholders_text, FOLDER_ICON, "a plain icon")
    )


PLACEHOLDER_MUTATIONS = (
    Mutation("marker-without-row", _apply_marker_without_row, "has no row", None),
    Mutation("row-without-file", _apply_row_without_file, "does not exist", None),
    Mutation("row-without-marker", _apply_row_without_marker, "carries no", None),
    Mutation(
        "kvconfig-marker",
        _placeholder_acceptance(KVCONFIG, "a Kvantum widget style"),
        None,
        _observe_placeholder(KVCONFIG),
    ),
    Mutation(
        "js-marker",
        _placeholder_acceptance(LAYOUT_JS, "a desktop layout"),
        None,
        _observe_placeholder(LAYOUT_JS),
    ),
    Mutation(
        "desktoprc-marker",
        _placeholder_acceptance(AURORAE_DESKTOPRC, "an Aurorae decoration config"),
        None,
        _observe_placeholder(AURORAE_DESKTOPRC),
    ),
)
