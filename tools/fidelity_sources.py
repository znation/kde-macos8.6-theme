"""Guarded PNG input loading for the fidelity comparison CLI."""

from __future__ import annotations

if __package__:
    from tools.containment import require_within_repo
    from tools.png import read_png
    from tools.repo_root import ROOT
else:  # imported by direct execution of tools/fidelity.py
    from containment import require_within_repo
    from png import read_png
    from repo_root import ROOT


def read_source(path: str, crop_rect: tuple[int, int, int, int] | None):
    """Read a PNG with alpha, bounding decoded rows when a crop allows it.

    Sideways overflow is retried without a row bound so the crop diagnostic
    retains the image's real dimensions. Vertical overflow is left bounded;
    the PNG decoder clamps the bound to the image height.
    """
    require_within_repo(path, ROOT)
    if crop_rect is None:
        return read_png(path, alpha=True)
    x, y, width, height = crop_rect
    image = read_png(path, max_rows=y + height, alpha=True)
    if x + width > image.width:
        return read_png(path, alpha=True)
    return image
