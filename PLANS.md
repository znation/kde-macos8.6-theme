# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Fidelity diagnostics: report the centroid of mismatching pixels (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal and grounding.** Locate the spatial centre of scattered rendering errors without treating their enclosing rectangle's midpoint as their centre. `tools/fidelity_spatial.py` reports row/column counts, bounds and runs; searches found no mismatch-centroid diagnostic.

**Implemented.** Added opt-in `--difference-centroid`, a constant-space row-major scan using the existing raw RGBA predicate, crop-relative mean coordinates, explicit JSON/text null for no mismatches, tests, and documentation. The test fixture covers unequal mismatch magnitudes, tolerance exclusion, hidden RGB and opaque-alpha fallback; CLI coverage checks cropped coordinates, both verdict outcomes, and default omission. (planned 2026-11-02 by the plan role; completed within this run.)
## Done
