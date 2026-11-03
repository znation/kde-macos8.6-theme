# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler: isolate scalar argument parsers (planned 2026-11-03 by the plan role)

**Goal.** Keep the sampler's growing CLI definition readable by separating scalar conversion from option construction and compatibility checks. `tools/sample_arguments.py` currently combines six scalar parsers with `build_parser`, `option_error` and `region_error`; the finished compatibility-validation plan moved checks out of image loading, rather than separating these responsibilities.

**Approach and files.** Move `rgb_argument`, `color_tolerance`, `match_alpha`, `match_pixels`, `match_pixel_offset` and `color_fraction` without semantic changes into new `tools/sample_argument_types.py`. Move their `argparse`, `math`, `re` and `plain_number` imports with them. Import the six names into `tools/sample_arguments.py` in its package and direct-script branches, retaining existing import access there; leave `positive_int`, parser construction and the two namespace validators in place. Add focused `tests/test_sample_argument_types.py` using unittest. No CLI option, report format or theme value changes are proposed. These three files bound the implementation; existing tooling guarantees in `docs/invariants.md` remain applicable.

**Acceptance criteria.** Direct scalar calls accept RGB `#aBcD09` as `(171, 205, 9)`, byte endpoints 0 and 255, match limits 1 and 1000, offset 0 and fraction endpoints 0 and 1. They reject malformed RGB, byte values -1/256, match limits 0/1001, negative offsets, fractions outside [0,1] and non-finite fractions with `ArgumentTypeError`; numeric parsers continue rejecting non-ASCII digits. Imports through `tools.sample_arguments` still expose the six parsers. Package and direct-script CLI invocations accept a valid search and histogram request on a tiny PNG with the same parsed JSON results, and reject invalid scalar inputs with status 2, empty stdout and the existing diagnostic content. Existing option-validation tests continue to show compatibility errors before image reads. `make check` passes.

### Reference-pixel sampler: isolate scalar argument parsers (planned 2026-11-03 by the plan role)

**Goal.** Keep scalar syntax and range rules separate from sampler parser construction and option compatibility. `tools/sample_arguments.py` currently owns six scalar parsers alongside `build_parser`, `option_error` and `region_error`. Source and related archive searches found the earlier compatibility extraction, but no scalar-parser extraction.

**Approach and files.** Move `rgb_argument`, `color_tolerance`, `match_alpha`, `match_pixels`, `match_pixel_offset` and `color_fraction` verbatim into new `tools/sample_validators.py`, moving their `math`/`re` imports and retaining `argparse.ArgumentTypeError` and the existing `plain_number` dependency. Import the six names back into `tools/sample_arguments.py` in both package and direct-script branches, preserving their existing import locations for callers. Leave coordinate/dimension parsing, parser construction, compatibility precedence and region checks in place. Add focused `tests/test_sample_validators.py`; these three files bound the implementation. Read the sampler tooling guarantees in `docs/invariants.md`; this extraction preserves them and adds no option, shared validation framework or dependency.

**Acceptance criteria.** Direct validator tests use literal expected values for optional-`#` mixed-case RGB, byte bounds 0/255, coordinate-list bounds 1/1000, offset zero and a large valid offset, and fraction bounds 0/1 plus decimal and exponent notation. Malformed RGB, out-of-range values, fractional integer inputs, non-ASCII digits, whitespace, nonfinite fractions and oversized integer strings raise `ArgumentTypeError` with the existing diagnostics rather than a traceback. Importing the six names from `tools.sample_arguments` remains supported. CLI cases using package invocation and `python3 tools/sample.py` produce matching successful sample reports and matching status-2 scalar-error diagnostics with empty stdout; package-path invalid cases confirm no PNG header or decode read occurs. Existing option-validation and sampler fixtures still pass, including explicit-zero presence checks and compatibility precedence. Run `make check` after final edits.

## Done
