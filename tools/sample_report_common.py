"""Shared image and region metadata for sampler reports."""

from __future__ import annotations


def region_from_args(args) -> dict:
    """Return the region the report's args define, as the {"x", "y", "width", "height"}
    dict every sample report result and JSON document carries. Four call sites: the pixels,
    runs, histogram and find-color-search report handlers."""
    return {"x": args.x, "y": args.y, "width": args.width, "height": args.height}


def report_context(args, width: int, height: int) -> dict:
    """Return the common image and requested-region fields used by reports."""
    return {
        "image": args.image,
        "image_width": width,
        "image_height": height,
        "region": region_from_args(args),
    }
