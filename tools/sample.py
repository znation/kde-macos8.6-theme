"""Sample RGB pixels and regions from reference PNG files."""

from __future__ import annotations

import os
from pathlib import Path
import sys

if __package__:
    from tools.containment import resolves_within
    from tools.diagnostics import report_error
    from tools.png import PngError, pixel_at, read_png, read_png_size  # noqa: F401
    from tools.repo_root import ROOT
    from tools.sample_arguments import build_parser
    from tools.sample_reports import report
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/sample.py
    from containment import resolves_within
    from diagnostics import report_error
    from png import PngError, pixel_at, read_png, read_png_size  # noqa: F401
    from repo_root import ROOT
    from sample_arguments import build_parser
    from sample_reports import report
    from terminal import escape_controls


def main(argv: list[str] | None = None) -> int:
    """Validate and load the requested region, then dispatch its report."""
    args = build_parser().parse_args(argv)
    if args.top_colors is not None and not args.histogram:
        return report_error("sample", "--top-colors requires --histogram")
    if args.color_bounds and not args.histogram:
        return report_error("sample", "--color-bounds requires --histogram")
    if args.color_fractions and not args.histogram:
        return report_error("sample", "--color-fractions requires --histogram")
    if args.color_tolerance is not None and args.find_color is None:
        return report_error("sample", "--color-tolerance requires --find-color")
    if args.match_alpha is not None and args.find_color is None:
        return report_error("sample", "--match-alpha requires --find-color")
    if args.match_pixels is not None and args.find_color is None:
        return report_error("sample", "--match-pixels requires --find-color")
    if args.match_fraction and args.find_color is None:
        return report_error("sample", "--match-fraction requires --find-color")
    if args.runs and args.width > 1 and args.height > 1:
        return report_error("sample", "--runs requires a single row or column")
    if args.alpha and args.find_color is not None:
        return report_error("sample", "--alpha cannot be combined with --find-color")

    # A checked-in link that escapes the repository could expose a private
    # image through its pixels, so refuse it before either read.
    image_path = Path(os.path.join(os.getcwd(), args.image))
    for ancestor in (image_path, *image_path.parents):
        try:
            in_repo = os.path.samefile(ancestor, ROOT)
        except OSError:
            continue
        if in_repo:
            if not resolves_within(ROOT, image_path):
                return report_error(
                    "sample", f"{args.image} resolves outside {ROOT} (a symlink escape); refusing to read it"
                )
            break

    try:
        width, height = read_png_size(args.image)
    except PngError as exc:
        return report_error("sample", str(exc))

    if args.width == 1 and args.height == 1:
        if not (0 <= args.x < width and 0 <= args.y < height):
            return report_error("sample", f"pixel ({args.x}, {args.y}) is outside the {width}x{height} image")
    elif (args.x < 0 or args.y < 0 or args.x + args.width > width or args.y + args.height > height):
        return report_error(
            "sample", f"region ({args.x}, {args.y}) {args.width}x{args.height} is outside the {width}x{height} image"
        )

    try:
        image = read_png(args.image, max_rows=args.y + args.height,
                         **({"alpha": True} if args.alpha or args.match_alpha is not None else {}))
    except PngError as exc:
        return report_error("sample", str(exc))
    header = f"image: {escape_controls(args.image)}  {width}x{height}"
    report(args, image, width, height, header)
    return 0


if __name__ == "__main__":
    sys.exit(main())
