"""Accumulate horizontal and vertical color-search match intervals."""

from __future__ import annotations


class _RunPage:
    """Count every closed run and retain the requested page of eligible ones.

    ``add`` counts the closed run; a run whose length is inside the
    eligibility bounds takes the next eligible index, and only runs from the
    requested page (index >= ``run_offset``, at most ``run_limit``) are
    kept. ``collect=False`` stops retention while still counting eligible
    runs, so ``omitted_runs`` stays computed against the eligible total.

    Two call sites apply these identical rules: ``_MatchRuns._close_run``'s
    horizontal page and ``_ColumnRuns._close``'s column-major page. The
    callers expose the page's counts as properties and alias the retained
    list as ``runs``, keeping the attributes their consumers read unchanged.
    """

    def __init__(self, *, min_run_length: int | None = None,
                 max_run_length: int | None = None,
                 run_offset: int = 0, run_limit: int | None = None,
                 collect: bool = True) -> None:
        self.min_run_length = min_run_length
        self.max_run_length = max_run_length
        self.run_offset = run_offset
        self.run_limit = run_limit
        self.collect = collect
        self.eligible_run_count = 0
        self.run_count = 0
        self.retained: list[dict] = []

    def _eligible(self, length: int) -> bool:
        return ((self.min_run_length is None or length >= self.min_run_length) and
                (self.max_run_length is None or length <= self.max_run_length))

    def add(self, run: dict) -> None:
        """Count the closed *run* and retain it when it is on the page."""
        self.run_count += 1
        if not self._eligible(run["length"]):
            return
        index = self.eligible_run_count
        self.eligible_run_count += 1
        if self.collect and index >= self.run_offset and (
                self.run_limit is None or len(self.retained) < self.run_limit):
            self.retained.append(run)


class _MatchRuns:
    def __init__(self, x: int, y: int, width: int, height: int,
                 *, horizontal: bool, vertical: bool, summarize: bool = False,
                 collect_runs: bool = True, summarize_columns: bool = False,
                 collect_column_runs: bool = True, min_run_length: int | None = None,
                 max_run_length: int | None = None, run_limit: int | None = None,
                 run_offset: int = 0) -> None:
        self.x, self.y = x, y
        self.right, self.bottom = x + width, y + height
        self.horizontal, self.vertical = horizontal, vertical
        self.summarize = summarize
        self.summarize_columns = summarize_columns
        self.collect_column_runs = collect_column_runs
        self.runs_page = _RunPage(min_run_length=min_run_length,
                                  max_run_length=max_run_length,
                                  run_offset=run_offset, run_limit=run_limit,
                                  collect=collect_runs)
        # The page owns the counts and the retained runs; aliases keep the
        # attributes read by sample_report_search and the storage tests.
        self.runs = self.runs_page.retained
        self.run_start = self.run_y = None
        self.longest_run = None
        self.longest_column_run = None
        self.column_runs = []
        self.column_run_count = 0
        self.column_starts = {}

    @property
    def run_count(self) -> int:
        return self.runs_page.run_count

    @property
    def eligible_run_count(self) -> int:
        return self.runs_page.eligible_run_count

    def observe(self, x: int, y: int, matches: bool) -> None:
        if self.horizontal and self.run_start is not None and y != self.run_y:
            self._end_row()
        if self.vertical:
            if matches:
                self.column_starts.setdefault(x, y)
            elif x in self.column_starts:
                self._end_column(x, y)
        if self.horizontal:
            if matches and self.run_start is None:
                self.run_start, self.run_y = x, y
            elif not matches and self.run_start is not None:
                self._close_run(x - self.run_start)
                self.run_start = self.run_y = None

    def _end_row(self) -> None:
        self._close_run(self.right - self.run_start)

    def _close_run(self, length: int) -> None:
        run = {"x": self.run_start, "y": self.run_y, "length": length}
        if not self.summarize or self.longest_run is None or length > self.longest_run["length"]:
            if self.summarize:
                self.longest_run = run
        self.runs_page.add(run)
        self.run_start = self.run_y = None

    def _end_column(self, x: int, y: int) -> None:
        start = self.column_starts.pop(x)
        run = {"x": x, "y": start, "length": y - start}
        self._record_column_run(run)

    def _record_column_run(self, run: dict) -> None:
        self.column_run_count += 1
        best = self.longest_column_run
        if self.summarize_columns and (best is None or
                (-run["length"], run["x"], run["y"]) <
                (-best["length"], best["x"], best["y"])):
            self.longest_column_run = run
        if self.collect_column_runs:
            self.column_runs.append(run)

    def finish(self) -> tuple[list[dict], list[dict]]:
        if self.horizontal and self.run_start is not None:
            self._end_row()
        if self.vertical:
            for x, start in self.column_starts.items():
                self._record_column_run(
                    {"x": x, "y": start, "length": self.bottom - start})
            self.column_runs.sort(key=lambda run: (run["x"], run["y"]))
        return self.runs, self.column_runs


class _ColumnRuns:
    """Collect vertical match intervals for a capped column-run page over a
    column-major scan: the active interval closes at every column boundary
    and the bottom edge, and counting, eligibility and the retained page are
    the shared `_RunPage` rules."""

    def __init__(self, x: int, y: int, width: int, height: int, *,
                 min_run_length: int | None = None,
                 max_run_length: int | None = None,
                 run_limit: int | None = None, run_offset: int = 0) -> None:
        self.x, self.y = x, y
        self.bottom = y + height
        self.runs_page = _RunPage(min_run_length=min_run_length,
                                  max_run_length=max_run_length,
                                  run_offset=run_offset, run_limit=run_limit)
        self.runs = self.runs_page.retained
        self.start_x = self.start_y = None

    @property
    def run_count(self) -> int:
        return self.runs_page.run_count

    @property
    def eligible_run_count(self) -> int:
        return self.runs_page.eligible_run_count

    def observe(self, x: int, y: int, matches: bool) -> None:
        if self.start_x is not None and x != self.start_x:
            self._close(self.bottom - self.start_y)
        if matches and self.start_x is None:
            self.start_x, self.start_y = x, y
        elif not matches and self.start_x is not None:
            self._close(y - self.start_y)

    def _close(self, length: int) -> None:
        self.runs_page.add(
            {"x": self.start_x, "y": self.start_y, "length": length})
        self.start_x = self.start_y = None

    def finish(self) -> list[dict]:
        if self.start_x is not None:
            self._close(self.bottom - self.start_y)
        return self.runs
