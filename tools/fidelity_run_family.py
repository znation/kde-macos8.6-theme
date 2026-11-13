"""Difference-run family assembly for the fidelity comparison CLI.

One family is one axis of differing runs: horizontal (``--difference-runs``)
or vertical (``--difference-column-runs``). Both families share one report
shape — the run list, the eligible count omitted by its page, the run count
and the longest run — and one assembly recipe:

* when a count cap is given, page the lazy scan through
  ``tools/fidelity_run_page.py::collect_run_page``;
* otherwise scan once for the full run list;
* derive the run count and longest pick from the page or the list when they
  exist, else pay for a full scan of their own;
* apply the min/max/limit filter to an uncapped full list.

The two families differ only in their option values, which the caller reads
from the parsed arguments, and in the four scan callables they use, which
:class:`RunFamilyCalls` bundles. ``main`` in ``tools/fidelity.py`` calls
:func:`collect_run_family` once per family and passes the resulting
:class:`RunFamilyReport` fields into ``tools/fidelity_reports.py``.
"""

from __future__ import annotations

from typing import Callable, NamedTuple

if __package__:
    from tools.fidelity_run_page import collect_run_page
    from tools.fidelity_spatial import (
        difference_column_run_count,
        difference_column_runs,
        difference_run_count,
        difference_runs,
        iter_difference_column_runs,
        iter_difference_runs,
        longest_difference_column_run,
        longest_difference_run,
        select_longest_run,
    )
else:  # run directly: python3 tools/fidelity.py
    from fidelity_run_page import collect_run_page
    from fidelity_spatial import (
        difference_column_run_count,
        difference_column_runs,
        difference_run_count,
        difference_runs,
        iter_difference_column_runs,
        iter_difference_runs,
        longest_difference_column_run,
        longest_difference_run,
        select_longest_run,
    )


class RunFamilyCalls(NamedTuple):
    """The four scan callables one difference-run family scans with.

    Each takes ``(candidate, reference, tolerance, flags=flags)`` and scans
    one axis; ``iter_runs`` is the lazy variant the capped page consumes.
    """

    runs: Callable[..., list[dict[str, int]]]
    iter_runs: Callable[..., object]
    run_count: Callable[..., int]
    longest_run: Callable[..., dict[str, int] | None]


HORIZONTAL_RUN_CALLS = RunFamilyCalls(
    runs=difference_runs,
    iter_runs=iter_difference_runs,
    run_count=difference_run_count,
    longest_run=longest_difference_run,
)
"""The scan callables of the horizontal (``--difference-runs``) family."""

COLUMN_RUN_CALLS = RunFamilyCalls(
    runs=difference_column_runs,
    iter_runs=iter_difference_column_runs,
    run_count=difference_column_run_count,
    longest_run=longest_difference_column_run,
)
"""The scan callables of the vertical (``--difference-column-runs``) family."""


class RunFamilyReport(NamedTuple):
    """One family's assembled report values.

    ``runs`` is ``None`` when the family's mode flag was not given and its
    page or scan did not run; ``omitted`` counts eligible runs the capped
    page or limit window left out; ``count`` and ``longest`` are ``None``
    unless the corresponding option was given.
    """

    runs: list[dict[str, int]] | None
    omitted: int | None
    count: int | None
    longest: dict[str, int] | None


def _filter_run_report(runs, minimum, maximum, limit, offset=0):
    """Filter a run report, then page through its eligible records."""
    if minimum is not None:
        runs = [run for run in runs if run["length"] >= minimum]
    if maximum is not None:
        runs = [run for run in runs if run["length"] <= maximum]
    omitted = None
    if limit is not None:
        eligible_count = len(runs)
        runs = runs[offset:offset + limit]
        omitted = eligible_count - len(runs)
    return runs, omitted


def collect_run_family(candidate, reference, tolerance, flags, calls, *,
                       enabled, minimum, maximum, cap,
                       offset: int | None, wants_count,
                       wants_longest) -> RunFamilyReport:
    """Assemble one family's run report from its shared or full scans.

    *candidate*, *reference*, *tolerance* and *flags* go to every scan
    unchanged; *flags* may be ``None`` when no spatial report asked for the
    shared scan. *minimum*/*maximum* are the paired length filters, *cap*
    the count cap whose presence turns capped paging on, *offset* the
    resolved page offset -- ``None`` (the offset option was not given) acts
    as 0. The count is derived before the filter, so it stays a full-scan
    value even when the list is filtered afterwards.
    """
    offset = 0 if offset is None else offset
    capped = enabled and cap is not None
    omitted = None
    if capped:
        runs, omitted, total, capped_longest = collect_run_page(
            calls.iter_runs(candidate, reference, tolerance, flags=flags),
            minimum, maximum, offset, cap)
    else:
        runs = (calls.runs(candidate, reference, tolerance, flags=flags)
                if enabled else None)
        total = capped_longest = None

    # Every report value below reads the capped run page's precomputed
    # total or longest pick when paging is active, else the page it
    # already holds, else a full scan it pays for only when no page ran.
    if wants_count:
        if capped:
            count = total
        elif runs is not None:
            count = len(runs)
        else:
            count = calls.run_count(candidate, reference, tolerance,
                                    flags=flags)
    else:
        count = None

    if wants_longest:
        if capped:
            longest = capped_longest
        elif runs is not None:
            longest = select_longest_run(runs)
        else:
            longest = calls.longest_run(candidate, reference, tolerance,
                                        flags=flags)
    else:
        longest = None

    if runs is not None and not capped:
        runs, omitted = _filter_run_report(
            runs, minimum, maximum, cap, offset)
    return RunFamilyReport(runs=runs, omitted=omitted, count=count,
                           longest=longest)
