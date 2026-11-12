"""Sample RGB pixels and regions from reference screenshots."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

if __package__:
    from tools.containment import resolves_within
    from tools.diagnostics import report_error
    from tools.jpeg_convert import JPEG_MAGIC, convert_jpeg, is_jpeg
    from tools.png import PngError, pixel_at, read_png, read_png_size  # noqa: F401
    from tools.repo_root import ROOT
    from tools.sample_arguments import build_parser, option_error, region_error
    from tools.sample_reports import report
    from tools.sample_report_common import format_image_header
else:  # run directly: python3 tools/sample.py
    from containment import resolves_within
    from diagnostics import report_error
    from jpeg_convert import JPEG_MAGIC, convert_jpeg, is_jpeg
    from png import PngError, pixel_at, read_png, read_png_size  # noqa: F401
    from repo_root import ROOT
    from sample_arguments import build_parser, option_error, region_error
    from sample_reports import report
    from sample_report_common import format_image_header


def _read_entire(fd: int) -> bytes:
    """Read the open regular file *fd* whole through its stable handle.

    The bytes come off the same handle the sniffer sniffed, so a concurrent
    directory swap cannot supply different bytes to the conversion.
    """
    chunks: list[bytes] = []
    position = 0
    while True:
        chunk = os.pread(fd, 1 << 20, position)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        position += len(chunk)


def _sample_jpeg(args, fd: int) -> int:
    """Decode a JPEG input into a private temporary PNG and sample it.

    The conversion writes into a private temporary directory, never the
    input's own, so the user's tree is untouched and no planted path is
    followed. Every failure reports the path the operator gave, and a decode
    failure's message is scrubbed of the temporary path the way the
    ``/proc/self/fd`` rewrite above carries the operator's name instead of
    the stable handle's.
    """
    directory = tempfile.mkdtemp(prefix="sample-jpeg-")
    temp_png = Path(directory) / "decoded.png"
    try:
        problem = convert_jpeg(_read_entire(fd), temp_png)
        if problem is not None:
            return report_error(
                "sample", f"cannot decode {args.image}: {problem}"
            )
        try:
            width, height = read_png_size(str(temp_png))
            message = region_error(args, width, height)
            if message is not None:
                return report_error("sample", message)
            image = read_png(str(temp_png), max_rows=args.y + args.height)
        except PngError as exc:
            return report_error(
                "sample", str(exc).replace(str(temp_png), args.image)
            )
    finally:
        shutil.rmtree(directory, ignore_errors=True)
    header = format_image_header(args.image, width, height)
    report(args, image, width, height, header)
    return 0


def _jpeg_alpha_refusal(args) -> str | None:
    """Return the refusal for alpha options given a JPEG input, else None.

    A JPEG carries no alpha channel to sample or match, so these refusals
    fire before any conversion runs.
    """
    if args.alpha:
        return "--alpha requires a PNG input: a JPEG image carries no alpha channel"
    if args.match_alpha is not None:
        return "--match-alpha requires a PNG input: a JPEG image carries no alpha channel"
    return None


def _jpeg_report(args: argparse.Namespace, fd: int) -> int | None:
    """Sample an open JPEG handle, or return None if it is not a JPEG.

    The alpha refusals are checked before the decode: the JPEG loader would
    otherwise convert the image's alpha plane away first.
    """
    if not is_jpeg(os.pread(fd, len(JPEG_MAGIC), 0)):
        return None
    refusal = _jpeg_alpha_refusal(args)
    if refusal is not None:
        return report_error("sample", refusal)
    return _sample_jpeg(args, fd)


def main(argv: list[str] | None = None) -> int:
    """Validate and load the requested region, then dispatch its report."""
    args = build_parser().parse_args(argv)
    message = option_error(args)
    if message is not None:
        return report_error("sample", message)

    # Open once, then check the opened object itself. Checking a pathname and
    # reopening it later would let a concurrent symlink swap bypass containment.
    image_path = Path(os.path.join(os.getcwd(), args.image))
    in_repo = False
    for ancestor in (image_path, *image_path.parents):
        try:
            in_repo = os.path.samefile(ancestor, ROOT)
        except OSError:
            continue
        if in_repo:
            break
    try:
        fd = os.open(args.image, os.O_RDONLY | os.O_NONBLOCK)
        try:
            # Linux procfs exposes the resolved target of this stable handle.
            # The PNG loader reopens that handle path, which cannot follow a
            # replacement of the original directory entry.
            opened_path = f"/proc/self/fd/{fd}" if in_repo else args.image
            if in_repo and not resolves_within(ROOT, opened_path):
                return report_error(
                    "sample", f"{args.image} resolves outside {ROOT} (a symlink escape); refusing to read it"
                )
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                return report_error("sample", f"cannot read {args.image}: not a regular file")
            # Sniff the bytes on the already-open stable handle, so a
            # concurrent symlink swap cannot change what is decoded.
            jpeg_result = _jpeg_report(args, fd)
            if jpeg_result is not None:
                return jpeg_result
            width, height = read_png_size(opened_path)
            message = region_error(args, width, height)
            if message is not None:
                return report_error("sample", message)
            image = read_png(opened_path, max_rows=args.y + args.height,
                             **({"alpha": True} if args.alpha or args.match_alpha is not None else {}))
        finally:
            os.close(fd)
    except OSError as exc:
        return report_error("sample", f"cannot read {args.image}: {exc}")
    except PngError as exc:
        message = str(exc)
        if opened_path != args.image:
            # The reads go through the stable /proc/self/fd handle so a
            # concurrent symlink swap cannot redirect them; a decode failure
            # carrying that handle name would still tell the operator nowhere
            # they typed, so the message names the path they gave instead,
            # like the read and containment refusals above.
            message = message.replace(opened_path, args.image)
        return report_error("sample", message)
    header = format_image_header(args.image, width, height)
    report(args, image, width, height, header)
    return 0


if __name__ == "__main__":
    sys.exit(main())
