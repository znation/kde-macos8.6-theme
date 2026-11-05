/*
    SPDX-FileCopyrightText: 2012 Martin Gräßlin <mgraesslin@kde.org>

    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.ksvg 1.0 as KSvg
import org.kde.kwin.decoration

DecorationButton {
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
    function widthForButton() {
        switch (buttonType) {
        case DecorationOptions.DecorationButtonMenu:
            // menu
            return AuroraeTheme.buttonWidthMenu;
        case DecorationOptions.DecorationButtonApplicationMenu:
            // app menu
            return AuroraeTheme.buttonWidthAppMenu;
        case DecorationOptions.DecorationButtonOnAllDesktops:
            // all desktops
            return AuroraeTheme.buttonWidthAllDesktops;
        case DecorationOptions.DecorationButtonQuickHelp:
            // help
            return AuroraeTheme.buttonWidthHelp;
        case DecorationOptions.DecorationButtonMinimize:
            // minimize
            return AuroraeTheme.buttonWidthMinimize;
        case DecorationOptions.DecorationButtonMaximizeRestore:
            // maximize
            return AuroraeTheme.buttonWidthMaximizeRestore;
        case DecorationOptions.DecorationButtonClose:
            // close
            return AuroraeTheme.buttonWidthClose;
        case DecorationOptions.DecorationButtonKeepAbove:
            // keep above
            return AuroraeTheme.buttonWidthKeepAbove;
        case DecorationOptions.DecorationButtonKeepBelow:
            // keep below
            return AuroraeTheme.buttonWidthKeepBelow;
        case DecorationOptions.DecorationButtonShade:
            // shade
            return AuroraeTheme.buttonWidthShade;
        default:
            return AuroraeTheme.buttonWidth;
        }
    }
    function pathForButton() {
        switch (buttonType) {
        case DecorationOptions.DecorationButtonOnAllDesktops:
            // all desktops
            return AuroraeTheme.allDesktopsButtonPath;
        case DecorationOptions.DecorationButtonQuickHelp:
            // help
            return AuroraeTheme.helpButtonPath;
        case DecorationOptions.DecorationButtonApplicationMenu:
            // app menu
            return AuroraeTheme.appMenuButtonPath;
        case DecorationOptions.DecorationButtonMinimize:
            // minimize
            return AuroraeTheme.minimizeButtonPath;
        case DecorationOptions.DecorationButtonMaximizeRestore:
            // maximize
            return AuroraeTheme.maximizeButtonPath;
        case DecorationOptions.DecorationButtonMaximizeRestore + 100:
            // maximize
            return AuroraeTheme.restoreButtonPath;
        case DecorationOptions.DecorationButtonClose:
            // close
            return AuroraeTheme.closeButtonPath;
        case DecorationOptions.DecorationButtonKeepAbove:
            // keep above
            return AuroraeTheme.keepAboveButtonPath;
        case DecorationOptions.DecorationButtonKeepBelow:
            // keep below
            return AuroraeTheme.keepBelowButtonPath;
        case DecorationOptions.DecorationButtonShade:
            // shade
            return AuroraeTheme.shadeButtonPath;
        default:
            return "";
        }
    }
    width: widthForButton() * AuroraeTheme.buttonSizeFactor
    height: AuroraeTheme.buttonHeight * AuroraeTheme.buttonSizeFactor
    KSvg.FrameSvg {
        property bool supportsHover: hasElementPrefix("hover")
        property bool supportsPressed: hasElementPrefix("pressed")
        property bool supportsDeactivated: hasElementPrefix("deactivated")
        property bool supportsInactive: hasElementPrefix("inactive")
        property bool supportsInactiveHover: hasElementPrefix("hover-inactive")
        property bool supportsInactivePressed: hasElementPrefix("pressed-inactive")
        property bool supportsInactiveDeactivated: hasElementPrefix("deactivated-inactive")
        id: buttonSvg
        imagePath: pathForButton()
    }
    KSvg.FrameSvgItem {
        id: buttonActive
        property bool shown: (decoration.client.active || !buttonSvg.supportsInactive) && ((!pressed && !toggled) || !buttonSvg.supportsPressed) && (!hovered || !buttonSvg.supportsHover) && (enabled || !buttonSvg.supportsDeactivated)
        anchors.fill: parent
        imagePath: buttonSvg.imagePath
        prefix: "active"
        opacity: shown ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: buttonActiveHover
        property bool shown: hovered && !pressed && !toggled && buttonSvg.supportsHover && (decoration.client.active || !buttonSvg.supportsInactiveHover)
        anchors.fill: parent
        imagePath: buttonSvg.imagePath
        prefix: "hover"
        opacity: shown ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: buttonActivePressed
        property bool shown: (toggled || pressed) && buttonSvg.supportsPressed && (decoration.client.active || !buttonSvg.supportsInactivePressed)
        anchors.fill: parent
        imagePath: buttonSvg.imagePath
        prefix: "pressed"
        opacity: shown ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: buttonActiveDeactivated
        property bool shown: !enabled && buttonSvg.supportsDeactivated && (decoration.client.active || !buttonSvg.supportsInactiveDeactivated)
        anchors.fill: parent
        imagePath: buttonSvg.imagePath
        prefix: "deactivated"
        opacity: shown ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: buttonInactive
        property bool shown: !decoration.client.active && buttonSvg.supportsInactive && !hovered && !pressed && !toggled && enabled
        anchors.fill: parent
        imagePath: buttonSvg.imagePath
        prefix: "inactive"
        opacity: shown ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: buttonInactiveHover
        property bool shown: !decoration.client.active && hovered && !pressed && !toggled && buttonSvg.supportsInactiveHover
        anchors.fill: parent
        imagePath: buttonSvg.imagePath
        prefix: "hover-inactive"
        opacity: shown ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: buttonInactivePressed
        property bool shown: !decoration.client.active && (toggled || pressed) && buttonSvg.supportsInactivePressed
        anchors.fill: parent
        imagePath: buttonSvg.imagePath
        prefix: "pressed-inactive"
        opacity: shown ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: buttonInactiveDeactivated
        property bool shown: !decoration.client.active && !enabled && buttonSvg.supportsInactiveDeactivated
        anchors.fill: parent
        imagePath: buttonSvg.imagePath
        prefix: "deactivated-inactive"
        opacity: shown ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    Component.onCompleted: {
        if (buttonType == DecorationOptions.DecorationButtonQuickHelp && !decoration.client.providesContextHelp) {
            visible = false;
        } else {
            visible = buttonSvg.imagePath != "";
        }
    }
}
