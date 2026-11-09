/*
    SPDX-FileCopyrightText: 2012 Martin Gräßlin <mgraesslin@kde.org>

    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.kwin.decoration

Item {
    id: button
    width: AuroraeTheme.buttonWidthMaximizeRestore * AuroraeTheme.buttonSizeFactor
    height: AuroraeTheme.buttonHeight * AuroraeTheme.buttonSizeFactor
    property bool hovered: false
    property bool pressed: false
    property bool toggled: false
    AuroraeButton {
        id: maximizeButton
        anchors.fill: parent
        buttonType: DecorationOptions.DecorationButtonMaximizeRestore
        opacity: (!decoration.client.maximized || AuroraeTheme.restoreButtonPath == "") ? 1 : 0
        hovered: button.hovered
        pressed: button.pressed
        toggled: button.toggled
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    AuroraeButton {
        id: restoreButton
        anchors.fill: parent
        buttonType: DecorationOptions.DecorationButtonMaximizeRestore + 100
        opacity: (decoration.client.maximized && AuroraeTheme.restoreButtonPath != "") ? 1 : 0
        hovered: button.hovered
        pressed: button.pressed
        toggled: button.toggled
        Behavior on opacity {
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    MouseArea {
        anchors.fill: parent
        // 2026-11-04, feature role, PLANS-DONE.md "Platinum KWin Decoration package,
        // part 3/3": gate the standalone hit area on window activity -- the
        // maximize/restore cell on an unfocused window's flat buttonless bar
        // maximized windows meant only to be refocused; the active=frontmost
        // direction (2026-11-04) and the package KPackage route (part 1/3's
        // Option A, not Option B's data-home engine shadow) are recorded in this
        // package's copy of the engine file (AuroraeTheme singleton spelling).
        enabled: decoration.client.active
        acceptedButtons: {
            return Qt.LeftButton | Qt.RightButton | Qt.MiddleButton;
        }
        hoverEnabled: true
        onEntered: button.hovered = true
        onExited: button.hovered = false
        onPressed: button.pressed = true
        onReleased: button.pressed = false
        onClicked: {
            decoration.requestToggleMaximization(mouse.button);
        }
    }
}
