# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel sampler: report matching-color region fraction (planned 2026-11-02 by the plan role)

**Goal and grounding.** Compare a selected color's coverage across differently sized reference regions, including tolerance-grouped or alpha-filtered matches. `tools/sample_reports.py::report` already counts these matches but emits count and bounds without a fraction. Searches of sampler code, tests and backlog found no `--match-fraction`; the finished histogram-fractions plan covers exact histogram colors, not the find-color predicate. This is independent of the waiting fidelity-column plan.

**Approach and files.** Add boolean `--match-fraction` to `tools/sample_arguments.py::build_parser`. In `tools/sample.py::main`, reject it without `--find-color` before image reads, following the existing match-option validation. In the find-color branch of `tools/sample_reports.py::report`, derive `count / (args.width * args.height)` from the existing completed scan; add numeric `fraction` inside JSON `match` and a text `fraction: VALUE` line immediately after `count`, using ordinary Python float formatting. Omit both without the flag. The denominator is the full requested region, including nonmatching pixels; `--match-pixels` truncation never changes it. Reuse the existing RGB-tolerance and exact-alpha predicate without another traversal or additional decoding. Add `tests/test_sample_match_fraction.py` using `support.cli_fixtures.CliTestCase`, document the option in README.md, and add a dated sampler tooling invariant in docs/invariants.md. These six files bound one implementation run; no new dependency or theme value is involved.

**Acceptance criteria.** Pin text and JSON fractions for an offset multi-row region with known matches inside and outside it, including a nonterminating fraction, no matches (0.0), and complete coverage (1.0). Confirm RGB tolerance includes its boundary, exact-alpha filtering preserves stored transparent RGB, and an opaque image supplies alpha 255. Combine with `--match-pixels 1` to prove the fraction uses the complete match count. Assert default field/line omission, identical existing counts/bounds with and without the flag, misuse rejection before `read_png_size` with empty stdout, bounded `max_rows` decoding, and direct-script invocation. Run `make check` after the final implementation and documentation edits.

### Split reference sampler report handlers by mode (planned 2026-11-02 by the organize role)

**Goal and grounding.** Reduce the concentration of unrelated behavior in `tools/sample_reports.py::report`. The 209-line module's single dispatcher implements four distinct modes—scanline runs, color histogram, color search, and individual pixel listing—and mixes pixel traversal, aggregation, result assembly, and text/JSON output. Its shape, rather than module length alone, is the reason to split it; the current implementation is too concentrated to refactor safely as this run's direct edit.

**Approach and files.** Keep `tools/sample_reports.py` as the small public dispatcher and move each mode's handler and mode-specific output assembly into `tools/sample_report_runs.py`, `tools/sample_report_histogram.py`, `tools/sample_report_search.py`, and `tools/sample_report_pixels.py`, respectively. Move shared pixel traversal and RGB formatting helpers (`_region_pixels`, `_positioned_region_pixels`, `_region_alpha`, `_hex`) into `tools/sample_report_pixels.py` as shared primitives, with the pixel-list handler named distinctly there. The dispatcher selects the existing mode precedence and passes the same arguments, image, dimensions, and header through. Update imports and references in source, tests, and markdown documentation; touch `tools/sample_reports.py`, the four new modules, tests that import internal helpers, README.md only if references require it, and `docs/invariants.md` if the tested guarantee's ownership changes. No CLI behavior or output changes.

**Acceptance criteria.** Preserve the current precedence (runs, histogram, find-color, JSON pixel listing, single pixel, region listing), text and JSON fields/order, alpha behavior, deterministic histogram sorting and bounds, and the current bounded coordinate behavior for color search. Add or adapt focused tests to exercise each handler through the CLI and pin its existing output; keep tests passing without introducing dependencies. Search source, tests, and markdown for moved names and old module references, then run `make check` after the final edits.

## Done
