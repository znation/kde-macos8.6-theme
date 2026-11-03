# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler: page through ranked histogram colors (planned 2026-11-03 by the plan role)

**Goal.** Inspect later palette entries without printing the complete histogram. Source/option searches and related finished histogram-limit plans show leading-color limits and filtering, but no histogram offset.

**Approach and files.** Add optional `--color-offset K` (default None) in `tools/sample_arguments.py::build_parser`; `option_error` requires `--top-colors` for explicit use, including zero, after the existing top-colors mode check. Add `color_offset` in `tools/sample_validators.py`, following `match_pixel_offset` with flag-specific diagnostics: nonnegative ASCII decimal integer via `plain_number`. In `tools/sample_report_histogram.py::_histogram_result`, apply existing color filters first, select the first K+N ranked eligible colors with `nsmallest`, then emit entries K through K+N-1, where N is top-colors. Clamp the selection size to the original distinct-color count before selection so a huge valid offset cannot cause allocation proportional to its numeric value. Ranking remains descending count then ascending RGB/RGBA tuple. Existing totals count original distinct colors and region area minus emitted counts, including skipped colors; fractions keep the full region denominator and spatial fields describe emitted colors. Explicit use adds top-level JSON `color_offset` and a `color offset: K` text line immediately before the color records in `report_histogram`. Omitted use preserves the output schema. Add `tests/test_sample_histogram_offset.py` using `CliTestCase`, extend `tests/test_sample_option_validation.py::TestSampleOptionValidation`, and document the option and selection-storage bound in README.md and the histogram row of docs/invariants.md. These seven files form one run; no decoder change or dependency.

**Acceptance criteria.** An offset crop of eight pixels has colors A=(0,0,0), B=(0,1,0), C=(1,0,0), D=(2,0,0) with counts 3,2,2,1. K=1,N=2 emits B,C in that order, `total_colors=4`, `omitted_pixels=4`, and fractions 0.25 each. K=3,N=2 emits D and omits seven pixels; K=4 or a much larger valid K emits no colors and omits eight. Filtering out A before K=1,N=1 emits C and omits six pixels. Successive pages reproduce the eligible ranked palette without repetition; explicit zero matches the ordinary leading page apart from offset metadata. Text and JSON agree, direct-script and package entry points agree, and omission retains existing output fixtures. Cover count/fraction filters, exclusions, empty eligible palettes, RGB/RGBA grouping with opacity ties, stored RGB under zero alpha, opaque fallback, and absolute bounds/positions/centroids of emitted colors. Negative, fractional, exponent, whitespace-padded, underscore, non-ASCII, empty and missing offsets fail with status 2 and empty stdout before PNG reads, including integer conversion-limit failures without traceback. Offset without top-colors fails before reads in histogram, ordinary, runs and search modes, and explicit zero is validated too; existing diagnostic precedence stays intact. Parser default is None and help lists the option. Run `make check` after final edits.

## Done

### Reference-pixel sampler: cap histogram colors by region fraction (planned 2026-11-03 by the plan role)

Superseded by the implemented `--max-color-fraction` option, recorded in PLANS-DONE.md as “Reference-pixel sampler: suppress dominant colors by region fraction.”
