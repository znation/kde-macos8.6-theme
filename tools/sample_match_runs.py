"""Accumulate horizontal and vertical color-search match intervals."""

from __future__ import annotations


class _MatchRuns:
    def __init__(self, x: int, y: int, width: int, height: int,
                 *, horizontal: bool, vertical: bool, summarize: bool = False,
                 collect_runs: bool = True, summarize_columns: bool = False,
                 collect_column_runs: bool = True) -> None:
        self.x, self.y = x, y
        self.right, self.bottom = x + width, y + height
        self.horizontal, self.vertical = horizontal, vertical
        self.summarize = summarize
        self.collect_runs = collect_runs
        self.summarize_columns = summarize_columns
        self.collect_column_runs = collect_column_runs
        self.runs = []
        self.run_count = 0
        self.longest_run = None
        self.longest_column_run = None
        self.column_runs = []
        self.run_start = self.run_y = None
        self.column_starts = {}

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
        self.run_count += 1
        run = {"x": self.run_start, "y": self.run_y, "length": length}
        if not self.summarize or self.longest_run is None or length > self.longest_run["length"]:
            if self.summarize:
                self.longest_run = run
        if self.collect_runs:
            self.runs.append(run)
        self.run_start = self.run_y = None

    def _end_column(self, x: int, y: int) -> None:
        start = self.column_starts.pop(x)
        run = {"x": x, "y": start, "length": y - start}
        self._record_column_run(run)

    def _record_column_run(self, run: dict) -> None:
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
