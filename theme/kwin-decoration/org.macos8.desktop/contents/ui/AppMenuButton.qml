/*
    SPDX-FileCopyrightText: 2012 Martin Gräßlin <mgraesslin@kde.org>

    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.kirigami 2.20 as Kirigami
import org.kde.kwin.decoration

Item {
    id: appMenuButton
    visible: decoration.client.hasApplicationMenu
    AuroraeButton {
        id: primary
        anchors.fill: parent
        buttonType: DecorationOptions.DecorationButtonApplicationMenu
        visible: AuroraeTheme.appMenuButtonPath
    }
    DecorationButton {
        id: fallback
        anchors.fill: parent
        buttonType: DecorationOptions.DecorationButtonApplicationMenu
        visible: !AuroraeTheme.appMenuButtonPath
        // 2026-11-05: the imported module's DecorationButton shadows the
        // package copy, so gate the fallback's hit area here too.
        enabled: decoration.client.active
        Kirigami.Icon {
            anchors.fill: parent
            source: decoration.client.icon
        }
    }
}
