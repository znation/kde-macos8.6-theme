"""Wordings and key ids the kwinrc uninstall-diagnostic suites share.

`make _uninstall` (tools/uninstall_live_diagnostics.py) prints the existing
diagnostics whose wordings are each suite's assertion contract. The three
kwinrc suites cover the button-layout, theme-key and library/theme-pair
diagnostics under `kwinrc`'s `[org.kde.kdecoration2]` group, and each
restates the existing wordings its siblings own. Those restated cross-suite
wordings and the group and key ids behind them live here so a wording or
id change lands in one place: `button_rule` feeds all three suites and
`aurorae_pair_rule` feeds two. The group and key ids use the test
modules' names (`REMOVAL_GROUP`, `LEFT_KEY`, `RIGHT_KEY`); the builders
derive the reset wordings from them.

The button-layout, decoration and aurorae suites also stage whole `kwinrc`
bodies made of the group header and two value lines, plain and around
foreign values, duplicates, CRLF endings or other groups; the
`button_body`/`button_lines`, `aurorae_pair_body`/`aurorae_pair_lines` and
`aurorae_theme_body`/`aurorae_theme_lines` builders share those bytes (the
`*_body` builders compose the real `[org.kde.kdecoration2]` header; the
`*_lines` primitives carry only the value lines for the shapes whose header
or surrounding keys the staging test itself owns). Their exact bytes are
pinned by `tests/test_kwinrc_uninstall_wording.py`.

The suites also share the per-file staging helper `write_kwinrc`, whose
single call site per suite stages a whole `kwinrc` body under the scratch
config home, and the composed four-key body `aurorae_pair_body() +
button_lines()` the recipe-order pins stage (our pair plus the button
layout in one file).
"""

from support.theme_install import write_config_file

REMOVAL_GROUP = "org.kde.kdecoration2"
LIBRARY_KEY = "library"
THEME_KEY = "theme"
AURORAE_LIBRARY = "org.kde.kwin.aurorae"
AURORAE_THEME = "org.macos8.desktop"
LEFT_KEY = "ButtonsOnLeft"
RIGHT_KEY = "ButtonsOnRight"
BUTTON_LEFT = "X"
BUTTON_RIGHT = "AL"


def button_lines(*, left=BUTTON_LEFT, right=BUTTON_RIGHT, eol="\n"):
    """The `ButtonsOnLeft=` then `ButtonsOnRight=` value lines with *eol*.

    The `X`/`AL` values are the pair `tools/apply_theme.py::
    DECORATION_BUTTONS` writes; feeds the whole-body builder and the suite
    bodies that put the pair in another header, end the lines differently
    or stage a foreign or empty value on either key.
    """
    return LEFT_KEY + "=" + left + eol + RIGHT_KEY + "=" + right + eol


def button_body(*, left=BUTTON_LEFT, right=BUTTON_RIGHT):
    """A whole `kwinrc` body: our decoration group header plus the pair."""
    return "[" + REMOVAL_GROUP + "]\n" + button_lines(left=left, right=right)


def aurorae_pair_lines(*, library=AURORAE_LIBRARY, theme=AURORAE_THEME, eol="\n"):
    """The `library=` then `theme=` value lines with *eol* endings.

    Feeds the whole-body builders and the suite bodies that put the pair in
    another header, add foreign values or duplicates around it, or end the
    lines differently.
    """
    return LIBRARY_KEY + "=" + library + eol + THEME_KEY + "=" + theme + eol


def aurorae_pair_body(*, library=AURORAE_LIBRARY, theme=AURORAE_THEME):
    """A whole `kwinrc` body: our decoration group header plus the pair."""
    return "[" + REMOVAL_GROUP + "]\n" + aurorae_pair_lines(
        library=library, theme=theme
    )


def aurorae_theme_lines(*, theme=AURORAE_THEME, eol="\n"):
    """The `theme=` value line alone, with *eol* ending."""
    return THEME_KEY + "=" + theme + eol


def aurorae_theme_body(*, theme=AURORAE_THEME):
    """A whole `kwinrc` body: our decoration group header plus only the theme."""
    return "[" + REMOVAL_GROUP + "]\n" + aurorae_theme_lines(theme=theme)


def write_kwinrc(config, body):
    """Write *body* as `<config>/kwinrc`; return its path.

    The three kwinrc uninstall-diagnostic suites stage their bodies
    through this one helper; the three former per-module copies were
    identical.
    """
    return write_config_file(config, "kwinrc", body)


def button_rule(path):
    """The existing button-layout diagnostic's line (the wording is the contract)."""
    return (
        "uninstall: the window-button layout "
        f"[{LEFT_KEY}=X, {RIGHT_KEY}=AL] that make apply wrote is still in "
        f"{path}; KWin keeps that layout under the default decoration after "
        "removal. Reset it with: kwriteconfig6 --file kwinrc --group "
        f"{REMOVAL_GROUP} --key {LEFT_KEY} --delete && kwriteconfig6 --file "
        f"kwinrc --group {REMOVAL_GROUP} --key {RIGHT_KEY} --delete"
    )


def aurorae_pair_rule(path):
    """The existing library/theme-pair diagnostic's line (the wording is the contract)."""
    return (
        "uninstall: the window-decoration selection "
        f"[{LIBRARY_KEY}={AURORAE_LIBRARY}, {THEME_KEY}={AURORAE_THEME}] "
        f"that the look-and-feel apply wrote is still in {path}; KWin cannot "
        "load the removed kwin/decorations/org.macos8.desktop decoration "
        "package and keeps a default window "
        "decoration. Reset it with: kwriteconfig6 --file kwinrc --group "
        f"{REMOVAL_GROUP} --key {LIBRARY_KEY} --delete && kwriteconfig6 "
        f"--file kwinrc --group {REMOVAL_GROUP} --key {THEME_KEY} --delete"
    )
