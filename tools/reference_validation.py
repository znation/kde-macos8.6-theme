"""Validation helpers for ``tools/check_references.py``.

``macos8.6-screenshots/sources.txt`` is the provenance record for the
reference set, and the reference directory holds the images it names. This
module reads both and returns the problems it finds: an entry that names a
missing, unreadable, non-image or unmaterialized-LFS file, a source URL that
is not a well-formed absolute URL, a file on disk with no entry, a path
that escapes the reference directory through a symlink, or a reference
directory that itself resolves outside the repository. ``check_references``
runs those checks and returns the problem list; the checker script
``tools/check_references.py`` handles its arguments and reports its problems.

Keeping the checks here leaves the entry point with only argument handling and
the summary, and mirrors the test suite's split between the checker's I/O and
validation cases (``tests/test_check_references_io.py`` and
``tests/test_check_references_validation.py``).
"""

from __future__ import annotations

import os
from pathlib import Path

if __package__:
    from tools.containment import (
        open_regular_binary,
        require_within_repo,
        resolves_within,
    )
    from tools.image_format import (
        image_stream_format,
        is_complete,
        is_image,
        LFS_POINTER_MAGIC,
    )
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
    from tools.reference_sources import (
        SOURCES_NAME,
        parse_sources,
        read_sources_text,
    )
else:  # imported from a directly run tool
    from containment import open_regular_binary, require_within_repo, resolves_within
    from image_format import (
        image_stream_format,
        is_complete,
        is_image,
        LFS_POINTER_MAGIC,
    )
    from repo_root import ROOT
    from terminal import escape_controls
    from reference_sources import (
        SOURCES_NAME,
        parse_sources,
        read_sources_text,
    )

IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp"})

# Trailing bytes the declared-entry check reads for a stream's terminator.
# The longest format terminator is PNG's 12-byte IEND chunk; WebP needs only
# the head's declared size and the file length.
_TAIL_BYTES = 12

# How each named format's complete stream ends, for the truncation
# diagnostic. WebP is phrased from its declared and held sizes instead.
_FORMAT_TERMINATIONS = {
    "PNG": "ends without the PNG IEND trailer",
    "JPEG": "ends without the JPEG EOI marker",
    "GIF": "ends without the GIF trailer byte",
}


def _image_prefix(path: Path) -> bytes:
    """Read enough leading bytes to check both LFS and image signatures.

    The same bounded prefix is sufficient for both checks. Opening once also
    keeps the declared-image path from doing two filesystem opens per file.
    """
    with open_regular_binary(path) as handle:
        return handle.read(max(len(LFS_POINTER_MAGIC), 12))


def _image_head_and_tail(path: Path) -> tuple[bytes, bytes, int]:
    """Read a declared image's leading and trailing bytes in one open.

    The same open already reads the head the LFS-pointer and image-signature
    checks use; the tail carries a stream's terminator, so the completeness
    check needs no second open per declared file. When the file is shorter
    than the tail window the tail is simply the bytes actually present, and
    :func:`tools.image_format.is_complete` refuses them for every format
    whose complete stream is at least that long.
    """
    with open_regular_binary(path) as handle:
        head = handle.read(max(len(LFS_POINTER_MAGIC), _TAIL_BYTES))
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(size - _TAIL_BYTES, 0))
        return head, handle.read(_TAIL_BYTES), size


def _incomplete_stream_suffix(head: bytes, tail: bytes, size: int) -> str:
    """Return the diagnostic naming how the stream *head* identifies ends short."""
    stream = image_stream_format(head)
    if stream == "WebP":
        # The diagnostic names the declared RIFF field itself, the way it is
        # written in the container; is_complete adds the 8-byte RIFF header.
        declared = int.from_bytes(head[4:8], "little")
        return (
            f"declares {declared} RIFF bytes but holds {size}; "
            "it may be a truncated download"
        )
    return (
        f"{_FORMAT_TERMINATIONS[stream]}; "
        "it may be a truncated download"
    )


def _undeclared_image_problem(path: Path) -> str:
    """Describe an undeclared image while keeping its path terminal-safe."""
    return (
        f"{escape_controls(str(path))}: image has no entry in "
        f"{SOURCES_NAME}"
    )


def _check_entries(
    directory: Path, sources: Path, entries: dict[str, int]
) -> list[tuple[int, str]]:
    """Check accepted declarations against files in the reference directory."""
    problems: list[tuple[int, str]] = []
    for filename, lineno in entries.items():
        image = directory / filename
        safe_filename = escape_controls(filename)
        if not resolves_within(directory, image):
            problems.append(
                (lineno, f"{sources}:{lineno}: {safe_filename!r} points outside "
                 f"{directory}/ (a symlink escape)")
            )
            continue
        if not image.is_file():
            problems.append((lineno, f"{sources}:{lineno}: {filename!r} does not exist in {directory}/"))
            continue
        try:
            head, tail, size = _image_head_and_tail(image)
            if head.startswith(LFS_POINTER_MAGIC):
                problems.append(
                    (lineno, f"{sources}:{lineno}: {filename!r} is an unmaterialized Git LFS pointer; "
                     "run `git lfs install && git lfs pull` to fetch the image")
                )
            elif not is_image(head):
                # The unrecognized-payload diagnostic outranks a truncation
                # one: without a known format there is no ending to judge.
                problems.append(
                    (lineno, f"{sources}:{lineno}: {filename!r} is not a PNG, JPEG, GIF or WebP image; "
                     "it may be an HTML error page or a truncated download")
                )
            elif not is_complete(head, tail, size):
                problems.append(
                    (lineno,
                     f"{sources}:{lineno}: {filename!r} "
                     f"{_incomplete_stream_suffix(head, tail, size)}")
                )
        except (OSError, ValueError) as exc:
            problems.append((lineno, f"{sources}:{lineno}: {filename!r} could not be read: {exc}"))
    return problems


def _check_undeclared(directory: Path, entries: dict[str, int]) -> list[str]:
    """Return a problem for each image in *directory* that has no entry."""
    problems: list[str] = []
    try:
        listed = sorted(directory.iterdir())
    except OSError as exc:
        problems.append(f"{directory}: could not be listed: {exc}")
        return problems

    for path in listed:
        if path.name == SOURCES_NAME:
            continue
        if path.name in entries:
            continue
        if not path.is_file():
            # A non-regular entry is normally a directory and is skipped, but
            # a name that looks like an image is still an unexplained
            # reference-set entry: a dangling symlink or a symlink loop named
            # *.png, whose bytes cannot be sniffed. Report it by name rather
            # than let the set look consistent. Do not open it -- opening a
            # FIFO or device would block.
            if path.suffix.lower() in IMAGE_SUFFIXES:
                problems.append(_undeclared_image_problem(path))
            continue
        # A symlink can point anywhere on the machine, so refuse to read one
        # that resolves outside the reference directory; the declared-entry
        # loop makes the same check before opening an image. Without this, the
        # content sniff below would read a private file outside the set.
        if not resolves_within(directory, path):
            problems.append(
                f"{escape_controls(str(path))}: points outside {directory}/ "
                "(a symlink escape)"
            )
            continue
        # An image with no entry is undeclared whether or not its name marks
        # it as one: the bytes are checked too, so a screenshot saved without
        # an image extension (or a JPEG under a .bin name) is still caught.
        # Files with an image extension are flagged even when their bytes are
        # not an image, so a stray or half-downloaded file cannot hide behind
        # its name.
        try:
            has_image_bytes = is_image(_image_prefix(path))
        except (OSError, ValueError) as exc:
            problems.append(
                f"{escape_controls(str(path))}: could not be read: {exc}"
            )
            continue
        if path.suffix.lower() in IMAGE_SUFFIXES or has_image_bytes:
            problems.append(_undeclared_image_problem(path))

    return problems


def check_references(directory: Path) -> list[str]:
    """Return a list of human-readable problems in *directory*.

    An empty list means every source entry names an existing image, every image
    has exactly one entry, and every entry has the three expected fields with an
    absolute source URL.

    The reference directory is contributor-supplied too: git stores a symlink,
    so ``macos8.6-screenshots`` itself can be a symlink to a directory outside
    the repository. Every containment check below uses *directory* as its base,
    so with such a symlink every path under the target would count as
    contained: the checker would list the target directory and read its
    ``sources.txt``, echoing that file's lines into the problem list the CLI
    prints. The directory is therefore refused when it resolves outside the
    repository, before anything inside it is touched. A directory outside the
    repository (a test's temporary reference set) is left alone.
    """
    try:
        require_within_repo(directory, ROOT)
    except ValueError as exc:
        return [escape_controls(str(exc))]
    sources = directory / SOURCES_NAME
    if not resolves_within(directory, sources):
        return [f"{sources}: points outside {directory}/ (a symlink escape)"]
    if not sources.is_file():
        return [f"{sources}: missing sources file"]

    sources_text, read_problem = read_sources_text(sources)
    if sources_text is None:
        return [read_problem]

    parse_problems, entries = parse_sources(directory, sources, sources_text)
    entry_problems = _check_entries(directory, sources, entries)
    ordered = sorted(parse_problems + entry_problems, key=lambda item: item[0])
    return [problem for _, problem in ordered] + _check_undeclared(directory, entries)
