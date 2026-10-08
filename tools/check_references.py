#!/usr/bin/env python3
"""Check that the Mac OS 8.6 reference screenshot set is self-consistent.

``macos8.6-screenshots/sources.txt`` is the provenance record for the reference
set: one ``<filename> | <source URL> | <version label>`` line per image. This
script verifies that record against the files actually on disk, so a renamed or
forgotten image cannot silently drop out of the evidence trail. It also rejects
unmaterialized Git LFS pointer files, which exist on disk but contain no image.

Usage:
    python3 tools/check_references.py              # check the repository
    python3 tools/check_references.py --self-test  # exercise the checks
    python3 tools/check_references.py --help       # show usage
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

REFERENCE_DIR = "macos8.6-screenshots"
SOURCES_NAME = "sources.txt"
IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp"})
SEPARATOR = " | "
# First line of a Git LFS pointer file; a real image never starts with this text.
LFS_POINTER_MAGIC = b"version https://git-lfs.github.com/spec/v1"

USAGE = """\
usage: check_references.py [--self-test | --help]

Check that macos8.6-screenshots/sources.txt matches the images on disk.

options:
  --self-test  run the checker's own fixtures instead of the repository
  -h, --help   show this message and exit
"""


def _is_lfs_pointer(path: Path) -> bool:
    """Return True when *path* is an unmaterialized Git LFS pointer, not data."""
    with path.open("rb") as handle:
        return handle.read(len(LFS_POINTER_MAGIC)) == LFS_POINTER_MAGIC


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
        image = directory / filename
        if not image.is_file():
            problems.append(f"{sources}:{lineno}: {filename!r} does not exist in {directory}/")
        elif _is_lfs_pointer(image):
            problems.append(
                f"{sources}:{lineno}: {filename!r} is an unmaterialized Git LFS pointer; "
                "run `git lfs install && git lfs pull` to fetch the image"
            )

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
        ("lfs pointer", "stub.png | u | l\n",
         [("stub.png", b"version https://git-lfs.github.com/spec/v1\n"
                       b"oid sha256:deadbeef\nsize 12345\n")],
         "Git LFS pointer"),
        ("binary image", "real.png | u | l\n",
         [("real.png", b"\x89PNG\r\n\x1a\n")], None),
    ]

    failed = False
    for name, sources_text, images, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / SOURCES_NAME).write_text(sources_text, encoding="utf-8")
            for image in images:
                name, content = image if isinstance(image, tuple) else (image, b"")
                (root / name).write_bytes(content)
            problems = check_references(root)
        if expected is None:
            if problems:
                failed = True
                print(f"self-test {name!r}: expected no problems, got {problems}")
        elif not any(expected in problem for problem in problems):
            failed = True
            print(f"self-test {name!r}: no problem mentioning {expected!r}; got {problems}")

    # Argument handling: --help prints usage and exits 0; anything unrecognized
    # exits 2 rather than silently running the repository check on a typo.
    cli_cases = [
        (["check_references.py", "--help"], 0, "usage:"),
        (["check_references.py", "-h"], 0, "usage:"),
        (["check_references.py", "--self-tests"], 2, "unknown argument"),
    ]
    for argv, expected_code, needle in cli_cases:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        combined = out.getvalue() + err.getvalue()
        if code != expected_code or needle not in combined:
            failed = True
            print(
                f"self-test cli {argv[1:]!r}: expected exit {expected_code} with {needle!r}, "
                f"got exit {code}: {combined!r}"
            )

    if failed:
        return 1
    print(f"self-test: {len(cases) + len(cli_cases)} cases passed")
    return 0


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args == ["--self-test"]:
        return _self_test()
    if args in (["-h"], ["--help"]):
        print(USAGE, end="")
        return 0
    if args:
        print(f"error: unknown argument(s): {' '.join(args)}", file=sys.stderr)
        print(USAGE, end="", file=sys.stderr)
        return 2

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
