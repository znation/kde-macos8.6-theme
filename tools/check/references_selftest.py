"""Built-in fixtures for ``tools/check_references.py --self-test``.

The checker's own checks are exercised against small throwaway reference sets.
The checker passes in its entry points (``check_references`` and ``main``) and
the ``sources.txt`` filename rather than this module importing them, so the
dependency runs one way and a caller that replaces ``check_references`` on the
checker module changes what the self-test runs.
"""

from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path
from typing import Callable

try:
    from tools.image_format import JPEG_MAGIC, PNG_MAGIC, TERMINAL_PNG
except ImportError:  # imported from a directly run tool
    from image_format import JPEG_MAGIC, PNG_MAGIC, TERMINAL_PNG

# Complete minimal stream bodies: a leading signature plus its format's
# terminator, so a fixture that must misbehave has to fail on some other
# check instead of tripping the ending rules every real image satisfies.
PNG_IMAGE = PNG_MAGIC + TERMINAL_PNG
WEBP_IMAGE = b"RIFF" + (4).to_bytes(4, "little") + b"WEBP"


def problems_match(problems: list[str], expected: list[str]) -> bool:
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


def run_self_test(
    check_references: Callable[[Path], list[str]],
    main: Callable[[list[str]], int],
    sources_name: str,
) -> int:
    """Run the checker against small fixtures; return 0 when all behave."""
    cases = [
        # (name, sources.txt contents or None to omit the file, files on disk as
        #  (filename, content) pairs, expected problems: None for a clean set, or
        #  one substring per problem the checker must report -- exactly that many,
        #  each matched by a distinct problem)
        ("clean", "good.png | https://example.test/g.png | Mac OS 8.6 (desktop)\n",
         [("good.png", PNG_IMAGE)], None),
        # An editor-added UTF-8 BOM is invisible: stripping it keeps the first
        # entry readable instead of folding the BOM into its filename.
        ("utf-8 BOM before the first entry",
         "\ufeffgood.png | https://example.test/g.png | Mac OS 8.6 (desktop)\n",
         [("good.png", PNG_IMAGE)], None),
        # U+2028 is a Unicode line separator, not a newline: a label that
        # contains one must stay on its own line instead of splitting into a
        # phantom second entry.
        ("label containing U+2028 stays one line",
         "good.png | https://example.test/g.png | Mac OS 8.6\u2028retail\n",
         [("good.png", PNG_IMAGE)], None),
        ("missing sources file", None, [("good.png", PNG_IMAGE)],
         ["missing sources file"]),
        ("comments and blank lines",
         "# provenance\n\ngood.png | https://example.test/x | l\n# trailing note\n",
         [("good.png", PNG_IMAGE)], None),
        ("missing file", "ghost.png | https://example.test/g.png | label\n", [],
         ["ghost.png"]),
        # A rejected entry never registers the filename, so the image on disk is
        # reported a second time as undeclared; the self-test pins that cascade.
        ("url with no scheme", "bad.png | example.test/b.png | label\n",
         [("bad.png", PNG_IMAGE)], ["absolute URL", "bad.png: image has no entry"]),
        ("url with a malformed scheme", "bad.png | ht!tp://example.test/b.png | label\n",
         [("bad.png", PNG_IMAGE)], ["absolute URL", "bad.png: image has no entry"]),
        # The scheme is valid, so the diagnostic must name the whitespace, not
        # the scheme, or it sends the reader after the wrong thing.
        ("url with raw whitespace", "bad.png | https://example.test/a b.png | label\n",
         [("bad.png", PNG_IMAGE)],
         ["whitespace or control", "bad.png: image has no entry"]),
        ("url with a control character",
         "bad.png | https://example.test/a\x01b.png | label\n",
         [("bad.png", PNG_IMAGE)],
         ["whitespace or control", "bad.png: image has no entry"]),
        # An empty authority (``https:///b.png``) names no host, so the citation
        # points nowhere; only file:// may legitimately omit it.
        ("url with an empty authority", "bad.png | https:///b.png | label\n",
         [("bad.png", PNG_IMAGE)],
         ["must name a host", "bad.png: image has no entry"]),
        # An authority can be non-empty yet still name no host: ``user@`` is
        # userinfo and ``:8080`` is a port, each with an empty host.
        ("url with an authority but no host",
         "bad.png | https://user@/b.png | label\n",
         [("bad.png", PNG_IMAGE)],
         ["must name a host", "bad.png: image has no entry"]),
        ("path in filename", "sub/good.png | https://example.test/x | l\n",
         [("sub/good.png", PNG_IMAGE)], ["bare filename"]),
        ("undeclared image", "", [("extra.png", PNG_MAGIC)], ["extra.png"]),
        # No image extension, but the bytes are a PNG: the scan must read the
        # content, not trust the name, or this file drops out of provenance.
        ("undeclared extensionless image", "", [("stray", PNG_MAGIC)], ["stray"]),
        ("undeclared jpeg misnamed as data", "",
         [("shot.bin", JPEG_MAGIC)], ["shot.bin"]),
        ("too few fields", "bad.png | https://example.test/b.png\n",
         [("bad.png", PNG_IMAGE)],
         ["expected 3 fields", "bad.png: image has no entry"]),
        ("empty field", "bad.png |  | label\n", [("bad.png", PNG_IMAGE)],
         ["empty field", "bad.png: image has no entry"]),
        ("duplicate",
         "dup.png | https://example.test/x | l\n"
         "dup.png | https://example.test/x | l\n",
         [("dup.png", PNG_IMAGE)], ["duplicate"]),
        ("lfs pointer", "stub.png | https://example.test/x | l\n",
         [("stub.png", b"version https://git-lfs.github.com/spec/v1\n"
                       b"oid sha256:deadbeef\nsize 12345\n")],
         ["Git LFS pointer"]),
        ("non-image payload", "fake.png | https://example.test/x | l\n",
         [("fake.png", b"<!DOCTYPE html>\n<html>404 Not Found</html>\n")],
         ["not a PNG, JPEG, GIF or WebP image"]),
        ("webp with jpg name", "shot.jpg | https://example.test/x | l\n",
         [("shot.jpg", WEBP_IMAGE)], None),
        # A stream cut short can end in valid image bytes when the signature
        # survives: the ending rules must catch each one at validation time.
        ("truncated png", "cut.png | https://example.test/x | l\n",
         [("cut.png", PNG_MAGIC)],
         ["ends without the PNG IEND trailer; it may be a truncated download"]),
        ("truncated jpeg", "cut.jpg | https://example.test/x | l\n",
         [("cut.jpg", JPEG_MAGIC)],
         ["ends without the JPEG EOI marker"]),
        ("truncated gif", "cut.gif | https://example.test/x | l\n",
         [("cut.gif", b"GIF89a")],
         ["ends without the GIF trailer byte"]),
        ("truncated webp", "cut.webp | https://example.test/x | l\n",
         [("cut.webp", b"RIFF" + (64).to_bytes(4, "little") + b"WEBP")],
         ["declares 64 RIFF bytes but holds 12; it may be a truncated download"]),
    ]

    failed = False
    for name, sources_text, images, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            if sources_text is not None:
                (root / sources_name).write_text(sources_text, encoding="utf-8")
            for filename, content in images:
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            problems = check_references(root)
        if expected is None:
            if problems:
                failed = True
                print(f"self-test {name!r}: expected no problems, got {problems}")
        elif not problems_match(problems, expected):
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
