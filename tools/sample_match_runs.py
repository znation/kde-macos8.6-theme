"""Accumulate horizontal and vertical color-search match intervals."""

from __future__ import annotations


class _MatchRuns:
    def __init__(self, x: int, y: int, width: int, height: int,
                 horizontal: bool, vertical: bool) -> None:
        self.x, self.y = x, y
        self.right, self.bottom = x + width, y + height
        self.horizontal, self.vertical = horizontal, vertical
        self.runs = []
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
                self.runs.append({"x": self.run_start, "y": self.run_y,
                                  "length": x - self.run_start})
                self.run_start = self.run_y = None

    def _end_row(self) -> None:
        self.runs.append({"x": self.run_start, "y": self.run_y,
                          "length": self.right - self.run_start})
        self.run_start = self.run_y = None

    def _end_column(self, x: int, y: int) -> None:
        start = self.column_starts.pop(x)
        self.column_runs.append({"x": x, "y": start, "length": y - start})

    def finish(self) -> tuple[list[dict], list[dict]]:
        if self.horizontal and self.run_start is not None:
            self._end_row()
        if self.vertical:
            self.column_runs.extend(
                {"x": x, "y": start, "length": self.bottom - start}
                for x, start in self.column_starts.items()
            )
            self.column_runs.sort(key=lambda run: (run["x"], run["y"]))
        return self.runs, self.column_runs
