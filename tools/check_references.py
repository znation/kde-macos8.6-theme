#!/usr/bin/env python3
"""Check that the Mac OS 8.6 reference screenshot set is self-consistent.

``macos8.6-screenshots/sources.txt`` is the provenance record for the reference
set: one ``<filename> | <source URL> | <version label>`` line per image. This
script verifies that record against the files actually on disk, so a renamed or
forgotten image cannot silently drop out of the evidence trail. It also rejects
unmaterialized Git LFS pointer files and files whose bytes are not a known image
format, such as an HTML error page saved under an image name.

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

# Leading bytes of the raster formats the reference set uses. The extension is
# deliberately not consulted: sherlock_fandom.jpg is a WebP payload.
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
GIF_MAGICS = (b"GIF87a", b"GIF89a")
IMAGE_MAGICS = (PNG_MAGIC, JPEG_MAGIC, *GIF_MAGICS)

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


def _looks_like_image(path: Path) -> bool:
    """Return True when *path* begins with a known raster image signature.

    Only the bytes decide, never the extension: ``sherlock_fandom.jpg`` is a
    WebP payload by design, so the WebP signature is accepted here too.
    """
    with path.open("rb") as handle:
        head = handle.read(12)
    if any(head.startswith(magic) for magic in IMAGE_MAGICS):
        return True
    return head[:4] == b"RIFF" and head[8:12] == b"WEBP"


def _escape_controls(text: str) -> str:
    """Render *text* with control characters escaped for terminal output.

    A screenshot filename is contributor-supplied data. Printed raw, a name
    containing an ESC or a newline would drive the operator's terminal with a
    live escape sequence or forge an extra diagnostic line, so every control
    character becomes a visible ``\\uXXXX`` escape before the name is shown.
    """
    return "".join(
        ch if ch.isprintable() else f"\\u{ord(ch):04x}" for ch in text
    )


def _resolves_within(directory: Path, path: Path) -> bool:
    """Return True when *path* resolves to a location inside *directory*.

    The reference directory is contributor-supplied, and a checked-in symlink
    can point anywhere on the machine: a ``sources.txt`` symlink to a private
    file would make the checker read that file and print its lines as
    diagnostics. Resolving both paths keeps every read inside the reference
    directory even when a symlink tries to leave it.
    """
    try:
        return path.resolve().is_relative_to(directory.resolve())
    except OSError:
        return False


def check_references(directory: Path) -> list[str]:
    """Return a list of human-readable problems in *directory*.

    An empty list means every source entry names an existing image, every image
    has exactly one entry, and every entry has the three expected fields.
    """
    sources = directory / SOURCES_NAME
    if not _resolves_within(directory, sources):
        return [f"{sources}: points outside {directory}/ (a symlink escape)"]
    if not sources.is_file():
        return [f"{sources}: missing sources file"]

    try:
        sources_text = sources.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{sources}: could not be read: {exc}"]
    except UnicodeDecodeError as exc:
        return [f"{sources}: not valid UTF-8 text: {exc}"]

    problems: list[str] = []
    entries: dict[str, int] = {}

    for lineno, raw in enumerate(sources_text.splitlines(), 1):
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
        if Path(filename).name != filename or filename in (".", ".."):
            problems.append(
                f"{sources}:{lineno}: {filename!r} must be a bare filename in "
                f"{directory}/, not a path"
            )
            continue
        if filename in entries:
            problems.append(
                f"{sources}:{lineno}: duplicate entry for {filename!r} "
                f"(first at line {entries[filename]})"
            )
            continue
        entries[filename] = lineno
        image = directory / filename
        if not _resolves_within(directory, image):
            problems.append(
                f"{sources}:{lineno}: {filename!r} points outside "
                f"{directory}/ (a symlink escape)"
            )
            continue
        if not image.is_file():
            problems.append(f"{sources}:{lineno}: {filename!r} does not exist in {directory}/")
            continue
        try:
            if _is_lfs_pointer(image):
                problems.append(
                    f"{sources}:{lineno}: {filename!r} is an unmaterialized Git LFS pointer; "
                    "run `git lfs install && git lfs pull` to fetch the image"
                )
            elif not _looks_like_image(image):
                problems.append(
                    f"{sources}:{lineno}: {filename!r} is not a PNG, JPEG, GIF or WebP image; "
                    "it may be an HTML error page or a truncated download"
                )
        except OSError as exc:
            problems.append(
                f"{sources}:{lineno}: {filename!r} could not be read: {exc}"
            )

    try:
        listed = sorted(directory.iterdir())
    except OSError as exc:
        problems.append(f"{directory}: could not be listed: {exc}")
        return problems

    for path in listed:
        if path.name == SOURCES_NAME or not path.is_file():
            continue
        if path.name in entries:
            continue
        # An image with no entry is undeclared whether or not its name marks
        # it as one: the bytes are checked too, so a screenshot saved without
        # an image extension (or a JPEG under a .bin name) is still caught.
        # Files with an image extension are flagged even when their bytes are
        # not an image, so a stray or half-downloaded file cannot hide behind
        # its name.
        try:
            has_image_bytes = _looks_like_image(path)
        except OSError as exc:
            problems.append(
                f"{_escape_controls(str(path))}: could not be read: {exc}"
            )
            continue
        if path.suffix.lower() in IMAGE_SUFFIXES or has_image_bytes:
            problems.append(
                f"{_escape_controls(str(path))}: image has no entry in {SOURCES_NAME}"
            )

    return problems


def _self_test() -> int:
    """Run the checker against small fixtures; return 0 when all behave."""
    cases = [
        # (name, sources.txt contents or None to omit the file, files on disk,
        #  substring expected in a problem)
        ("clean", "good.png | https://example.test/g.png | Mac OS 8.6 (desktop)\n",
         [("good.png", PNG_MAGIC)], None),
        ("missing sources file", None, [("good.png", PNG_MAGIC)],
         "missing sources file"),
        ("comments and blank lines",
         "# provenance\n\ngood.png | u | l\n# trailing note\n",
         [("good.png", PNG_MAGIC)], None),
        ("missing file", "ghost.png | https://example.test/g.png | label\n", [],
         "ghost.png"),
        ("path in filename", "sub/good.png | u | l\n",
         [("sub/good.png", PNG_MAGIC)], "bare filename"),
        ("undeclared image", "", [("extra.png", PNG_MAGIC)], "extra.png"),
        # No image extension, but the bytes are a PNG: the scan must read the
        # content, not trust the name, or this file drops out of provenance.
        ("undeclared extensionless image", "", [("stray", PNG_MAGIC)], "stray"),
        ("undeclared jpeg misnamed as data", "",
         [("shot.bin", JPEG_MAGIC)], "shot.bin"),
        ("too few fields", "bad.png | https://example.test/b.png\n",
         [("bad.png", PNG_MAGIC)], "expected 3 fields"),
        ("empty field", "bad.png |  | label\n", [("bad.png", PNG_MAGIC)], "empty field"),
        ("duplicate", "dup.png | u | l\ndup.png | u | l\n",
         [("dup.png", PNG_MAGIC)], "duplicate"),
        ("lfs pointer", "stub.png | u | l\n",
         [("stub.png", b"version https://git-lfs.github.com/spec/v1\n"
                       b"oid sha256:deadbeef\nsize 12345\n")],
         "Git LFS pointer"),
        ("non-image payload", "fake.png | u | l\n",
         [("fake.png", b"<!DOCTYPE html>\n<html>404 Not Found</html>\n")],
         "not a PNG, JPEG, GIF or WebP image"),
        ("webp with jpg name", "shot.jpg | u | l\n",
         [("shot.jpg", b"RIFF\x24\x00\x00\x00WEBPVP8 ")], None),
    ]

    failed = False
    for name, sources_text, images, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            if sources_text is not None:
                (root / SOURCES_NAME).write_text(sources_text, encoding="utf-8")
            for image in images:
                filename, content = (
                    image if isinstance(image, tuple) else (image, b"")
                )
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
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
