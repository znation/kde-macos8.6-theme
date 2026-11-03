# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler: isolate scalar argument parsers (planned 2026-11-03 by the plan role)

**Goal.** Keep the sampler's growing CLI definition readable by separating scalar conversion from option construction and compatibility checks. `tools/sample_arguments.py` currently combines six scalar parsers with `build_parser`, `option_error` and `region_error`; the finished compatibility-validation plan moved checks out of image loading, rather than separating these responsibilities.

**Approach and files.** Move `rgb_argument`, `color_tolerance`, `match_alpha`, `match_pixels`, `match_pixel_offset` and `color_fraction` without semantic changes into new `tools/sample_argument_types.py`. Move their `argparse`, `math`, `re` and `plain_number` imports with them. Import the six names into `tools/sample_arguments.py` in its package and direct-script branches, retaining existing import access there; leave `positive_int`, parser construction and the two namespace validators in place. Add focused `tests/test_sample_argument_types.py` using unittest. No CLI option, report format or theme value changes are proposed. These three files bound the implementation; existing tooling guarantees in `docs/invariants.md` remain applicable.

**Acceptance criteria.** Direct scalar calls accept RGB `#aBcD09` as `(171, 205, 9)`, byte endpoints 0 and 255, match limits 1 and 1000, offset 0 and fraction endpoints 0 and 1. They reject malformed RGB, byte values -1/256, match limits 0/1001, negative offsets, fractions outside [0,1] and non-finite fractions with `ArgumentTypeError`; numeric parsers continue rejecting non-ASCII digits. Imports through `tools.sample_arguments` still expose the six parsers. Package and direct-script CLI invocations accept a valid search and histogram request on a tiny PNG with the same parsed JSON results, and reject invalid scalar inputs with status 2, empty stdout and the existing diagnostic content. Existing option-validation tests continue to show compatibility errors before image reads. `make check` passes.


## Done
