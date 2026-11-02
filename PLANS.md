# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel sampler: measure contiguous matching-color segments (planned 2026-11-02 by the plan role)

**Goal and grounding.** Measure separated border segments and gaps for a chosen reference color, including tolerance-grouped matches. `tools/sample_report_search.py::report_search` reports enclosing bounds and a bounded coordinate prefix; `tools/sample_report_runs.py::_color_runs` groups equal colors rather than the search predicate. Searches of sampler source/tests and related finished sampler plans found no match-run report. This is independent of the queued fidelity vertical-run diagnostic.

**Approach and files.** Add boolean `--match-runs` in `tools/sample_arguments.py::build_parser`; require `--find-color` before image reads in `tools/sample.py::main`. In `tools/sample_report_search.py::report_search`, accumulate maximal contiguous horizontal matching intervals during the existing row-major scan, using its RGB-tolerance and exact-alpha predicate. Flush on a nonmatch, row boundary and end of scan; adjacent matches merge even when their actual RGB values differ. Emit absolute-image-coordinate records `{ "x": start, "y": row, "length": length }` in row-major order as `match.runs` in JSON and a JSON-formatted `matching runs: ...` text line after existing search details. Omit the field/line and run accumulation without the flag. Empty matches produce `[]`; `--match-pixels` limits only the coordinate list, never these runs. Keep `--run-axis` exclusive to the existing `--runs` mode: this option always scans horizontally. Add `tests/test_sample_match_runs.py` using `support.cli_fixtures.CliTestCase`, document absolute coordinates, horizontal ordering and potentially large output in README.md, and append a dated tooling invariant to docs/invariants.md. These six files bound one implementation run; no theme changes or new dependencies.

**Acceptance criteria.** Offset nonsquare synthetic regions pin exact text/JSON runs for separated intervals, adjacent tolerance-matching but unequal colors, empty rows, first/last pixels, final-row flushing and matches at opposite row boundaries that must remain separate. Assert sum of lengths equals the full match count, with no outside-region matches included. Cover no matches, complete coverage, single-pixel, single-row and single-column regions; include tolerance boundary inclusion, exact-alpha rejection, stored RGB under alpha zero and opaque alpha fallback. Combine `--match-pixels 1` and `--match-fraction` to prove runs retain full-region coverage. Assert default field/line omission, missing `--find-color` rejection before header/decode reads with status 2 and empty stdout, and direct-script imports. Verify decoding remains once with `max_rows=y+height`. Existing search and ordinary color-run tests remain green. Run `make check` after final edits.

## Done
