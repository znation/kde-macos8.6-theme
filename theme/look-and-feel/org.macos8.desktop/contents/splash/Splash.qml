/*
    SPDX-FileCopyrightText: 2026 kde-macos8.6-theme

    SPDX-License-Identifier: GPL-2.0-or-later
*/

import QtQuick

/*
    Mac OS 8.6 Platinum startup splash.

    The artwork is authored on the 240x180 grid of the reference thumbnail
    `macos8.6-screenshots/boot2_betawiki.png`; `unit` scales that grid by whole
    pixels so the layout keeps its proportions on any screen. The colour and
    rectangle literals below are pinned by `tests/test_lookandfeel_splash.py`
    to pixels and colour scans of that reference.
*/
Rectangle {
    id: root
    color: root.fieldColor

    readonly property int unit: Math.max(1, Math.floor(Math.min(width / 240, height / 180)))

    readonly property color fieldColor: "#63639C"
    readonly property color panelBevelColor: "#DDDDDD"
    readonly property color panelColor: "#FFFFFF"
    readonly property color panelRuleColor: "#BFBFBF"
    readonly property color trackColor: "#DDDDDD"
    readonly property color fillColor: "#ADADAD"
    readonly property color wordmarkColor: "#000000"

    // Reference rectangles, in the 240x180 grid. The bevel is the bounding box
    // of the reference's non-field pixels; the panel is the `#BFBFBF` rule
    // that bounds the white face, so its 2px border leaves the reference's
    // white face `x=80..159, y=39..88` inside it.
    readonly property int bevelX: 71
    readonly property int bevelY: 31
    readonly property int bevelWidth: 98
    readonly property int bevelHeight: 76
    readonly property int panelX: 78
    readonly property int panelY: 37
    readonly property int panelWidth: 84
    readonly property int panelHeight: 54
    readonly property int logoX: 107
    readonly property int logoY: 45
    readonly property int logoWidth: 26
    readonly property int logoHeight: 21
    readonly property int trackX: 101
    readonly property int trackY: 94
    readonly property int trackWidth: 38
    readonly property int trackHeight: 9

    property int stage

    onStageChanged: {
        if (stage == 2) {
            introAnimation.running = true
        }
    }

    Item {
        id: content
        width: 240 * root.unit
        height: 180 * root.unit
        anchors.centerIn: parent
        opacity: 0

        Rectangle {
            id: bevel
            x: root.bevelX * root.unit
            y: root.bevelY * root.unit
            width: root.bevelWidth * root.unit
            height: root.bevelHeight * root.unit
            color: root.panelBevelColor
        }

        Rectangle {
            id: panel
            x: root.panelX * root.unit
            y: root.panelY * root.unit
            width: root.panelWidth * root.unit
            height: root.panelHeight * root.unit
            color: root.panelColor
            border.color: root.panelRuleColor
            border.width: 2 * root.unit
        }

        Image {
            id: logo
            x: root.logoX * root.unit
            y: root.logoY * root.unit
            width: root.logoWidth * root.unit
            height: root.logoHeight * root.unit
            source: "images/macos-logo.svg"
            sourceSize.width: width
            sourceSize.height: height
            asynchronous: true
        }

        Text {
            id: wordmark
            anchors.horizontalCenter: panel.horizontalCenter
            y: 71 * root.unit
            text: "Mac OS"
            color: root.wordmarkColor
            font.pixelSize: 12 * root.unit
        }

        Rectangle {
            id: track
            x: root.trackX * root.unit
            y: root.trackY * root.unit
            width: root.trackWidth * root.unit
            height: root.trackHeight * root.unit
            color: root.trackColor

            Rectangle {
                id: fill
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: parent.width * Math.min(1, root.stage / 6)
                color: root.fillColor
            }
        }
    }

    OpacityAnimator {
        id: introAnimation
        running: false
        target: content
        from: 0
        to: 1
        duration: 800
        easing.type: Easing.InOutQuad
    }
}
