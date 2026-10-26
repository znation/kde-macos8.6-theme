# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### The selector matcher reads a comma in `:not(...)` as a descendant step, so the negation matches almost every element (found by the steward role 2026-10-26)

**Symptom.** `tests/support/selector_matching.py`'s `_selector_is_supported` accepts
`:not(.a, .b)` as supported, and `matches` then returns True for a parentless element with
class `a` or `b`, and for a class-`a` element even under a class-`a` parent; a browser
matches none of those against that selector. The only False case found is a class-`b`
element under a class-`a` ancestor. A future scope test written against such a selector
would pass its "does not match" assertions for almost every element and let an over-broad
sheet rule through. No selector in
`theme/firefox/org.macos8.desktop/chrome/userChrome.css` puts a comma inside `:not(...)`
(grep), so no shipped assertion is mis-evaluated today; the gap is latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.selector_matching import element, matches, _selector_is_supported; e = element("toolbarbutton", classes={"a"}); print(matches(":not(.a, .b)", e)); print(_selector_is_supported(":not(.a, .b)"))'
```

prints `True` then `True`. An element with class `b` whose parent has class `a` returns
`False` instead, so `.a, .b` behaves like the descendant selector `.a .b`.

**Suspected cause.** `_split_selector` treats only whitespace and `>` as combinators (and
rejects `+`/`~`); a comma inside `:not(...)` stays in the compound, where
`_compound_is_supported` accepts it and `_compound_matches` reads the two class fragments
as a descendant chain. `tests/support/gtk_css.py::_split_selector_list` deliberately keeps
the comma inside `:not(...)` together, pinned by
`tests/test_gtk_css.py::TestRuleBlockSemantics::test_a_comma_inside_parentheses_does_not_split_the_group`,
so the matcher must either reject a selector-list argument as unsupported or evaluate it
as a list rather than treating it as supported.

## Fixed
