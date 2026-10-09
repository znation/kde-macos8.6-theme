#!/usr/bin/env python3
"""Check that the Mac OS 8.6 reference screenshot set is self-consistent.

``macos8.6-screenshots/sources.txt`` is the provenance record for the reference
set: one ``<filename> | <source URL> | <version label>`` line per image. This
script verifies that record against the files actually on disk, so a renamed or
forgotten image cannot silently drop out of the evidence trail. It also rejects
unmaterialized Git LFS pointer files, files whose bytes are not a known image
format (such as an HTML error page saved under an image name), and source URLs
that are not well-formed absolute URLs (a bare host, a relative path, or a raw
space is a broken citation).

Usage:
    python3 tools/check_references.py              # check the repository
    python3 tools/check_references.py --self-test  # exercise the checks
    python3 tools/check_references.py --help       # show usage
"""

from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
from pathlib import Path

try:
    from tools.image_format import (
        JPEG_MAGIC,
        LFS_POINTER_MAGIC,
        PNG_MAGIC,
        is_image,
    )
    from tools.terminal import escape_controls
except ImportError:  # run directly: python3 tools/check_references.py
    from image_format import (
        JPEG_MAGIC,
        LFS_POINTER_MAGIC,
        PNG_MAGIC,
        is_image,
    )
    from terminal import escape_controls

REFERENCE_DIR = "macos8.6-screenshots"
SOURCES_NAME = "sources.txt"
IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp"})
SEPARATOR = " | "
# Only CR, LF and CRLF end a sources.txt line. ``str.splitlines`` also breaks
# on U+2028/U+2029, NEL and the C0 separators, so a version label containing
# one would split into a phantom line and be reported as a malformed entry.
_LINE_BREAK = re.compile(r"\r\n|\r|\n")
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
    return is_image(head)


# RFC 3986 scheme: ALPHA *( ALPHA / DIGIT / "+" / "-" / "." ). Any other
# character (a space from a copy-paste, a stray "!") means the token is not a
# scheme, however absolute the rest of the URL looks.
_SCHEME_PUNCTUATION = frozenset("+-.")

# Schemes whose host may legitimately be empty: ``file:///path`` names no
# host, while a network scheme with an empty host (``https:///path``) is a
# citation with nowhere to point.
_SCHEMES_ALLOWING_EMPTY_HOST = frozenset({"file"})


def _url_problem(url: str) -> str | None:
    """Return why *url* is not a well-formed absolute URL, or None when it is.

    A provenance source is an absolute URL, so a bare host or a relative path
    (``example.test/x.png``) is a broken citation even though it is non-empty.
    The scheme must follow RFC 3986 (``ALPHA *( ALPHA / DIGIT / "+" / "-" /
    "." )``), the URL must contain no raw whitespace or control character
    (which belong percent-encoded), and the authority between ``://`` and the
    path must name a host unless the scheme is ``file``. The rules catch broken
    citations that a first-character-only scheme test accepts: ``ht!tp://x``,
    ``https://example.test/a b.png``, ``https:///image.png`` and
    ``https://user@/image.png``.

    The failures are returned separately because the fix differs: a URL with no
    (or a malformed) scheme needs a source, one whose scheme is fine but which
    carries a space or control character only needs that character
    percent-encoded, and one with an empty authority needs a host. Blaming the
    scheme for the latter two sends the reader after the wrong thing.
    """
    scheme, sep, rest = url.partition("://")
    if (
        not (sep and rest)
        or not scheme.isascii()
        or not scheme[:1].isalpha()
        or not all(ch.isalnum() or ch in _SCHEME_PUNCTUATION for ch in scheme)
    ):
        return (
            "must be an absolute URL with a valid scheme, "
            "e.g. https://example.test/image.png"
        )
    if not all(ch.isprintable() and not ch.isspace() for ch in url):
        return "must not contain whitespace or control characters; percent-encode them"
    # The authority runs to the first ``/``, ``?`` or ``#``. Its host is what
    # remains after any ``userinfo@`` prefix and ``:port`` suffix, so an
    # authority that is empty, or holds only userinfo or only a port, names no
    # host at all (``scheme:///path``, ``scheme://@/path``, ``scheme://:80/p``).
    authority = rest.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    host = authority.rsplit("@", 1)[-1].split(":", 1)[0]
    if not host and scheme.lower() not in _SCHEMES_ALLOWING_EMPTY_HOST:
        return (
            "must name a host between the scheme and the path "
            "(only file:// URLs may omit it), "
            "e.g. https://example.test/image.png"
        )
    return None


def _is_absolute_url(url: str) -> bool:
    """Return True when *url* is a well-formed absolute URL.

    See :func:`_url_problem`, which this wraps, for the rules and the reason a
    URL can fail.
    """
    return _url_problem(url) is None


def _resolves_within(directory: Path, path: Path) -> bool:
    """Return True when *path* resolves to a location inside *directory*.

    The reference directory is contributor-supplied, and a checked-in symlink
    can point anywhere on the machine: a ``sources.txt`` symlink to a private
    file would make the checker read that file and print its lines as
    diagnostics. Resolving both paths keeps every read inside the reference
    directory even when a symlink tries to leave it. A resolution that fails
    is not assumed to be contained: an ``OSError`` (a filesystem failure) and
    a ``RuntimeError`` (the symlink loop ``Path.resolve()`` raised before
    Python 3.13) both make this return False, so the caller reports the path
    instead of the exception aborting the whole check.
    """
    try:
        return path.resolve().is_relative_to(directory.resolve())
    except (OSError, RuntimeError):
        return False


def check_references(directory: Path) -> list[str]:
    """Return a list of human-readable problems in *directory*.

    An empty list means every source entry names an existing image, every image
    has exactly one entry, and every entry has the three expected fields with an
    absolute source URL.
    """
    sources = directory / SOURCES_NAME
    if not _resolves_within(directory, sources):
        return [f"{sources}: points outside {directory}/ (a symlink escape)"]
    if not sources.is_file():
        return [f"{sources}: missing sources file"]

    try:
        # utf-8-sig strips a leading UTF-8 BOM that an editor may have added.
        # The BOM is invisible, so decoding as plain UTF-8 folds it into the
        # first filename and the check reports a phantom missing file instead
        # of the real one, which then looks undeclared.
        sources_text = sources.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return [f"{sources}: could not be read: {exc}"]
    except UnicodeDecodeError as exc:
        return [f"{sources}: not valid UTF-8 text: {exc}"]

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
        url_problem = _url_problem(url)
        if url_problem is not None:
            problems.append(
                f"{sources}:{lineno}: source URL {url!r} {url_problem}"
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
        if not _resolves_within(directory, path):
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


def _problems_match(problems: list[str], expected: list[str]) -> bool:
    """Return True when *expected* matches *problems* exactly.

    Each expected substring must match a distinct problem and no problem may be
    left unmatched, so a fixture that emits an extra diagnostic -- not merely
    one that omits an expected problem -- fails the self-test.
    """
    remaining = list(problems)
    for needle in expected:
        for index, problem in enumerate(remaining):
            if needle in problem:
                del remaining[index]
                break
        else:
            return False
    return not remaining


def _self_test() -> int:
    """Run the checker against small fixtures; return 0 when all behave."""
    cases = [
        # (name, sources.txt contents or None to omit the file, files on disk as
        #  (filename, content) pairs, expected problems: None for a clean set, or
        #  one substring per problem the checker must report -- exactly that many,
        #  each matched by a distinct problem)
        ("clean", "good.png | https://example.test/g.png | Mac OS 8.6 (desktop)\n",
         [("good.png", PNG_MAGIC)], None),
        # An editor-added UTF-8 BOM is invisible: stripping it keeps the first
        # entry readable instead of folding the BOM into its filename.
        ("utf-8 BOM before the first entry",
         "\ufeffgood.png | https://example.test/g.png | Mac OS 8.6 (desktop)\n",
         [("good.png", PNG_MAGIC)], None),
        # U+2028 is a Unicode line separator, not a newline: a label that
        # contains one must stay on its own line instead of splitting into a
        # phantom second entry.
        ("label containing U+2028 stays one line",
         "good.png | https://example.test/g.png | Mac OS 8.6\u2028retail\n",
         [("good.png", PNG_MAGIC)], None),
        ("missing sources file", None, [("good.png", PNG_MAGIC)],
         ["missing sources file"]),
        ("comments and blank lines",
         "# provenance\n\ngood.png | https://example.test/x | l\n# trailing note\n",
         [("good.png", PNG_MAGIC)], None),
        ("missing file", "ghost.png | https://example.test/g.png | label\n", [],
         ["ghost.png"]),
        # A rejected entry never registers the filename, so the image on disk is
        # reported a second time as undeclared; the self-test pins that cascade.
        ("url with no scheme", "bad.png | example.test/b.png | label\n",
         [("bad.png", PNG_MAGIC)], ["absolute URL", "bad.png: image has no entry"]),
        ("url with a malformed scheme", "bad.png | ht!tp://example.test/b.png | label\n",
         [("bad.png", PNG_MAGIC)], ["absolute URL", "bad.png: image has no entry"]),
        # The scheme is valid, so the diagnostic must name the whitespace, not
        # the scheme, or it sends the reader after the wrong thing.
        ("url with raw whitespace", "bad.png | https://example.test/a b.png | label\n",
         [("bad.png", PNG_MAGIC)],
         ["whitespace or control", "bad.png: image has no entry"]),
        ("url with a control character",
         "bad.png | https://example.test/a\x01b.png | label\n",
         [("bad.png", PNG_MAGIC)],
         ["whitespace or control", "bad.png: image has no entry"]),
        # An empty authority (``https:///b.png``) names no host, so the citation
        # points nowhere; only file:// may legitimately omit it.
        ("url with an empty authority", "bad.png | https:///b.png | label\n",
         [("bad.png", PNG_MAGIC)],
         ["must name a host", "bad.png: image has no entry"]),
        # An authority can be non-empty yet still name no host: ``user@`` is
        # userinfo and ``:8080`` is a port, each with an empty host.
        ("url with an authority but no host",
         "bad.png | https://user@/b.png | label\n",
         [("bad.png", PNG_MAGIC)],
         ["must name a host", "bad.png: image has no entry"]),
        ("path in filename", "sub/good.png | https://example.test/x | l\n",
         [("sub/good.png", PNG_MAGIC)], ["bare filename"]),
        ("undeclared image", "", [("extra.png", PNG_MAGIC)], ["extra.png"]),
        # No image extension, but the bytes are a PNG: the scan must read the
        # content, not trust the name, or this file drops out of provenance.
        ("undeclared extensionless image", "", [("stray", PNG_MAGIC)], ["stray"]),
        ("undeclared jpeg misnamed as data", "",
         [("shot.bin", JPEG_MAGIC)], ["shot.bin"]),
        ("too few fields", "bad.png | https://example.test/b.png\n",
         [("bad.png", PNG_MAGIC)],
         ["expected 3 fields", "bad.png: image has no entry"]),
        ("empty field", "bad.png |  | label\n", [("bad.png", PNG_MAGIC)],
         ["empty field", "bad.png: image has no entry"]),
        ("duplicate",
         "dup.png | https://example.test/x | l\n"
         "dup.png | https://example.test/x | l\n",
         [("dup.png", PNG_MAGIC)], ["duplicate"]),
        ("lfs pointer", "stub.png | https://example.test/x | l\n",
         [("stub.png", b"version https://git-lfs.github.com/spec/v1\n"
                       b"oid sha256:deadbeef\nsize 12345\n")],
         ["Git LFS pointer"]),
        ("non-image payload", "fake.png | https://example.test/x | l\n",
         [("fake.png", b"<!DOCTYPE html>\n<html>404 Not Found</html>\n")],
         ["not a PNG, JPEG, GIF or WebP image"]),
        ("webp with jpg name", "shot.jpg | https://example.test/x | l\n",
         [("shot.jpg", b"RIFF\x24\x00\x00\x00WEBPVP8 ")], None),
    ]

    failed = False
    for name, sources_text, images, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            if sources_text is not None:
                (root / SOURCES_NAME).write_text(sources_text, encoding="utf-8")
            for filename, content in images:
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            problems = check_references(root)
        if expected is None:
            if problems:
                failed = True
                print(f"self-test {name!r}: expected no problems, got {problems}")
        elif not _problems_match(problems, expected):
            failed = True
            print(
                f"self-test {name!r}: expected problems matching {expected!r}, "
                f"got {problems!r}"
            )

    # Argument handling: --help prints usage and exits 0; anything unrecognized
    # exits 2 rather than silently running the repository check on a typo.
    cli_cases = [
        (["--help"], 0, "usage:"),
        (["-h"], 0, "usage:"),
        (["--self-tests"], 2, "unknown argument"),
    ]
    for argv, expected_code, needle in cli_cases:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        combined = out.getvalue() + err.getvalue()
        if code != expected_code or needle not in combined:
            failed = True
            print(
                f"self-test cli {argv!r}: expected exit {expected_code} with {needle!r}, "
                f"got exit {code}: {combined!r}"
            )

    if failed:
        return 1
    print(f"self-test: {len(cases) + len(cli_cases)} cases passed")
    return 0


def _plural(count: int, singular: str) -> str:
    """Return *singular*, pluralized with ``s`` when *count* is not one.

    Both count-bearing diagnostics this module prints (the unknown-argument
    error and the problem summary) read as broken English when a single item
    is followed by ``(s)``; this picks the form from the actual count.
    """
    return singular if count == 1 else singular + "s"


def main(argv: list[str] | None = None) -> int:
    """Run the checker; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/fidelity.py``, ``None``
    reads ``sys.argv``. A caller that passes ``["--help"]`` gets usage instead
    of having its first real argument silently dropped as a program name and
    the repository check run instead.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--self-test"]:
        return _self_test()
    if args in (["-h"], ["--help"]):
        print(USAGE, end="")
        return 0
    if args:
        print(
            f"error: unknown {_plural(len(args), 'argument')}: "
            f"{escape_controls(' '.join(args))}",
            file=sys.stderr,
        )
        print(USAGE, end="", file=sys.stderr)
        return 2

    directory = Path(__file__).resolve().parent.parent / REFERENCE_DIR
    problems = check_references(directory)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(
            f"{len(problems)} {_plural(len(problems), 'problem')} "
            "in the reference set",
            file=sys.stderr,
        )
        return 1
    print(f"{directory}: reference set is consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
