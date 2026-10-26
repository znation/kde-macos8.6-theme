"""Command-line fidelity comparison for the Mac OS 8.6 Plasma theme.

Compares a rendered PNG surface against a reference screenshot and reports the
comparison metrics from the sibling ``tools/fidelity_metrics.py``: mean
absolute error, per-channel mean absolute error (R, G, B, A), RMSE, the worst
per-channel delta and where it occurs, and the fraction of differing pixels.

Only PNG is read, so the harness crops a reference screenshot to a surface and
saves it as PNG before comparing. The Plasma render step that produces the
candidate image is outside this tool; ``tools/render_surface.py`` does it.

Usage::

    python3 tools/fidelity.py CANDIDATE REFERENCE [--candidate-crop X,Y,W,H]
        [--crop X,Y,W,H] [--max-mae F] [--max-frac F] [--tolerance N]

The verdict passes when every threshold set with ``--max-mae``/``--max-frac``
is met; when neither is set it passes only when no pixel differs from the
reference by more than ``--tolerance``.

Exit status: 0 when the comparison passes, 1 when it fails, 2 usage or
read error.
"""

from __future__ import annotations

import sys

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.fidelity_arguments import parse_crop, max_mae, max_frac, tolerance
    from tools.containment import require_within_repo
    from tools.diagnostics import report_error
    from tools.fidelity_metrics import (
        FidelityError,
        compare,
        crop,
    )
    from tools.png import PngError, read_png
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/fidelity.py
    from argument_parsing import EscapingArgumentParser
    from fidelity_arguments import parse_crop, max_mae, max_frac, tolerance
    from containment import require_within_repo
    from diagnostics import report_error
    from fidelity_metrics import FidelityError, compare, crop
    from png import PngError, read_png
    from repo_root import ROOT
    from terminal import escape_controls


def _read_source(path: str, crop_rect: tuple[int, int, int, int] | None):
    """Read *path*, decoding only the scanlines *crop_rect* needs when given.

    ``crop`` slices the decoded pixel rows afterwards, so rows below the crop's
    bottom edge would be decoded and thrown away. Passing ``max_rows`` lets the
    PNG decoder skip their predictor work while still inflating and validating
    the whole stream, which saves seconds on a large Paeth-filtered reference.
    The bound shortens the returned height, so a rectangle that overflows the
    image sideways is re-read whole; ``crop`` then reports it against the real
    width and height as before. A rectangle that overflows vertically is
    already read whole because the decoder clamps the bound to the height.
    The alpha plane is decoded too, so a transparent candidate cannot compare
    equal to an opaque reference.

    A repository path that resolves outside the repository (a checked-in
    symlink) is refused before it is read: the report's worst-delta values and
    the pass/fail status would otherwise let a private image be probed against
    a known candidate.
    """
    require_within_repo(path, ROOT)
    if crop_rect is None:
        return read_png(path, alpha=True)
    x, y, width, height = crop_rect
    image = read_png(path, max_rows=y + height, alpha=True)
    if x + width > image.width:
        # The crop is rejected either way; re-read unbounded only so its
        # diagnostic names the file's real height rather than the bound's.
        return read_png(path, alpha=True)
    return image


def main(argv: list[str] | None = None) -> int:
    """Run the comparison CLI; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/check_references.py``,
    ``None`` reads ``sys.argv``.
    """
    parser = EscapingArgumentParser(
        prog="fidelity",
        description="Measure a rendered PNG surface against a reference PNG.",
        epilog=(
            "exit status: 0 when the comparison passes, 1 when it fails, "
            "2 usage or read error; passes when every --max-mae/--max-frac "
            "threshold set is met, and otherwise when no pixel differs "
            "beyond --tolerance"
        ),
    )
    parser.add_argument("candidate", help="rendered surface image (PNG)")
    parser.add_argument("reference", help="reference image (PNG)")
    parser.add_argument(
        "--candidate-crop",
        type=parse_crop,
        metavar="X,Y,W,H",
        help="crop the candidate to this region before comparing",
    )
    parser.add_argument(
        "--crop",
        type=parse_crop,
        metavar="X,Y,W,H",
        help="crop the reference to this region before comparing",
    )
    parser.add_argument(
        "--tolerance",
        type=tolerance,
        default=0,
        help="per-channel delta (0-255) at or below which a pixel is not 'differing'",
    )
    parser.add_argument(
        "--max-mae",
        type=max_mae,
        default=None,
        help=(
            "fail when mean absolute error exceeds this (0-255); when set, "
            "replaces the default no-differing-pixel gate"
        ),
    )
    parser.add_argument(
        "--max-frac",
        type=max_frac,
        default=None,
        help=(
            "fail when the differing-pixel fraction exceeds this (0-1); when "
            "set, replaces the default no-differing-pixel gate"
        ),
    )
    args = parser.parse_args(argv)

    try:
        candidate = _read_source(args.candidate, args.candidate_crop)
        reference = _read_source(args.reference, args.crop)
        if args.candidate_crop is not None:
            candidate = crop(candidate, *args.candidate_crop)
        if args.crop is not None:
            reference = crop(reference, *args.crop)
        metrics = compare(candidate, reference, tolerance=args.tolerance)
    except (PngError, FidelityError, ValueError) as exc:
        return report_error("fidelity", str(exc))

    # Every threshold the caller set is a budget that must be met. With no
    # budget set the verdict falls back to the strictest one: no pixel
    # differing by more than --tolerance. --max-mae and --max-frac therefore
    # replace the default gate rather than silently defaulting to zero, which
    # would require byte-exactness no matter what --tolerance says.
    budgets = []
    if args.max_mae is not None:
        budgets.append(metrics.mae <= args.max_mae)
    if args.max_frac is not None:
        budgets.append(metrics.frac_differing <= args.max_frac)
    ok = all(budgets) if budgets else metrics.frac_differing <= 0.0
    print(
        f"candidate: {escape_controls(args.candidate)}  "
        f"{candidate.width}x{candidate.height}"
    )
    print(
        f"reference: {escape_controls(args.reference)}  "
        f"{reference.width}x{reference.height}"
    )
    if args.candidate_crop is not None:
        # The candidate line names the cropped size but not the rectangle it
        # came from, so a transcript could not be replayed without the
        # original --candidate-crop argument. Echo it; the fields are plain
        # ints from parse_crop, so no escaping is needed.
        x, y, width, height = args.candidate_crop
        print(f"candidate crop: {x},{y},{width},{height}")
    if args.crop is not None:
        # The reference line names the cropped size but not the rectangle it
        # came from, so a transcript could not be replayed without the
        # original --crop argument. Echo it; the fields are plain ints from
        # parse_crop, so no escaping is needed.
        x, y, width, height = args.crop
        print(f"reference crop: {x},{y},{width},{height}")
    print(f"pixels compared: {metrics.pixels}")
    print(f"mean absolute error: {metrics.mae:.4f}")
    if metrics.mae_a is None:
        print(
            f"per-channel MAE (R, G, B): {metrics.mae_r:.4f} "
            f"{metrics.mae_g:.4f} {metrics.mae_b:.4f}"
        )
    else:
        print(
            f"per-channel MAE (R, G, B, A): {metrics.mae_r:.4f} "
            f"{metrics.mae_g:.4f} {metrics.mae_b:.4f} "
            f"{metrics.mae_a:.4f}"
        )
    print(f"RMSE: {metrics.rmse:.4f}")
    print(
        f"max channel delta: {metrics.max_delta} "
        f"at ({metrics.max_x}, {metrics.max_y})"
    )
    print(
        f"differing pixels: {metrics.differing} / {metrics.pixels} "
        f"({metrics.frac_differing:.6f})"
    )
    verdict = "PASS" if ok else "FAIL"
    mae_budget = "unset" if args.max_mae is None else f"{args.max_mae:.4f}"
    fraction_budget = "unset" if args.max_frac is None else f"{args.max_frac:.6f}"
    print(
        f"{verdict}: max-mae={mae_budget} max-frac={fraction_budget} "
        f"tolerance={args.tolerance}"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
