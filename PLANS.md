# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel sampler: measure parallel scanline runs in a rectangle (planned 2026-11-02 by the plan role)

**Goal and grounding.** Inspect a complete bevel's color bands in one invocation rather than sampling each row or column separately. `tools/sample.py::main` rejects two-dimensional `--runs` regions; `tools/sample_report_runs.py::_color_runs` handles one scanline. Source and archive searches found single-scanline RGB/RGBA reporting and its extraction, but no explicit rectangular run axis. This is independent of the waiting fidelity diagnostic.

**Approach and files.** Add `--run-axis {horizontal,vertical}` (default absent) in `tools/sample_arguments.py::build_parser`, requiring `--runs` before image reads in `tools/sample.py::main`. Keep the existing two-dimensional rejection when the option is absent. In `tools/sample_report_runs.py::report_runs`, use the explicit axis to enumerate independent scanlines: horizontal visits rows top-to-bottom, each left-to-right; vertical visits columns left-to-right, each top-to-bottom. Reuse `_color_runs` on one-row/one-column subregions and flatten their records into the existing `runs` array; never merge across scanline boundaries. Explicit vertical scans of height 1 must still report vertical axis, including a single pixel. Preserve the current text header, axis line and per-run format, absolute origins, RGB/RGBA equality and opaque alpha fallback. Decode once using the existing bottom-row bound; do not transpose or re-decode the image. Add `tests/test_sample_run_axis.py` using `support.cli_fixtures.CliTestCase`, document ordering and an example in README.md, and update the scanline guarantee in `docs/invariants.md` with the implementation date. These seven files bound one implementation run; no theme assets or decoder changes.

**Acceptance criteria.** Offset nonsquare fixtures pin exact JSON and text for both axes, repeated colors within a line, equal colors across adjacent line boundaries that must remain separate, and distinct final rows/columns. Run lengths cover the rectangle exactly and each run stays within its scanline. Cover explicit axes on one-row, one-column and single-pixel regions; RGBA alpha-only transitions, differing RGB beneath zero alpha and opaque RGB fallback. Existing invocations without the option retain their output and two-dimensional rejection. Invalid axis values and use without `--runs` (including histogram/search modes) return 2 with empty stdout before image reads. Mock decoding to assert one call bounded to `y + height`; exercise direct-script rectangular output, out-of-bounds regions and corrupt images. Run `make check` after final edits.

## Done
