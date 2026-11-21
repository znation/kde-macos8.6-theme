"""Expected texts and the manifest for the org.macos8.desktop engine copies.

The package's QML copies of the KWin 6.3.6 Aurorae engine files under
`/usr/share/kwin/aurorae/`: which copies are byte-equal, which need only the
`auroraeTheme` to `AuroraeTheme` rename, and which add a window-activity gate
or caption band on top of the rename. Each expected text is re-derived from
the engine file on disk. Consumed by tests/test_kwin_decoration_copies.py and
by the singleton pins in tests/test_kwin_decoration_package.py.
"""

from __future__ import annotations

from support.aurorae_fixtures import AURORAE_ID
from support.repo_root import ROOT

ENGINE_DIR = "/usr/share/kwin/aurorae"
PACKAGE_DIR = f"{ROOT}/theme/kwin-decoration/{AURORAE_ID}"

# The engine files the package copies byte-equal (no `auroraeTheme` source
# token), and the rename each engine file needs. `aurorae.qml` ships as
# `main.qml`, the component Helper::loadComponent() reads. Part 3/3 and the
# 2026-11-05 shadow fix moved the gated copies out of these tuples into the
# expectations that follow: equal-plus-gate, not plain equal.
BYTE_EQUAL_COPIES = ("Decoration.qml",)
RENAMED_COPIES = (
    ("aurorae.qml", "main.qml"),
    ("AuroraeButtonGroup.qml", "AuroraeButtonGroup.qml"),
    ("AuroraeMaximizeButton.qml", "AuroraeMaximizeButton.qml"),
)

# The part 3/3 hit-area gating (2026-11-04): the package copy equals its engine
# file with only the additions below, so an un-gated copy or an engine byte
# touched anywhere else fails. The comments are the dated plan-notes the
# copies carry; each expected text re-derives from the engine file on disk.
DECORATION_BUTTON_COMMENT = """\
    // 2026-11-04, feature role, PLANS-DONE.md "Platinum KWin Decoration package,
    // part 3/3": Platinum is active=frontmost (the 2026-11-04 direction), so an
    // unfocused window's bar is the flat buttonless strip its empty
    // inactive-centre art draws while this button's hit cell stayed live and a
    // click meant only to refocus could close or maximize the window. This
    // KWin/Decoration package copy -- run instead of the engine file only through
    // the loadComponent() KPackage route, the Option A plan part 1/3 chose over
    // Option B's data-home shadow of the shared engine component -- gates the
    // interactive hit area on window activity. Geometry and art are untouched:
    // active windows draw and press as before, and on an unfocused window the
    // disabled Item drops its MouseArea so the click falls through to the title
    // bar's activate.
"""
MENU_BUTTON_COMMENT = """\
        // 2026-11-04, feature role, PLANS-DONE.md "Platinum KWin Decoration package,
        // part 3/3": gate the standalone hit area on window activity -- on an
        // unfocused window's flat buttonless bar a long-press here eats the
        // refocusing click and, with closeOnDoubleClick, a second click could
        // even close the window; the active=frontmost direction (2026-11-04) and
        // the package KPackage route (part 1/3's Option A, not Option B's
        // data-home engine shadow) are recorded in this file's package copy.
"""
MAXIMIZE_BUTTON_COMMENT = """\
        // 2026-11-04, feature role, PLANS-DONE.md "Platinum KWin Decoration package,
        // part 3/3": gate the standalone hit area on window activity -- the
        // maximize/restore cell on an unfocused window's flat buttonless bar
        // maximized windows meant only to be refocused; the active=frontmost
        // direction (2026-11-04) and the package KPackage route (part 1/3's
        // Option A, not Option B's data-home engine shadow) are recorded in this
        // package's copy of the engine file (AuroraeTheme singleton spelling).
"""
DECORATION_BUTTON_COMMENT_HEAD = "    id: button\n"
ENABLED_BLOCK_HEAD = "    enabled: {\n"
MOUSEAREA_HEAD = "    MouseArea {\n        anchors.fill: parent\n"
INACTIVE_GUARD = """\
        if (!decoration.client.active) {
            return false;
        }
"""
INACTIVE_MOUSEAREA_GATE = "        enabled: decoration.client.active\n"

# The 2026-11-05 shadowing fix: the imported module's DecorationButton wins
# over the package's same-named base file, so the effective gate moved onto
# the AuroraeButton subclass item and the AppMenuButton fallback.
AURORAE_BUTTON_GATE = """\
    // 2026-11-05: the imported `org.kde.kwin.decoration` module also provides
    // a `DecorationButton`, and the explicit import wins over this package's
    // same-named local file -- so the base copy's `enabled` gate never ran and
    // an unfocused window's close, maximize and shade cells stayed live.
    // Gate this subclass item itself, reproducing the base's capability
    // switch; a disabled item drops its inherited MouseArea, so the click
    // falls through to the title bar's activation.
    enabled: {
        if (!decoration.client.active) {
            return false;
        }
        switch (buttonType) {
        case DecorationOptions.DecorationButtonClose:
            return decoration.client.closeable;
        case DecorationOptions.DecorationButtonMaximizeRestore:
            return decoration.client.maximizeable;
        case DecorationOptions.DecorationButtonMinimize:
            return decoration.client.minimizeable;
        case DecorationOptions.DecorationButtonExplicitSpacer:
            return false;
        default:
            return true;
        }
    }
"""
APP_MENU_VISIBLE_HEAD = "        visible: !AuroraeTheme.appMenuButtonPath\n"
APP_MENU_FALLBACK_GATE = """\
        // 2026-11-05: the imported module's DecorationButton shadows the
        // package copy, so gate the fallback's hit area here too.
        enabled: decoration.client.active
"""


def expected_gated_aurorae_button(engine):
    """The package AuroraeButton.qml copy: rename, then the subclass gate.

    2026-11-05: the imported org.kde.kwin.decoration module exports its own
    DecorationButton, so the package base copy is shadowed and the effective
    hit-area gate lives on this subclass item.
    """
    renamed = engine.replace("auroraeTheme.", "AuroraeTheme.")
    assert renamed.count("DecorationButton {\n") == 1, ENGINE_DIR
    gated = renamed.replace(
        "DecorationButton {\n",
        "DecorationButton {\n" + AURORAE_BUTTON_GATE,
        1,
    )
    visibility = '''    Component.onCompleted: {
        if (buttonType == DecorationOptions.DecorationButtonQuickHelp && !decoration.client.providesContextHelp) {
            visible = false;
        } else {
            visible = buttonSvg.imagePath != "";
        }
    }'''
    assert gated.count(visibility) == 1, ENGINE_DIR
    return gated.replace(
        visibility,
        '''    visible: Qt.binding(function() {
        return buttonSvg.imagePath != "" &&
               (buttonType != DecorationOptions.DecorationButtonShade || decoration.client.shadeable) &&
               (buttonType != DecorationOptions.DecorationButtonQuickHelp || decoration.client.providesContextHelp);
    })''',
        1,
    )


def expected_gated_app_menu_button(engine):
    """The package AppMenuButton.qml copy: rename and the fallback gate."""
    renamed = engine.replace("auroraeTheme.", "AuroraeTheme.")
    assert renamed.count(APP_MENU_VISIBLE_HEAD) == 1, ENGINE_DIR
    return renamed.replace(
        APP_MENU_VISIBLE_HEAD,
        APP_MENU_VISIBLE_HEAD + APP_MENU_FALLBACK_GATE,
        1,
    )


def expected_gated_decoration_button(engine):
    """The package DecorationButton.qml copy: comment, then the guarded switch."""
    assert engine.count(DECORATION_BUTTON_COMMENT_HEAD) == 1, ENGINE_DIR
    copy = engine.replace(
        DECORATION_BUTTON_COMMENT_HEAD,
        DECORATION_BUTTON_COMMENT_HEAD + DECORATION_BUTTON_COMMENT,
    )
    assert copy.count(ENABLED_BLOCK_HEAD) == 1, ENGINE_DIR
    return copy.replace(ENABLED_BLOCK_HEAD, ENABLED_BLOCK_HEAD + INACTIVE_GUARD)


def expected_gated_menu_button(engine):
    """The package MenuButton.qml copy: the enabled MouseArea, comment first."""
    assert engine.count(MOUSEAREA_HEAD) == 1, ENGINE_DIR
    return engine.replace(
        MOUSEAREA_HEAD,
        MOUSEAREA_HEAD + MENU_BUTTON_COMMENT + INACTIVE_MOUSEAREA_GATE,
    )


def expected_gated_aurorae_maximize_button(engine):
    """The package AuroraeMaximizeButton.qml copy: rename, comment, gate."""
    renamed = engine.replace("auroraeTheme.", "AuroraeTheme.")
    assert renamed.count(MOUSEAREA_HEAD) == 1, ENGINE_DIR
    return renamed.replace(
        MOUSEAREA_HEAD,
        MOUSEAREA_HEAD + MAXIMIZE_BUTTON_COMMENT + INACTIVE_MOUSEAREA_GATE,
    )


# The 2026-11-12 caption gap: the package main.qml copy adds a solid band
# behind the caption, the way Mac OS 8.6 clears the title-bar pinstripes
# behind the title text (reference apps_macrumors8.6.jpg, columns sampled
# 2026-11-12). The engine caption Text is untouched; the band sits before it
# so the Text paints on top.
CAPTION_HEAD = "    Text {\n        id: caption\n"
CAPTION_GAP_BLOCK = """\
    // 2026-11-12, caption gap: Mac OS 8.6 clears the title-bar pinstripes
    // behind the caption -- the reference screenshots draw a solid #CCCCCC
    // band the width of the painted caption plus about 4px each side,
    // spanning the stripe rows while the frame's top highlight and bottom
    // rule stay (apps_macrumors8.6.jpg "About This Computer", pixel columns
    // sampled 2026-11-12) -- so the title reads over the stripes. The band
    // shows only on an active window: the inactive art is stripe-free.
    Rectangle {
        id: captionGap
        color: "#cccccc"
        visible: decoration.client.active
        // The band is the painted caption plus 4px each side, never wider
        // than the space between the button groups.
        property real bandWidth: Math.min(caption.width, caption.contentWidth + 8)
        x: {
            if (caption.horizontalAlignment === Text.AlignRight) {
                return caption.x + caption.width - bandWidth;
            }
            if (caption.horizontalAlignment === Text.AlignHCenter) {
                return caption.x + (caption.width - bandWidth) / 2;
            }
            return caption.x;
        }
        y: caption.y + 2
        width: bandWidth
        height: caption.height - 4
    }
"""


def expected_gated_main(engine):
    """The package main.qml copy: rename, then the caption gap band."""
    renamed = engine.replace("auroraeTheme.", "AuroraeTheme.")
    assert renamed.count(CAPTION_HEAD) == 1, ENGINE_DIR
    return renamed.replace(CAPTION_HEAD, CAPTION_GAP_BLOCK + CAPTION_HEAD, 1)


# Renamed copies that carry a gated addition on top of the theme-token
# rename; the plain rename-only expectation does not apply to them.
RENAMED_GATED_COPIES = {
    "AuroraeMaximizeButton.qml": expected_gated_aurorae_maximize_button,
    "main.qml": expected_gated_main,
}


GATED_COPIES = (
    ("DecorationButton.qml", expected_gated_decoration_button),
    ("MenuButton.qml", expected_gated_menu_button),
    ("AuroraeMaximizeButton.qml", expected_gated_aurorae_maximize_button),
    ("AuroraeButton.qml", expected_gated_aurorae_button),
    ("AppMenuButton.qml", expected_gated_app_menu_button),
)


def read_text(path):
    """Return the UTF-8 text at *path*."""
    with open(path, encoding="utf-8") as handle:
        return handle.read()


