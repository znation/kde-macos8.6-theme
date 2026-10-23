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

import re
from pathlib import Path

if __package__:
    from tools.containment import require_within_repo, resolves_within
    from tools.image_format import LFS_POINTER_MAGIC, is_image
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
    from tools.url_check import url_problem
else:  # imported from a directly run tool
    from containment import require_within_repo, resolves_within
    from image_format import LFS_POINTER_MAGIC, is_image
    from repo_root import ROOT
    from terminal import escape_controls
    from url_check import url_problem

SOURCES_NAME = "sources.txt"
IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp"})
SEPARATOR = " | "
# The provenance record is contributor-supplied, so a checked-in (or LFS-
# smudged) multi-gigabyte sources.txt must not be loaded whole: read_text()
# would allocate it and exhaust memory instead of reporting a diagnostic.
# The real file is a few kilobytes; 1 MiB leaves ample room for growth while
# bounding the read the way read_png bounds an oversize image.
_MAX_SOURCES_BYTES = 1 << 20
# Only CR, LF and CRLF end a sources.txt line. ``str.splitlines`` also breaks
# on U+2028/U+2029, NEL and the C0 separators, so a version label containing
# one would split into a phantom line and be reported as a malformed entry.
_LINE_BREAK = re.compile(r"\r\n|\r|\n")


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
    return is_image(head)


def _read_sources_text(sources: Path) -> tuple[str | None, str | None]:
    """Return ``(text, None)`` for the provenance record, or ``(None, problem)``."""
    try:
        # Read at most one byte past the cap, so an oversize file is detected
        # without loading the rest of it, then decode the bytes. utf-8-sig
        # strips a leading UTF-8 BOM that an editor may have added: the BOM is
        # invisible, so decoding as plain UTF-8 folds it into the first
        # filename and the check reports a phantom missing file instead of the
        # real one, which then looks undeclared.
        with sources.open("rb") as handle:
            data = handle.read(_MAX_SOURCES_BYTES + 1)
    except OSError as exc:
        return None, f"{sources}: could not be read: {exc}"
    if len(data) > _MAX_SOURCES_BYTES:
        return None, (
            f"{sources}: is larger than the {_MAX_SOURCES_BYTES}-byte limit "
            "for a provenance record"
        )
    try:
        return data.decode("utf-8-sig"), None
    except UnicodeDecodeError as exc:
        return None, f"{sources}: not valid UTF-8 text: {exc}"


def _check_entries(
    directory: Path, sources: Path, sources_text: str
) -> tuple[list[str], dict[str, int]]:
    """Validate each ``sources.txt`` entry; return ``(problems, entries)``.

    ``entries`` maps each accepted filename to the line it was declared on.
    """
    problems: list[str] = []
    entries: dict[str, int] = {}

    for lineno, raw in enumerate(_LINE_BREAK.split(sources_text), 1):
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
        if "\x00" in filename:
            # A NUL byte cannot appear in a POSIX path, and Path.resolve()
            # raises ValueError on one; reject it here so a malformed entry
            # becomes a diagnostic instead of aborting the whole check.
            problems.append(
                f"{sources}:{lineno}: {filename!r} contains a NUL byte and "
                "cannot name a file"
            )
            continue
        problem = url_problem(url)
        if problem is not None:
            problems.append(
                f"{sources}:{lineno}: source URL {url!r} {problem}"
            )
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
        if not resolves_within(directory, image):
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

    return problems, entries


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
                problems.append(
                    f"{escape_controls(str(path))}: image has no entry in "
                    f"{SOURCES_NAME}"
                )
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
            has_image_bytes = _looks_like_image(path)
        except OSError as exc:
            problems.append(
                f"{escape_controls(str(path))}: could not be read: {exc}"
            )
            continue
        if path.suffix.lower() in IMAGE_SUFFIXES or has_image_bytes:
            problems.append(
                f"{escape_controls(str(path))}: image has no entry in {SOURCES_NAME}"
            )

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

    sources_text, read_problem = _read_sources_text(sources)
    if sources_text is None:
        return [read_problem]

    problems, entries = _check_entries(directory, sources, sources_text)
    return problems + _check_undeclared(directory, entries)
