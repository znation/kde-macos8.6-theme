# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler: cap histogram colors by region fraction (planned 2026-11-03 by the plan role)

**Refused 2026-11-03 by plan: This entry duplicates the implemented --max-color-fraction feature and would add redundant work without a behavior change.**

**Goal.** Isolate sparse detail colors with a crop-size-independent upper cutoff. The sampler supports minimum fraction and maximum absolute count, but source and archive searches found no maximum-fraction option. This is independent of the queued fidelity pagination plan.

**Approach and files.** Add optional `--max-color-fraction F`, default None, in `tools/sample_arguments.py::build_parser`, with its histogram dependency in `option_error` after the minimum-fraction check. In `tools/sample_validators.py`, add a maximum-fraction converter using `plain_number`, finite checking and inclusive 0–1 bounds, with diagnostics naming the new flag; preserve `color_fraction`'s existing contract. In `tools/sample_report_histogram.py::_histogram_result`, retain colors whose `count / (args.width * args.height) <= F`, intersecting with existing exclusions, count and minimum-fraction filters before top-color selection. Extend the filtered-summary conditions in `_histogram_result` and `report_histogram` so explicit use reports original distinct-color totals and omitted pixels even when nothing is removed. Contradictory fraction cutoffs yield a successful empty palette. Add `tests/test_sample_histogram_max_fraction.py` with `CliTestCase` fixtures and extend `tests/test_sample_option_validation.py::TestSampleOptionValidation`; document the option in README.md and its guarantee in docs/invariants.md. Keep this to these seven files and a few hundred changed lines; no decoding or histogram architecture changes.

**Acceptance criteria.** Given an offset eight-pixel crop with RGB counts 3, 2, 2 and 1, F=0.25 emits counts 2, 2 and 1 in descending count/ascending RGB order, reports `total_colors=4` and `omitted_pixels=3`, and retains fractions 0.25, 0.25 and 0.125. Adding top-colors 1 emits the earlier count-2 tuple and reports six omitted pixels. The same color proportions in a doubled-area crop select the same palette. F=0 emits an empty palette and eight omitted pixels; F=1 retains the full palette with explicit totals. Minimum fraction 0.25 plus maximum fraction 0.25 retains both count-2 colors; minimum 0.5 plus maximum 0.25 returns an empty palette. Cover intersections with named exclusions and both count limits, full-region fractions after filtering, and absolute positions/bounds/centroids for emitted colors. An RGBA fixture splits a shared RGB across alpha levels so maximum-fraction selection differs from ordinary merged RGB selection; include transparent stored RGB and opaque fallback. Text and JSON agree on retained colors and totals; omitted-option output keeps its existing schema, and direct-script/package invocations agree. Negative, over-one, nonfinite, whitespace-padded, underscore, non-ASCII, empty and missing values exit 2 with empty stdout before PNG reads; decimal and exponent notation within bounds succeed. Explicit use without histogram, including F=0 in pixel/run/search modes, exits 2 before reads and names the histogram requirement. Existing compatibility precedence stays intact, parser default is None, and help lists the option. Run `make check` after final edits.

## Done
