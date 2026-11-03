# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: filter short horizontal mismatch runs (planned 2026-11-02 by the plan role)

**Goal.** Isolate sustained horizontal border mismatches from short fragments in fidelity reports. Source and archive-heading searches found horizontal interval lists and longest-run summaries, but no minimum-length mismatch-list filter. This is independently mergeable from the waiting reference-sampler filter: it uses the fidelity CLI and tests.

**Approach and files.** Add optional `--min-difference-run-length N` to `tools/fidelity_cli_parser.py::build_parser`, importing the existing `tools/argument_parsing.py::positive_int` factory in both import modes and using an absent default. In `tools/fidelity.py::main`, retain the parser instance and reject explicit use without `--difference-runs` with `parser.error("--min-difference-run-length requires --difference-runs")` before `_read_source`. After computing `longest_run` from the complete horizontal list, filter `runs` by inclusive length before passing it to `report_data`. Keep segmentation, comparison metrics, thresholds, verdict, longest summaries and other diagnostics based on the full compared crops; do not change `difference_runs`, `select_longest_run`, or the report schema. Requested empty lists remain JSON `difference_runs: []` and text `difference runs: []`. Add `tests/test_fidelity_difference_runs_min_length.py` using `support.fidelity_cli_case.FidelityCliTestCase`, extend `tests/test_fidelity_cli_parser.py`, document the option beside `--difference-runs` in README.md, and amend its tooling guarantee in docs/invariants.md. These six files bound one run; filtering reduces output rather than scanning work. Vertical filtering is outside this entry.

**Acceptance criteria.** Literal text/JSON expectations cover offset nonsquare crops with intervals shorter than, equal to and longer than the cutoff, separated intervals, final-row flushing and adjacent row boundaries that must stay separate. Cutoff 1 matches omitted-option output; no mismatches and a cutoff exceeding crop width emit empty lists. Exercise strict tolerance boundaries, alpha-only differences, RGB beneath alpha zero and missing-alpha fallback. Combine the filter with both longest summaries and vertical intervals: even when the horizontal list is emptied, its longest summary remains non-null when mismatches exist. Compare metrics, bounds, remaining requested diagnostics and exit status against unfiltered output under both default failure and an accepting aggregate budget. Mock the image-based horizontal summary helper to prove list-plus-summary mode still reuses the complete collected list. Reject zero, negative, non-ASCII, fractional, malformed and missing values with status 2 and empty stdout; valid numeric use without `--difference-runs` must produce the dependency diagnostic before source reads. Check help, parser defaults and direct-script/package parity. Run `make check` after final edits.

## Done
