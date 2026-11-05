/*
    SPDX-FileCopyrightText: 2012 Martin Gräßlin <mgraesslin@kde.org>

    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.kwin.decoration
import org.kde.kirigami 2.20 as Kirigami

Item {
    id: menuButton
    property int buttonType: DecorationOptions.DecorationButtonMenu
    property bool hovered: false
    property bool pressed: false
    property bool toggled: false
    property bool closeOnDoubleClick: decorationSettings.closeOnDoubleClickOnMenu

    Kirigami.Icon {
        anchors.fill: parent
        source: decoration.client.icon
    }
    DecorationOptions {
        id: options
        deco: decoration
    }
    Timer {
        id: timer
        interval: options.mousePressAndHoldInterval
        repeat: false
        onTriggered: decoration.requestShowWindowMenu()
    }
    MouseArea {
        anchors.fill: parent
        // 2026-11-04, feature role, PLANS.md "Platinum KWin Decoration package,
        // part 3/3": gate the standalone hit area on window activity -- on an
        // unfocused window's flat buttonless bar a long-press here eats the
        // refocusing click and, with closeOnDoubleClick, a second click could
        // even close the window; the active=frontmost direction (2026-11-04) and
        // the package KPackage route (part 1/3's Option A, not Option B's
        // data-home engine shadow) are recorded in this file's package copy.
        enabled: decoration.client.active
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onPressed: {
            parent.pressed = true;
            // we need a timer to figure out whether there is a double click in progress or not
            // if we have a "normal" click we want to open the context menu. This would eat our
            // second click of the double click. To properly get the double click we have to wait
            // the double click delay to ensure that it was only a single click.
            if (timer.running) {
                timer.stop();
            } else if (menuButton.closeOnDoubleClick) {
                timer.start();
            }
        }
        onReleased: {
            parent.pressed = false;
            timer.stop();
        }
        onExited: {
            if (!parent.pressed) {
                return;
            }
            if (timer.running) {
                timer.stop();
            }
            parent.pressed = false;
        }
        onClicked: (mouse) => {
            // for right clicks we show the menu instantly
            // and if the option is disabled we always show menu directly
            if (!menuButton.closeOnDoubleClick || mouse.button == Qt.RightButton) {
                decoration.requestShowWindowMenu();
                timer.stop();
            }
        }
        onDoubleClicked: {
            if (menuButton.closeOnDoubleClick) {
                decoration.requestClose();
            }
        }
    }
}
