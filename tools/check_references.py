#!/usr/bin/env python3
"""Check that the Mac OS 8.6 reference screenshot set is self-consistent.

``macos8.6-screenshots/sources.txt`` is the provenance record for the reference
set: one ``<filename> | <source URL> | <version label>`` line per image. This
script verifies that record against the files actually on disk, so a renamed or
forgotten image cannot silently drop out of the evidence trail.

Usage:
    python3 tools/check_references.py              # check the repository
    python3 tools/check_references.py --self-test  # exercise the checks
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REFERENCE_DIR = "macos8.6-screenshots"
SOURCES_NAME = "sources.txt"
IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp"})
SEPARATOR = " | "


def check_references(directory: Path) -> list[str]:
    """Return a list of human-readable problems in *directory*.

    An empty list means every source entry names an existing image, every image
    has exactly one entry, and every entry has the three expected fields.
    """
    sources = directory / SOURCES_NAME
    if not sources.is_file():
        return [f"{sources}: missing sources file"]

    problems: list[str] = []
    entries: dict[str, int] = {}

    for lineno, raw in enumerate(sources.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(SEPARATOR)
        if len(fields) != 3:
            problems.append(
                f"{sources}:{lineno}: expected 3 fields separated by {SEPARATOR.strip()!r}, "
                f"got {len(fields)}: {line!r}"
            )
            continue
        filename, url, label = (field.strip() for field in fields)
        if not filename or not url or not label:
            problems.append(f"{sources}:{lineno}: empty field in entry: {line!r}")
            continue
        if filename in entries:
            problems.append(
                f"{sources}:{lineno}: duplicate entry for {filename!r} "
                f"(first at line {entries[filename]})"
            )
            continue
        entries[filename] = lineno
        if not (directory / filename).is_file():
            problems.append(f"{sources}:{lineno}: {filename!r} does not exist in {directory}/")

    for path in sorted(directory.iterdir()):
        if path.name == SOURCES_NAME or not path.is_file():
            continue
        if path.suffix.lower() in IMAGE_SUFFIXES and path.name not in entries:
            problems.append(f"{path}: image has no entry in {SOURCES_NAME}")

    return problems


def _self_test() -> int:
    """Run the checker against small fixtures; return 0 when all behave."""
    cases = [
        # (name, sources.txt contents, files on disk, substring expected in a problem)
        ("clean", "good.png | https://example.test/g.png | Mac OS 8.6 (desktop)\n",
         ["good.png"], None),
        ("missing file", "ghost.png | https://example.test/g.png | label\n", [],
         "ghost.png"),
        ("undeclared image", "", ["extra.png"], "extra.png"),
        ("too few fields", "bad.png | https://example.test/b.png\n", ["bad.png"],
         "expected 3 fields"),
        ("empty field", "bad.png |  | label\n", ["bad.png"], "empty field"),
        ("duplicate", "dup.png | u | l\ndup.png | u | l\n", ["dup.png"], "duplicate"),
    ]

    failed = False
    for name, sources_text, images, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / SOURCES_NAME).write_text(sources_text, encoding="utf-8")
            for image in images:
                (root / image).write_bytes(b"")
            problems = check_references(root)
        if expected is None:
            if problems:
                failed = True
                print(f"self-test {name!r}: expected no problems, got {problems}")
        elif not any(expected in problem for problem in problems):
            failed = True
            print(f"self-test {name!r}: no problem mentioning {expected!r}; got {problems}")

    if failed:
        return 1
    print(f"self-test: {len(cases)} cases passed")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv[1:]:
        return _self_test()

    directory = Path(__file__).resolve().parent.parent / REFERENCE_DIR
    problems = check_references(directory)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(f"{len(problems)} problem(s) in the reference set", file=sys.stderr)
        return 1
    print(f"{directory}: reference set is consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
