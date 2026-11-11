"""Histogram reports for the reference pixel sampler."""

from __future__ import annotations

import json
from collections import Counter
from heapq import nsmallest

if __package__:
    from tools.sample_report_common import (
        compact_json, hex, positioned_region_pixels, print_region_line,
        region_alpha, region_pixels, report_context,
    )
else:  # run directly: python3 tools/sample.py
    from sample_report_common import (
        compact_json, hex, positioned_region_pixels, print_region_line,
        region_alpha, region_pixels, report_context,
    )


def _palette_filters_requested(args) -> bool:
    """Return whether any optional palette filter limits the emitted colors.

    Three sites in this module share the predicate: the result assembler's
    eligibility branch, its totals fields and the printer's totals lines.
    Only ``top_colors`` is guaranteed present in every caller's namespace
    (the sample CLI's parser always defines it); tests drive the report with
    namespaces carrying just the attributes their report asked for, so every
    other attribute is read tolerantly with getattr.
    """
    return (args.top_colors is not None
            or getattr(args, "color_offset", None) is not None
            or getattr(args, "min_color_count", None) is not None
            or getattr(args, "max_color_count", None) is not None
            or getattr(args, "min_color_fraction", None) is not None
            or getattr(args, "max_color_fraction", None) is not None
            or getattr(args, "exclude_colors", None)
            or getattr(args, "include_colors", None))


def _histogram_spatial_fields(args, image, colors):
    """Collect requested absolute positions, centroids and bounds for emitted colors."""
    fields = {color: {} for color, _ in colors}
    color_centroids = getattr(args, "color_centroids", False)
    if not (args.color_bounds or args.color_positions or color_centroids):
        return fields
    positions = {color: None for color, _ in colors} if args.color_positions else None
    bounds = ({color: [args.x + args.width, args.y + args.height, -1, -1]
               for color, _ in colors} if args.color_bounds else None)
    sums = {color: [0, 0] for color, _ in colors} if color_centroids else None
    alphas = iter(region_alpha(image, args.x, args.y, args.width, args.height)) if args.alpha else None
    for x, y, rgb in positioned_region_pixels(image, args.x, args.y, args.width, args.height):
        color = (*rgb, next(alphas)) if alphas is not None else rgb
        if color not in fields:
            continue
        if positions is not None and positions[color] is None:
            positions[color] = {"x": x, "y": y}
        if sums is not None:
            sums[color][0] += x
            sums[color][1] += y
        if bounds is not None:
            box = bounds[color]
            box[0], box[1] = min(box[0], x), min(box[1], y)
            box[2], box[3] = max(box[2], x), max(box[3], y)
    for color, count in colors:
        if positions is not None:
            fields[color]["position"] = positions[color]
        if sums is not None:
            fields[color]["centroid"] = {"x": sums[color][0] / count, "y": sums[color][1] / count}
        if bounds is not None:
            box = bounds[color]
            fields[color]["bounds"] = {"x": box[0], "y": box[1],
                "width": box[2] - box[0] + 1, "height": box[3] - box[1] + 1}
    return fields


def _scanline_color_counts(args, image):
    """Collect per-row and per-column distinct regional colors over one traversal.

    Colors group exactly like the histogram's emitted colors: RGB alone, or
    RGBA tuples with ``--alpha`` including each transparent pixel's stored RGB.
    Counts cover the complete region and are unaffected by displayed-palette
    filters. Either scanline axis is None when it was not requested.
    """
    row_sets = [set() for _ in range(args.height)] if getattr(args, "row_color_counts", False) else None
    column_sets = [set() for _ in range(args.width)] if getattr(args, "column_color_counts", False) else None
    if row_sets is None and column_sets is None:
        return None, None
    alphas = iter(region_alpha(image, args.x, args.y, args.width, args.height)) if args.alpha else None
    for x, y, rgb in positioned_region_pixels(image, args.x, args.y, args.width, args.height):
        color = (*rgb, next(alphas)) if alphas is not None else rgb
        if row_sets is not None:
            row_sets[y - args.y].add(color)
        if column_sets is not None:
            column_sets[x - args.x].add(color)
    rows = [len(row_set) for row_set in row_sets] if row_sets is not None else None
    columns = [len(column_set) for column_set in column_sets] if column_sets is not None else None
    return rows, columns


def _histogram_result(args, image, width: int, height: int) -> dict:
    """Assemble the complete histogram report without printing or mutating args."""
    context = report_context(args, width, height)
    region = context["region"]
    if args.alpha:
        pixels = zip(region_pixels(image, args.x, args.y, args.width, args.height),
                     region_alpha(image, args.x, args.y, args.width, args.height))
        counts = Counter((*rgb, alpha) for rgb, alpha in pixels)
    else:
        counts = Counter(region_pixels(image, args.x, args.y, args.width, args.height))
    min_color_count = getattr(args, "min_color_count", None)
    max_color_count = getattr(args, "max_color_count", None)
    min_color_fraction = getattr(args, "min_color_fraction", None)
    max_color_fraction = getattr(args, "max_color_fraction", None)
    excluded = {tuple(color) for color in (getattr(args, "exclude_colors", None) or ())}
    included = {tuple(color) for color in (getattr(args, "include_colors", None) or ())}
    color_offset = getattr(args, "color_offset", None)
    if _palette_filters_requested(args):
        total_colors = len(counts)
        candidates = counts.items()
        if included:
            candidates = ((color, count) for color, count in candidates if color[:3] in included)
        if excluded:
            candidates = ((color, count) for color, count in candidates if color[:3] not in excluded)
        if min_color_count is not None:
            candidates = ((color, count) for color, count in candidates
                         if count >= min_color_count)
        if max_color_count is not None:
            candidates = ((color, count) for color, count in candidates
                         if count <= max_color_count)
        if min_color_fraction is not None:
            denominator = args.width * args.height
            candidates = ((color, count) for color, count in candidates
                          if count / denominator >= min_color_fraction)
        if max_color_fraction is not None:
            denominator = args.width * args.height
            candidates = ((color, count) for color, count in candidates
                          if count / denominator <= max_color_fraction)
        if args.top_colors is not None:
            limit = min(total_colors, (color_offset or 0) + args.top_colors)
            selected = nsmallest(limit, candidates, key=lambda item: (-item[1], item[0]))
            colors = selected[color_offset or 0:]
        else:
            colors = sorted(candidates, key=lambda item: (-item[1], item[0]))
        omitted_pixels = args.width * args.height - sum(count for _, count in colors)
    else:
        colors = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    row_counts, column_counts = None, None
    if getattr(args, "row_color_counts", False) or getattr(args, "column_color_counts", False):
        row_counts, column_counts = _scanline_color_counts(args, image)
    spatial = _histogram_spatial_fields(args, image, colors)
    denominator = args.width * args.height
    cumulative_fractions = {}
    if getattr(args, "color_cumulative_fractions", False):
        running = 0
        for color, count in colors:
            running += count
            cumulative_fractions[color] = running / denominator
    result = {**context, "colors": [
            {"rgb": list(color[:3]), "hex": hex(color[:3]), "count": count,
             **({"alpha": color[3]} if args.alpha else {}),
             **({"fraction": count / denominator} if args.color_fractions else {}),
             **({"cumulative_fraction": cumulative_fractions[color]}
                if cumulative_fractions else {}),
             **spatial[color]}
            for color, count in colors
        ]}
    if row_counts is not None:
        result["row_color_counts"] = row_counts
    if column_counts is not None:
        result["column_color_counts"] = column_counts
    if color_offset is not None:
        result["color_offset"] = color_offset
    if _palette_filters_requested(args):
        result["total_colors"] = total_colors
        result["omitted_pixels"] = omitted_pixels
    return result


def report_histogram(args, image, width: int, height: int, header: str) -> None:
    """Print the histogram report: the region's counted colors, as JSON or plain text."""
    result = _histogram_result(args, image, width, height)
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
        return
    print(header)
    print_region_line(args)
    if "color_offset" in result:
        print(f"color offset: {result['color_offset']}")
    for color in result["colors"]:
        rgb = color["rgb"]
        suffix = f"  alpha={color['alpha']}" if "alpha" in color else ""
        if "bounds" in color:
            bounds = color["bounds"]
            suffix += f"  bounds={bounds['x']},{bounds['y']},{bounds['width']},{bounds['height']}"
        if "fraction" in color:
            suffix += f"  fraction={color['fraction']}"
        if "cumulative_fraction" in color:
            suffix += f"  cumulative_fraction={color['cumulative_fraction']}"
        if "position" in color:
            position = color["position"]
            suffix += f"  position={position['x']},{position['y']}"
        if "centroid" in color:
            centroid = color["centroid"]
            suffix += f"  centroid={centroid['x']},{centroid['y']}"
        print(f"{rgb[0]},{rgb[1]},{rgb[2]}  {color['hex']}  count={color['count']}{suffix}")
    if "row_color_counts" in result:
        print(f"row color counts: {compact_json(result['row_color_counts'])}")
    if "column_color_counts" in result:
        print(f"column color counts: {compact_json(result['column_color_counts'])}")
    if _palette_filters_requested(args):
        print(f"total colors: {result['total_colors']}")
        print(f"omitted pixels: {result['omitted_pixels']}")
