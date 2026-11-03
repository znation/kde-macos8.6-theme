"""Sample RGB pixels and regions from reference PNG files."""

from __future__ import annotations

import os
from pathlib import Path
import stat
import sys

if __package__:
    from tools.containment import resolves_within
    from tools.diagnostics import report_error
    from tools.png import PngError, pixel_at, read_png, read_png_size  # noqa: F401
    from tools.repo_root import ROOT
    from tools.sample_arguments import build_parser, option_error, region_error
    from tools.sample_reports import report
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/sample.py
    from containment import resolves_within
    from diagnostics import report_error
    from png import PngError, pixel_at, read_png, read_png_size  # noqa: F401
    from repo_root import ROOT
    from sample_arguments import build_parser, option_error, region_error
    from sample_reports import report
    from terminal import escape_controls


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
            width, height = read_png_size(opened_path)
            message = region_error(args, width, height)
            if message is not None:
                return report_error("sample", message)
            image = read_png(opened_path, max_rows=args.y + args.height,
                             **({"alpha": True} if args.alpha or args.match_alpha is not None else {}))
        finally:
            os.close(fd)
    except OSError:
        return report_error("sample", f"cannot read {args.image}")
    except PngError as exc:
        return report_error("sample", str(exc))
    header = f"image: {escape_controls(args.image)}  {width}x{height}"
    report(args, image, width, height, header)
    return 0


if __name__ == "__main__":
    sys.exit(main())
