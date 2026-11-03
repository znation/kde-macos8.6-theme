# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Reference-pixel histogram: isolate spatial diagnostic collection (planned 2026-11-02 by the plan role)

**Goal and grounding.** Keep palette counting and output assembly readable as spatial diagnostics grow. `tools/sample_report_histogram.py::_histogram_result` currently owns optional bounds, first-position and centroid state as well as counting, ranking and color-record construction. Source and archive searches found the earlier result/printer split and individual diagnostic features, but no separate spatial collector. This maintenance task is independent of the queued centroid feature's CLI work.

**Approach and files.** Extract `_histogram_spatial_fields(args, image, colors)` in `tools/sample_report_histogram.py`, where `colors` is the selected ordered list of `(color_tuple, count)` pairs. Return a mapping from emitted color tuples to dictionaries containing requested `position`, `centroid` and `bounds` fields. Move the existing optional positioned traversal, alpha-key construction and coordinate bookkeeping into it; keep counting, selection, fractions, record assembly and printing in their current functions. With no spatial flags, return empty per-color dictionaries without traversing pixels. Merge the returned fields into each color record in the existing JSON field order (position, centroid, bounds). Use `getattr(args, "color_centroids", False)` as the current assembler does. No new option, class or dependency. Extend `tests/test_sample_histogram_result.py`; these two files bound the implementation. Read the sampler rows in `docs/invariants.md`; this extraction changes no documented guarantee.

**Acceptance criteria.** Add direct collector tests with explicit expected dictionaries for a nonzero-origin crop combining bounds, first positions and centroids, including disconnected occurrences, exact RGBA separation and top-color selection. Assert that returned keys are emitted colors, first positions use row-major order, and centroid divisors use full selected-color counts. Instrument `_positioned_region_pixels` to verify no traversal without spatial flags and one traversal with the three flags combined. Extend the existing combined CLI fixture to pin JSON field order and exact text suffix order with centroids enabled; compare package and direct-script results. Preserve existing RGB grouping, opaque alpha fallback, default output, namespace immutability and row-bounded decode tests. Run `make check` after final edits; keep the change within a few hundred lines including tests.

## Done
