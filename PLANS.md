# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler: list bounded matching-color coordinates (planned 2026-11-02 by the plan role)

**Goal and grounding.** Locate actual pixels within disconnected color matches rather than treating their enclosing bounds as a solid patch. `tools/sample_reports.py::report` currently computes `--find-color` counts and bounds in its `_positioned_region_pixels` traversal but emits no matching-coordinate list. Searches of sampler code/tests and related planned and archived headings found no bounded match-coordinate feature; the completed color-location plans cover bounds, tolerance and alpha filtering.

**Approach and files.** Add optional `--match-pixels N` in `tools/sample_arguments.py::build_parser`, using an ASCII integer validator with range 1–1000. In `tools/sample.py::main`, reject use without `--find-color` before either image read. In the existing matching branch of `tools/sample_reports.py::report`, retain the first N accepted positions in row-major order while continuing the same traversal to compute full count and bounds. Reuse the existing RGB-tolerance and exact-alpha predicate; store at most N coordinate records, without another image read or traversal. With the option, JSON's `match` gains `pixels: [{"x": X, "y": Y}, ...]` and `omitted_pixels: count - len(pixels)`; coordinates are absolute. Text appends `matching pixels: K`, one `pixel (X, Y)` line per retained position, then `omitted pixels: M` after the existing match fields. Emit empty pixels and zero omitted when absent; omit the new fields/lines when the option is absent. Add `tests/test_sample_match_pixels.py` using `support.cli_fixtures.CliTestCase` and the existing PNG fixture helpers, document the limit and full-region counting in README.md, and extend the sampler invariant in docs/invariants.md. These six files bound one implementation run; no theme assets or dependencies change.

**Acceptance criteria.** An offset multi-row fixture with disconnected matches pins exact text/JSON ordering and coordinates, excluding matching pixels outside the region. Cover N=1, N below/equal/above match count, and no matches; full count and enclosing bounds must include matches beyond the retained prefix. Test tolerance-boundary inclusion and exact-alpha exclusion, including opaque fallback and transparent RGB. Invalid N (zero, negative, over 1000, fractional, non-ASCII digits, empty or missing) and use without `--find-color` return 2 with empty stdout before header or row reads. Verify omitted-option output retains its existing schema, one direct-script invocation succeeds, and decoding still uses the requested bottom-row bound. Run `make check` after implementation and documentation edits.

## Done
