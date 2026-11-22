"""Shared helpers for the `_uninstall` kdedefaults mirror diagnostic suites.

The warn suite (test_kdedefaults_mirror_uninstall_diagnostic) and the silence
suite (test_kdedefaults_mirror_uninstall_silence) share these wordings and
staging helpers; each rule's wording is the assertion contract.
"""

import os

from support import theme_install
from support.tmp_dir import make_config_home

LNF_ID = "org.macos8.desktop"




def widget_rule(path):
    """The expected mirror widget-style line (the wording is the contract)."""
    return (
        "uninstall: the widget-style selection the look-and-feel apply left "
        "in defaults ([KDE] widgetStyle=kvantum) is still in " + path +
        " after removal; when the live key is absent or reset away, the "
        "defaults layer re-selects the style that key names. Reset it with: "
        "kwriteconfig6 --file \"" + path + "\" --group KDE --key widgetStyle "
        "--delete"
    )


def icons_rule(path):
    """The expected mirror icon-theme line (the wording is the contract)."""
    return (
        "uninstall: the icon-theme selection the look-and-feel apply left "
        "in defaults ([Icons] Theme=" + LNF_ID + ") is still in " + path +
        " after removal; when the live key is absent or reset away, the "
        "defaults layer re-selects the removed icon theme and KDE and Qt "
        "applications keep the default icons. Reset it with: kwriteconfig6 "
        "--file \"" + path + "\" --group Icons --key Theme --delete"
    )


def mirror_kwinrc_rule(path):
    """The expected mirror decoration-pair line (wording is the contract)."""
    return (
        "uninstall: the window-decoration selection [library="
        "org.kde.kwin.aurorae, theme=" + LNF_ID +
        "] that the look-and-feel apply left in defaults is still in " +
        path + "; when the live keys are absent or reset away, the defaults "
        "layer re-selects the removed kwin/decorations/org.macos8.desktop "
        "decoration package and KWin keeps a "
        "default window decoration. Reset it with: kwriteconfig6 --file \"" +
        path + "\" --group org.kde.kdecoration2 --key library --delete && "
        "kwriteconfig6 --file \"" + path +
        "\" --group org.kde.kdecoration2 --key theme --delete"
    )


def mirror_plasmarc_rule(path):
    """The expected mirror desktop-theme line (wording is the contract)."""
    return (
        "uninstall: the desktop theme selection the look-and-feel apply "
        "left in defaults still names " + LNF_ID + " after removal in" +
        " " + path + "; when the live key is absent or reset away, the "
        "defaults layer re-selects the removed desktop theme. Reset it "
        "with: kwriteconfig6 --file \"" + path + "\" --group Theme --key name "
        "--delete"
    )


def scratch_home(case):
    """A temporary config home with the `kdedefaults/` directory created."""
    tmp, config = make_config_home(case)
    os.makedirs(os.path.join(config, "kdedefaults"), exist_ok=True)
    return tmp, config


def run_uninstall(tmp, config, env=None):
    """Run the uninstall recipe with XDG_CONFIG_HOME at *config*, or with *env*."""
    return theme_install.uninstall_recipe(
        tmp,
        extra=(),
        env=env if env is not None else dict(os.environ, XDG_CONFIG_HOME=config),
    )


def mirror_paths(config):
    """The three mirror paths under *config*, in recipe order."""
    return (
        os.path.join(config, "kdedefaults", "kdeglobals"),
        os.path.join(config, "kdedefaults", "kwinrc"),
        os.path.join(config, "kdedefaults", "plasmarc"),
    )
