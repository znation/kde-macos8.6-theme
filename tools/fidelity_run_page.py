"""Bounded collection for paged horizontal fidelity interval reports."""

from __future__ import annotations

from collections.abc import Iterable


def collect_run_page(intervals: Iterable[dict[str, int]], minimum: int | None,
                     maximum: int | None, offset: int, limit: int):
    """Return page, omitted eligible count, total count and first longest run."""
    page = []
    total = eligible = 0
    longest = None
    for run in intervals:
        total += 1
        if longest is None or run["length"] > longest["length"]:
            longest = run
        length = run["length"]
        if minimum is not None and length < minimum:
            continue
        if maximum is not None and length > maximum:
            continue
        if offset <= eligible < offset + limit:
            page.append(run)
        eligible += 1
    return page, eligible - len(page), total, longest
