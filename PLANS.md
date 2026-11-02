# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel sampler: identify an actual pixel for each histogram color (planned 2026-11-02 by the plan role)

**Goal and grounding.** Give palette investigations a reproducible pixel anchor per emitted color. `tools/sample_report_histogram.py::report_histogram` reports counts and optional enclosing bounds; the bounds' top-left need not contain that color when occurrences are disconnected. Source and archive searches found no per-histogram-color first-occurrence report; the finished histogram-bounds plan covers enclosing rectangles. This plan is independent of the queued fidelity input extraction.

**Approach and files.** Add boolean `--color-positions` to `tools/sample_arguments.py::build_parser`, with `option_error` rejecting it without `--histogram` before image reads. In `tools/sample_report_histogram.py::report_histogram`, retain the existing count/order/top-color selection, then optionally record the first row-major occurrence within the requested region for each emitted color. Use absolute image coordinates; add `position: {"x": X, "y": Y}` to each JSON color and append `  position=X,Y` after existing text fields. RGB mode groups opacity variants; `--alpha` uses exact RGBA keys, preserves RGB beneath transparency and uses opaque fallback 255. Reuse `_positioned_region_pixels` and `_region_alpha`; when combined with `--color-bounds`, collect positions in the same additional traversal. Keep state bounded by emitted colors, with no coordinate lists or additional PNG reads. Add `tests/test_sample_histogram_positions.py` using `support.cli_fixtures.CliTestCase` and `support.png_fixtures`; document the flag in README.md and a dated tooling guarantee in `docs/invariants.md`. These five files bound this single opt-in feature; no dependency or theme-art changes.

**Acceptance criteria.** Fixtures pin exact text and JSON positions for a single pixel, a uniform region, and disconnected occurrences whose bounds corner does not contain the color. A crop with nonzero x/y origins excludes earlier outside occurrences and reports absolute coordinates. Cover row-major selection, count ties, `--top-colors 1` and a limit above the distinct count, plus combined bounds/fractions output without changing counts or ordering. Cover RGB grouping across alpha variants, RGBA separation at alpha 0/128/255, transparent RGB preservation and opaque fallback. Misuse with ordinary sampling, runs and find-color exits 2 with empty stdout before header or decoder reads. Spies prove positions alone and positions plus bounds each use one additional positioned traversal and one bounded PNG decode; omitting both flags skips that traversal and keeps existing output. Direct-script and package JSON invocations agree and help lists the flag. Run `make check` after final edits.

## Done
