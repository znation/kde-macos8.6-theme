# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: filter short vertical mismatch runs (planned 2026-11-02 by the plan role)

**Goal.** Isolate sustained side-border mismatches from short vertical fragments in fidelity reports. Source and related archive searches found vertical interval lists and longest summaries but no vertical minimum-length filter. This is independent of the waiting sampler plan and extends the finished horizontal fidelity filter.

**Approach and files.** Add optional `--min-difference-column-run-length N` using the existing `positive_int` factory and `None` default in `tools/fidelity_cli_parser.py::build_parser`. In `tools/fidelity.py::main`, require `--difference-column-runs` with `parser.error("--min-difference-column-run-length requires --difference-column-runs")` before `_read_source`. After computing `longest_column_run` from the complete column list, filter `column_runs` by inclusive length before `report_data`. Preserve segmentation, column-major order, full comparison metrics, thresholds, verdict and longest summaries; do not change `difference_column_runs`, `select_longest_run` or report schemas. Requested empty lists remain JSON `difference_column_runs: []` and text `difference column runs: []`. Add `tests/test_fidelity_column_runs_min_length.py` using `support.fidelity_cli_case.FidelityCliTestCase`, extend `tests/test_fidelity_cli_parser.py`, document the option beside `--difference-column-runs` in README.md and amend the vertical-list guarantee in docs/invariants.md. These six files bound one run; this filters output without optimizing scans.

**Acceptance criteria.** Literal text/JSON expectations cover offset nonsquare crops with intervals shorter than, equal to and longer than the cutoff, separated intervals, bottom-edge flushing and adjacent columns that remain separate. Cutoff 1 matches omitted-option output; identical images and a cutoff above crop height emit empty lists. Exercise strict tolerance boundaries, alpha-only differences, RGB beneath alpha zero and missing-alpha fallback. Combine with the horizontal list and its cutoff and both longest summaries; an emptied vertical list must retain its non-null longest summary when mismatches exist. Compare metrics, bounds, remaining requested diagnostics and exit status against unfiltered output under default failure and an accepting aggregate budget. Mock the image-based vertical summary helper to prove list-plus-summary mode reuses the complete collected list. Reject zero, negative, fractional, non-ASCII, malformed and missing values with status 2 and empty stdout; valid numeric use without the vertical-list flag must produce the dependency diagnostic before source reads. Check help, parser defaults and direct-script/package parity. Run `make check` after final edits.

## Done
