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

The two decoration suites also stage whole `kwinrc` bodies made of the group
header and the `library=`/`theme=` value lines, plain and around foreign
values, duplicates, CRLF endings or other groups; the `aurorae_pair_body`,
`aurorae_pair_lines`, `aurorae_theme_body` and `aurorae_theme_lines`
builders share those bytes (`aurorae_pair_body` and `aurorae_theme_body`
compose the real `[org.kde.kdecoration2]` header; the `_lines` primitives
carry only the value lines for the shapes whose header or surrounding keys
the staging test itself owns). Their exact bytes are pinned by
`tests/test_kwinrc_uninstall_wording.py`.
"""

REMOVAL_GROUP = "org.kde.kdecoration2"
LIBRARY_KEY = "library"
THEME_KEY = "theme"
AURORAE_LIBRARY = "org.kde.kwin.aurorae"
AURORAE_THEME = "org.macos8.desktop"
LEFT_KEY = "ButtonsOnLeft"
RIGHT_KEY = "ButtonsOnRight"


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
