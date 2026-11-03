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

    message = region_error(args, width, height)
    if message is not None:
        return report_error("sample", message)

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
