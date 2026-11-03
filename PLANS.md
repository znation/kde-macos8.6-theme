# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


### Reference-pixel sampler: exclude known background colors from histograms (planned 2026-11-02 by the plan role)

**Goal.** Inspect bevel and accent palettes without known background colors consuming the `--top-colors` slots. Existing minimum-count and fraction filters suppress rare colors, but cannot remove a named dominant background.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add repeatable `--exclude-color RRGGBB`, parsed by the existing `rgb_argument`, defaulting to `None`; `option_error` requires `--histogram` before image access. In `tools/sample_report_histogram.py::_histogram_result`, form a set of excluded RGB tuples and filter counted candidates by `color[:3]` before minimum-count/fraction predicates and top-N selection. With `--alpha`, exclude every opacity variant of the named RGB, including stored RGB under zero alpha; no tolerance or alpha selector is added. Preserve full-region counts, fraction denominator and original distinct RGB/RGBA total. Explicit exclusion always enables `total_colors` and `omitted_pixels`, even for an absent color; omitted pixels include exclusion and other filters without double counting. Extend both result assembly and `report_histogram`'s text-total condition. Spatial fields remain limited to emitted keys through `_histogram_spatial_fields`. Add `tests/test_sample_histogram_exclusions.py` using the CLI fixtures patterned on `TestSampleHistogramMinimumCount`, and document semantics in README.md and the sampler histogram section of `docs/invariants.md`. This is one selection feature; no theme artwork changes.

**Acceptance criteria.** Pin text/JSON output for an offset crop with a dominant excluded background, remaining count ties and `--top-colors`; prove exclusion precedes truncation. Cover repeated exclusions, duplicates, lowercase and optional `#`, absent colors, and exclusion of the entire palette (empty colors, full area omitted). Combine with minimum count/fraction, fractions and spatial fields, verifying retained values use full-region occurrences and denominator. RGBA fixtures distinguish original opacity-key totals while excluding every matching RGB variant; include opaque fallback and transparent stored RGB. Missing/malformed color arguments and use without histogram (ordinary, runs and find-color modes) exit 2 with empty stdout before header or image decoding reads. Verify omitted-option output retains existing fixtures, help/default parsing, and package/direct-script parity. Run `make check` after final edits.

