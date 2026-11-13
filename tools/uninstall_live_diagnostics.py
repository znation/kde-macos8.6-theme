"""The uninstall diagnostics for the live (running user's) config files.

One handler per config surface ``make apply`` writes to the live config home:
``kdeglobals``, the GTK settings files and user CSS,
``Kvantum/kvantum.kvconfig``, ``plasmarc``, ``kcminputrc`` and ``kwinrc``.
Each handler takes the config root and the ids it needs, reads through the
shared scanner in :mod:`uninstall_config` and returns only its own warnings;
the coordinator in :mod:`uninstall_diagnostics` calls them in the recipe's
order, so these handlers cannot change the order ``make uninstall`` prints.
"""

from __future__ import annotations

import os

if __package__:
    from tools.text_lines import BOM
    from tools.uninstall_config import (
        latched_match,
        read_selected_values_at,
        read_text,
    )
else:  # imported from a directly run tool
    from text_lines import BOM
    from uninstall_config import (
        latched_match,
        read_selected_values_at,
        read_text,
    )


# The fixed-width font selection the apply writes after the global-theme
# step: the Qt 6 serialized QFont form naming JetBrains Mono at 10 pt,
# Medium weight (Qt 6 weight 500) with the style name Medium (recorded in
# theme/fonts/org.macos8.desktop/PROVENANCE.md).
FIXED_FONT_VALUE = "JetBrains Mono,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium"


def _font_diagnostics(kde: dict[tuple[str, str], str], path: str) -> list[str]:
    """The six font warnings, one per selection the apply published."""
    diagnoses = (
        (
            ("General", "font"),
            "the font selection [General] font=Lato,10",
            "--group General --key font --delete",
            "Lato,10",
        ),
        (
            ("General", "fixed"),
            "the font selection [General]"
            " fixed=" + FIXED_FONT_VALUE,
            "--group General --key fixed --delete",
            FIXED_FONT_VALUE,
        ),
        (
            ("General", "menuFont"),
            "the font selection [General] menuFont=ChicagoFLF,10",
            "--group General --key menuFont --delete",
            "ChicagoFLF,10",
        ),
        (
            ("General", "toolBarFont"),
            "the font selection [General] toolBarFont=Lato,10",
            "--group General --key toolBarFont --delete",
            "Lato,10",
        ),
        (
            ("General", "smallestReadableFont"),
            "the font selection [General] smallestReadableFont=Lato,8",
            "--group General --key smallestReadableFont --delete",
            "Lato,8",
        ),
        (
            ("WM", "activeFont"),
            "the font selection [WM] activeFont=ChicagoFLF,10",
            "--group WM --key activeFont --delete",
            "ChicagoFLF,10",
        ),
    )
    out = []
    for (section, key), wording, reset_tail, published in diagnoses:
        if kde.get((section, key)) != published:
            continue
        out.append(
            f"uninstall: {wording} the look-and-feel apply wrote is still"
            f" in {path} after removal; KDE and Qt keep naming the selected"
            " font family the removal deleted and fall back to a default where"
            " no other copy of that family remains installed. Reset it with:"
            f" kwriteconfig6 --file kdeglobals {reset_tail}"
        )
    return out


def kdeglobals_messages(
    config_home: str, scheme_id: str, icon_theme_id: str, lnf_id: str
) -> list[str]:
    """The live ``kdeglobals`` selections: scheme, style engine, fonts, LnF."""
    path = os.path.join(config_home, "kdeglobals")
    kde = read_selected_values_at(
        path,
        {
            "General": (
                "ColorScheme",
                "widgetStyle",
                "font",
                "fixed",
                "menuFont",
                "toolBarFont",
                "smallestReadableFont",
            ),
            "WM": ("activeFont",),
            "KDE": ("widgetStyle", "LookAndFeelPackage"),
            "Icons": ("Theme",),
        },
    )
    messages: list[str] = []
    scheme = kde.get(("General", "ColorScheme"))
    if scheme is not None and scheme == scheme_id:
        messages.append(
            f"uninstall: color scheme {scheme_id} is still selected in"
            f" {path} after removal; if KDE cannot resolve it, it"
            " falls back to BreezeLight on the next start. Reset it with:"
            " plasma-apply-colorscheme BreezeLight"
        )
    if kde.get(("KDE", "widgetStyle")) == "kvantum":
        messages.append(
            "uninstall: the widget-style selection the look-and-feel"
            " apply wrote ([KDE] widgetStyle=kvantum) is still in"
            f" {path} after removal; every Qt start keeps"
            " selecting the style that key names whether or not it still"
            " resolves. Reset it with: kwriteconfig6 --file kdeglobals"
            " --group KDE --key widgetStyle --delete"
        )
    if kde.get(("Icons", "Theme")) == icon_theme_id:
        messages.append(
            "uninstall: the icon-theme selection the look-and-feel apply"
            f" wrote ([Icons] Theme={icon_theme_id}) is still in"
            f" {path} after removal; KDE and Qt applications"
            " cannot load the removed icon theme and keep the default"
            " icons. Reset it with: kwriteconfig6 --file kdeglobals"
            " --group Icons --key Theme --delete"
        )
    messages.extend(_font_diagnostics(kde, path))
    if kde.get(("KDE", "LookAndFeelPackage")) == lnf_id:
        messages.append(
            "uninstall: the global theme the look-and-feel apply step"
            f" selected ([KDE] LookAndFeelPackage={lnf_id}) is still in"
            f" {path} after removal; Plasma keeps naming the"
            " removed global theme and draws the stock look-and-feel on"
            " the next start. Reset it with: kwriteconfig6 --file"
            " kdeglobals --group KDE --key LookAndFeelPackage --delete"
        )
    return messages


def gtk_messages(config_home: str, gtk_id: str, css_marker: str) -> list[str]:
    """The GTK settings files and the GTK 4 user CSS naming the theme."""
    chosen = ""
    for ini in (
        os.path.join(config_home, "gtk-3.0", "settings.ini"),
        os.path.join(config_home, "gtk-4.0", "settings.ini"),
    ):
        ini_text = read_text(ini)
        if ini_text is not None and latched_match(
            ini_text, "Settings", "gtk-theme-name", gtk_id
        ):
            chosen = f"{chosen} {ini}"
    css = os.path.join(config_home, "gtk-4.0", "gtk.css")
    # The marker is ASCII, so the same bounded read_text scan the ini files
    # get finds it in the decoded text byte-for-byte; a shared-cap reader
    # cannot read this path while skipping the cap the ini reads have.
    css_text = read_text(css)
    css_first_line = css_text.splitlines()[0] if css_text else ""
    if css_first_line.removeprefix(BOM).startswith(css_marker):
        chosen = f"{chosen} {css}"
    if not chosen:
        return []
    return [
        f"uninstall: a GTK selection still names {gtk_id} after removal"
        f" in{chosen}; GTK applications cannot load the removed theme"
        " and keep their default style. Clear it with: make remove-gtk"
    ]


def kvantum_messages(config_home: str, kvantum_id: str) -> list[str]:
    """The Kvantum theme named in the live kvconfig."""
    path = os.path.join(config_home, "Kvantum", "kvantum.kvconfig")
    kvantum = read_selected_values_at(path, {"General": ("theme",)})
    if kvantum.get(("General", "theme")) == kvantum_id:
        return [
            f"uninstall: the Kvantum selection still names {kvantum_id}"
            f" after removal in {path}; Kvantum applications cannot"
            " load the removed theme and keep their default style."
            " Clear it with: make remove-kvantum"
        ]
    return []


def plasmarc_messages(config_home: str, dtheme_id: str) -> list[str]:
    """The desktop theme named in the live plasmarc."""
    path = os.path.join(config_home, "plasmarc")
    desktop = read_selected_values_at(path, {"Theme": ("name",)})
    if desktop.get(("Theme", "name")) == dtheme_id:
        return [
            "uninstall: the desktop theme selection still names"
            f" {dtheme_id} after removal in {path}; Plasma cannot"
            " load the removed desktop theme and keeps the default"
            " style. Reset it with: plasma-apply-desktoptheme breeze"
        ]
    return []


def kcminputrc_messages(config_home: str, icon_theme_id: str) -> list[str]:
    """The pointer theme named in the live kcminputrc."""
    path = os.path.join(config_home, "kcminputrc")
    mouse = read_selected_values_at(path, {"Mouse": ("cursorTheme",)})
    if mouse.get(("Mouse", "cursorTheme")) == icon_theme_id:
        return [
            "uninstall: the pointer selection still names"
            f" {icon_theme_id} after removal in {path}; Xcursor"
            " applications cannot load the removed cursor theme and"
            " keep the default pointer. Reset it with:"
            " plasma-apply-cursortheme breeze_cursors"
        ]
    return []


def kwinrc_messages(config_home: str, aurorae_id: str) -> list[str]:
    """The live kwinrc decoration keys: button layout and aurorae theme."""
    path = os.path.join(config_home, "kwinrc")
    deco = read_selected_values_at(
        path,
        {"org.kde.kdecoration2": ("ButtonsOnLeft", "ButtonsOnRight", "library", "theme")},
    )
    messages: list[str] = []
    curtain = deco.get(("org.kde.kdecoration2", "ButtonsOnLeft"))
    if curtain == "X" and deco.get(
        ("org.kde.kdecoration2", "ButtonsOnRight")
    ) == "AL":
        messages.append(
            "uninstall: the window-button layout"
            " [ButtonsOnLeft=X, ButtonsOnRight=AL] that make apply wrote"
            f" is still in {path}; KWin keeps that layout under the"
            " default decoration after removal. Reset it with:"
            " kwriteconfig6 --file kwinrc --group org.kde.kdecoration2"
            " --key ButtonsOnLeft --delete && kwriteconfig6 --file"
            " kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight"
            " --delete"
        )
    library = deco.get(("org.kde.kdecoration2", "library"))
    theme = deco.get(("org.kde.kdecoration2", "theme"))
    if library == "org.kde.kwin.aurorae" and theme == aurorae_id:
        messages.append(
            "uninstall: the window-decoration selection"
            f" [library=org.kde.kwin.aurorae, theme={aurorae_id}] that"
            f" the look-and-feel apply wrote is still in {path};"
            " KWin cannot load the removed"
            f" kwin/decorations/{aurorae_id} decoration package and"
            " keeps a default window decoration. Reset it with:"
            " kwriteconfig6 --file kwinrc --group org.kde.kdecoration2"
            " --key library --delete && kwriteconfig6 --file kwinrc"
            " --group org.kde.kdecoration2 --key theme --delete"
        )
    if theme == aurorae_id:
        messages.append(
            "uninstall: the window-decoration selection still names"
            f" {aurorae_id} after removal in {path};"
            " KWin cannot load the removed"
            f" kwin/decorations/{aurorae_id} decoration package and"
            " keeps the default style. Reset it with: kwriteconfig6"
            " --file kwinrc --group org.kde.kdecoration2 --key theme"
            " --delete && kwriteconfig6 --file kwinrc --group"
            " org.kde.kdecoration2 --key library --delete"
        )
    return messages
