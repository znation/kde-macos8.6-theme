# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel sampler: measure vertical matching-color segments (planned 2026-11-02 by the plan role)

**Goal and grounding.** Measure disjoint vertical border segments for a chosen reference color, including tolerance-grouped matches. `tools/sample_report_search.py::report_search` currently accumulates horizontal `--match-runs` during its row-major search. The finished horizontal-match plan explicitly leaves that option horizontal; ordinary `--runs --run-axis vertical` groups equal colors rather than matches to a search predicate. Source, test and archive searches found no vertical color-search run report. This is independent of the queued fidelity budget.

**Approach and files.** Add boolean `--match-column-runs` in `tools/sample_arguments.py::build_parser`, requiring `--find-color` before image reads in `tools/sample.py::main`. In `tools/sample_report_search.py::report_search`, use the existing match predicate and row-major traversal, tracking an active starting y per region column only when requested. Close a column's interval on a nonmatch and flush remaining intervals at the region bottom. Emit absolute-coordinate `{x, y, length}` records sorted by x then y as `match.column_runs` in JSON and a JSON-formatted `matching column runs:` text line after the optional horizontal runs line. Empty matches emit `[]`; adjacent matching pixels merge even if their RGB values differ within tolerance. Both run flags may coexist; coordinate limits affect neither run report. Avoid another decode or region scan and omit tracking/output without the flag. Add `tests/test_sample_match_column_runs.py` using `support.cli_fixtures.CliTestCase`; document ordering, absolute coordinates and potentially large output in README.md, and append a dated tooling row in docs/invariants.md. These six files bound one implementation run.

**Acceptance criteria.** Offset nonsquare synthetic regions pin exact text/JSON intervals for separated vertical segments, unequal adjacent tolerance matches, empty columns, first/last rows, final flushing and adjacent columns that must remain separate. Assert column-major ordering and sum of lengths equal to the full match count. Cover absent matches, full coverage, single pixel, single row and single column; exact tolerance boundaries, alpha-filter rejection, stored RGB beneath zero alpha and opaque fallback. Combine both run flags, `--match-pixels 1` and `--match-fraction` to prove the existing horizontal records and row-major coordinate prefix retain their meanings while vertical runs cover the full region. Assert field/line omission by default, missing `--find-color` rejection before header/decode reads with status 2 and empty stdout, help and direct-script invocation. Verify decoding occurs once with `max_rows=y+height`. Run `make check` after final edits.

## Done
