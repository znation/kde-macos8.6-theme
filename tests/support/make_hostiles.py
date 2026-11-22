"""The shell-hostile make values the Makefile refusal tests drive each guard with.

`HOSTILES` holds the four recipe-shell metacharacters -- a double quote, `$`,
a backtick and a backslash -- as `(char, make_value, shown_value)` triples. The
double-quoted recipe words the guards protect expand each one as shell syntax.
`test_make_refusals.py`, `test_make_refusals_color_scheme.py` and
`test_make_refusals_tools.py` share the table, so each guard is tried with the
same values.
"""

# The guard reads each value raw (`$(value)`), so a `$` arrives as
# written: the make argument `x$$y` stays doubled in the value the guard
# inspects, and the diagnostic collapses the doubling for display (`x$y`).
# The other three characters pass through make verbatim.
HOSTILES = (
    ('"', 'x"; y"', 'x"; y"'),
    ("$", "x$$y", "x$y"),
    ("`", "x`y`", "x`y`"),
    ("\\", "x\\y", "x\\y"),
)
