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
"""

REMOVAL_GROUP = "org.kde.kdecoration2"
LIBRARY_KEY = "library"
THEME_KEY = "theme"
AURORAE_LIBRARY = "org.kde.kwin.aurorae"
AURORAE_THEME = "org.macos8.desktop"
LEFT_KEY = "ButtonsOnLeft"
RIGHT_KEY = "ButtonsOnRight"


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
