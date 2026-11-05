/*
    SPDX-FileCopyrightText: 2012 Martin Gräßlin <mgraesslin@kde.org>

    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.kwin.decoration

Item {
    function createButtons() {
        var component = Qt.createComponent("AuroraeButton.qml");
        for (var i=0; i<buttons.length; i++) {
            if (buttons[i] == DecorationOptions.DecorationButtonExplicitSpacer) {
                Qt.createQmlObject("import QtQuick 2.0; Item { width: AuroraeTheme.explicitButtonSpacer * AuroraeTheme.buttonSizeFactor; height: AuroraeTheme.buttonHeight * AuroraeTheme.buttonSizeFactor }",
                    groupRow, "explicitSpacer" + buttons + i);
            } else if (buttons[i] == DecorationOptions.DecorationButtonMenu) {
                Qt.createQmlObject("import QtQuick 2.0; MenuButton { width: AuroraeTheme.buttonWidthMenu * AuroraeTheme.buttonSizeFactor; height: AuroraeTheme.buttonHeight * AuroraeTheme.buttonSizeFactor }",
                    groupRow, "menuButton" + buttons + i);
            } else if (buttons[i] == DecorationOptions.DecorationButtonApplicationMenu) {
                Qt.createQmlObject("import QtQuick 2.0; AppMenuButton { width: AuroraeTheme.buttonWidthAppMenu * AuroraeTheme.buttonSizeFactor; height: AuroraeTheme.buttonHeight * AuroraeTheme.buttonSizeFactor }",
                    groupRow, "appMenuButton" + buttons + i);
            } else if (buttons[i] == DecorationOptions.DecorationButtonMaximizeRestore) {
                var maximizeComponent = Qt.createComponent("AuroraeMaximizeButton.qml");
                maximizeComponent.createObject(groupRow);
            } else {
                component.createObject(groupRow, {buttonType: buttons[i]});
            }
        }
    }
    id: group
    property var buttons
    property bool animate: false

    Row {
        id: groupRow
        spacing: AuroraeTheme.buttonSpacing * AuroraeTheme.buttonSizeFactor
    }
    onButtonsChanged: {
        for (var i = 0; i < groupRow.children.length; i++) {
            groupRow.children[i].destroy();
        }
        createButtons();
    }
    anchors {
        top: root.top
        topMargin: (decoration.client.maximized ? AuroraeTheme.titleEdgeTopMaximized + AuroraeTheme.buttonMarginTopMaximized : AuroraeTheme.titleEdgeTop + root.padding.top + AuroraeTheme.buttonMarginTop)
    }
}
