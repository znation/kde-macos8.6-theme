"""Small KDE INI texts that every project reader is checked against.

KConfig (observed with `kreadconfig6` 6.13.0) treats ``=`` as the only
key/value delimiter -- a ``ColorScheme:MacOS8`` line is an invalid entry and is
ignored -- trims each line before parsing, keeps section and key names
case-sensitive, lets a later duplicate key override an earlier one, treats only
a leading ``#`` as a comment, and keeps a ``#`` inside a value in that value.
The project's readers also strip a leading UTF-8 BOM, a deliberate leniency
(KConfig logs a BOM-prefixed first line as invalid) so an editor-saved file
still loads. A line that opens a group header but never closes it (``[General``)
is one more invalid entry KConfig skips: a following key stays in the section
that is still open. A key before the first header is not ignored: KConfig
files it in the ``<default>`` root group, and an empty ``[]`` header opens a
group of its own, so a key after it does not join the previous group.

`CASES` holds one small text per rule; `tests/test_kde_ini_parity.py` feeds
each through the test-side reader, `tools.theme_defaults.defaults_groups` and
the `uninstall` recipe's `awk`, so a rule learned by one reader fails in the
others. A case's expected value is the ``[General] ColorScheme`` KDE resolves,
or None when it resolves none. ``defaults_raises`` marks a malformed-heading
case that `defaults_groups` refuses instead of skipping: its headings name
output files, so a silently dropped heading would drop a config section.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# The scheme id `make uninstall` warns about; a fixture selecting it through
# the recipe's color-scheme reader must make the recipe warn.
SCHEME_ID = "MacOS8"

# The first plain ``[group]`` heading in a generic INI text. The leading class
# keeps any indentation and a UTF-8 BOM in front of the bracket, and the
# lookahead accepts a CRLF line ending without consuming its carriage return.
_PLAIN_HEADING = re.compile(
    r"^([ \t\ufeff]*)\[([^\[\]]+)\](?=\r?$)", re.MULTILINE
)


@dataclass(frozen=True)
class Case:
    """One rule-bearing KDE INI text and the selection KDE resolves from it."""

    name: str
    text: str
    expected: str | None
    defaults_raises: bool = False


CASES = (
    Case("plain value", "[General]\nColorScheme=MacOS8\n", "MacOS8"),
    Case(
        "CRLF line endings",
        "[General]\r\nColorScheme=MacOS8\r\n",
        "MacOS8",
    ),
    Case(
        "BOM and CRLF line endings",
        "\ufeff[General]\r\nColorScheme=MacOS8\r\n",
        "MacOS8",
    ),
    Case(
        "leading UTF-8 BOM",
        "\ufeff[General]\nColorScheme=MacOS8\n",
        "MacOS8",
    ),
    Case(
        "indented section header",
        "  [General]\nColorScheme=MacOS8\n",
        "MacOS8",
    ),
    Case(
        "indented key and padded value",
        "[General]\n  ColorScheme = MacOS8  \n",
        "MacOS8",
    ),
    Case(
        "last duplicate key wins",
        "[General]\nColorScheme=BreezeLight\nColorScheme=MacOS8\n",
        "MacOS8",
    ),
    Case(
        "later duplicate overrides",
        "[General]\nColorScheme=MacOS8\nColorScheme=BreezeLight\n",
        "BreezeLight",
    ),
    Case(
        "key case is significant",
        "[General]\ncolorscheme=MacOS8\n",
        None,
    ),
    Case(
        "section case is significant",
        "[general]\nColorScheme=MacOS8\n",
        None,
    ),
    Case(
        "colon is not a delimiter",
        "[General]\nColorScheme:MacOS8\n",
        None,
    ),
    Case(
        "colon line is skipped",
        "[General]\nColorScheme:MacOS8\nColorScheme=BreezeLight\n",
        "BreezeLight",
    ),
    Case(
        "semicolon is not a comment",
        "[General]\n;ColorScheme=BreezeLight\nColorScheme=MacOS8\n",
        "MacOS8",
    ),
    Case(
        "malformed header before any section",
        "[General\nColorScheme=MacOS8\n",
        None,
        defaults_raises=True,
    ),
    Case(
        "malformed header keeps the previous section",
        "[General]\nColorScheme=BreezeLight\n[Broken\nColorScheme=MacOS8\n",
        "MacOS8",
        defaults_raises=True,
    ),
    Case(
        "key before the first heading is the root group",
        "ColorScheme=BreezeLight\n[General]\nColorScheme=MacOS8\n",
        "MacOS8",
    ),
    Case(
        "empty group header before a section",
        "[]\nColorScheme=MacOS8\n",
        None,
    ),
    Case(
        "empty group header after a section",
        "[General]\nColorScheme=BreezeLight\n[]\nColorScheme=MacOS8\n",
        "BreezeLight",
    ),
    Case(
        "comments and blank lines",
        "# note\n\n[General]\n# another\nColorScheme=MacOS8\n",
        "MacOS8",
    ),
    Case(
        "hash inside a value",
        "[General]\nColorScheme=MacOS8 # tail\n",
        "MacOS8 # tail",
    ),
    Case(
        "percent inside a value",
        "[General]\nColorScheme=100%\n",
        "100%",
    ),
    Case(
        "equals inside a value",
        "[General]\nColorScheme=MacOS8=Extra\n",
        "MacOS8=Extra",
    ),
    Case("empty value", "[General]\nColorScheme=\n", ""),
)


def as_defaults(text: str) -> str:
    """Return *text* with its first plain ``[group]`` heading made a defaults heading.

    ``contents/defaults`` names a target file in the heading
    (``[kdeglobals][General]``), so the corpus text is rewritten into that
    dialect before `defaults_groups` reads it. The rule-bearing lines below
    the heading are unchanged.
    """
    return _PLAIN_HEADING.sub(r"\1[kdeglobals][\2]", text, count=1)
