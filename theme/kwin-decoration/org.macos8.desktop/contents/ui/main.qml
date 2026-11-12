/*
    SPDX-FileCopyrightText: 2012 Martin Gräßlin <mgraesslin@kde.org>

    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.kwin.decoration
import org.kde.ksvg 1.0 as KSvg

Decoration {
    id: root
    property bool animate: false
    property alias decorationMask: maskItem.mask
    property alias supportsMask: backgroundSvg.supportsMask
    Component.onCompleted: {
        borders.left   = Qt.binding(function() { return Math.max(0, AuroraeTheme.borderLeft);});
        borders.right  = Qt.binding(function() { return Math.max(0, AuroraeTheme.borderRight);});
        borders.top    = Qt.binding(function() { return Math.max(0, AuroraeTheme.borderTop);});
        borders.bottom = Qt.binding(function() { return Math.max(0, AuroraeTheme.borderBottom);});
        maximizedBorders.left   = Qt.binding(function() { return Math.max(0, AuroraeTheme.borderLeftMaximized);});
        maximizedBorders.right  = Qt.binding(function() { return Math.max(0, AuroraeTheme.borderRightMaximized);});
        maximizedBorders.bottom = Qt.binding(function() { return Math.max(0, AuroraeTheme.borderBottomMaximized);});
        maximizedBorders.top    = Qt.binding(function() { return Math.max(0, AuroraeTheme.borderTopMaximized);});
        padding.left   = AuroraeTheme.paddingLeft;
        padding.right  = AuroraeTheme.paddingRight;
        padding.bottom = AuroraeTheme.paddingBottom;
        padding.top    = AuroraeTheme.paddingTop;
        root.animate = true;
    }
    DecorationOptions {
        id: options
        deco: decoration
    }
    Item {
        id: titleRect
        x: decoration.client.maximized ? maximizedBorders.left : borders.left
        y: decoration.client.maximized ? 0 : root.borders.bottom
        width: decoration.client.width//parent.width - x - (decoration.client.maximized ? maximizedBorders.right : borders.right)
        height: decoration.client.maximized ? maximizedBorders.top : borders.top
        Component.onCompleted: {
            decoration.installTitleItem(titleRect);
        }
    }
    KSvg.FrameSvg {
        property bool supportsInactive: hasElementPrefix("decoration-inactive")
        property bool supportsMask: hasElementPrefix("mask")
        property bool supportsMaximized: hasElementPrefix("decoration-maximized")
        property bool supportsMaximizedInactive: hasElementPrefix("decoration-maximized-inactive")
        property bool supportsInnerBorder: hasElementPrefix("innerborder")
        property bool supportsInnerBorderInactive: hasElementPrefix("innerborder-inactive")
        id: backgroundSvg
        imagePath: AuroraeTheme.decorationPath
    }
    KSvg.FrameSvgItem {
        id: decorationActive
        property bool shown: (!decoration.client.maximized || !backgroundSvg.supportsMaximized) && (decoration.client.active || !backgroundSvg.supportsInactive)
        anchors.fill: parent
        imagePath: backgroundSvg.imagePath
        prefix: "decoration"
        opacity: shown ? 1 : 0
        enabledBorders: decoration.client.maximized ? KSvg.FrameSvg.NoBorder : KSvg.FrameSvg.TopBorder | KSvg.FrameSvg.BottomBorder | KSvg.FrameSvg.LeftBorder | KSvg.FrameSvg.RightBorder
        Behavior on opacity {
            enabled: root.animate
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: decorationInactive
        anchors.fill: parent
        imagePath: backgroundSvg.imagePath
        prefix: "decoration-inactive"
        opacity: (!decoration.client.active && backgroundSvg.supportsInactive) ? 1 : 0
        enabledBorders: decoration.client.maximized ? KSvg.FrameSvg.NoBorder : KSvg.FrameSvg.TopBorder | KSvg.FrameSvg.BottomBorder | KSvg.FrameSvg.LeftBorder | KSvg.FrameSvg.RightBorder
        Behavior on opacity {
            enabled: root.animate
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: decorationMaximized
        property bool shown: decoration.client.maximized && backgroundSvg.supportsMaximized && (decoration.client.active || !backgroundSvg.supportsMaximizedInactive)
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            leftMargin: 0
            rightMargin: 0
            topMargin: 0
        }
        imagePath: backgroundSvg.imagePath
        prefix: "decoration-maximized"
        height: parent.maximizedBorders.top
        opacity: shown ? 1 : 0
        enabledBorders: KSvg.FrameSvg.NoBorder
        Behavior on opacity {
            enabled: root.animate
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: decorationMaximizedInactive
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            leftMargin: 0
            rightMargin: 0
            topMargin: 0
        }
        imagePath: backgroundSvg.imagePath
        prefix: "decoration-maximized-inactive"
        height: parent.maximizedBorders.top
        opacity: (!decoration.client.active && decoration.client.maximized && backgroundSvg.supportsMaximizedInactive) ? 1 : 0
        enabledBorders: KSvg.FrameSvg.NoBorder
        Behavior on opacity {
            enabled: root.animate
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    AuroraeButtonGroup {
        id: leftButtonGroup
        buttons: options.titleButtonsLeft
        width: childrenRect.width
        animate: root.animate
        anchors {
            left: root.left
            leftMargin: decoration.client.maximized ? AuroraeTheme.titleEdgeLeftMaximized : (AuroraeTheme.titleEdgeLeft + root.padding.left)
        }
    }
    AuroraeButtonGroup {
        id: rightButtonGroup
        buttons: options.titleButtonsRight
        width: childrenRect.width
        animate: root.animate
        anchors {
            right: root.right
            rightMargin: decoration.client.maximized ? AuroraeTheme.titleEdgeRightMaximized : (AuroraeTheme.titleEdgeRight + root.padding.right)
        }
    }
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
    Text {
        id: caption
        text: decoration.client.caption
        textFormat: Text.PlainText
        horizontalAlignment: AuroraeTheme.horizontalAlignment
        verticalAlignment: AuroraeTheme.verticalAlignment
        elide: Text.ElideRight
        height: Math.max(AuroraeTheme.titleHeight, AuroraeTheme.buttonHeight * AuroraeTheme.buttonSizeFactor)
        color: decoration.client.active ? AuroraeTheme.activeTextColor : AuroraeTheme.inactiveTextColor
        font: options.titleFont
        renderType: Text.NativeRendering
        anchors {
            left: leftButtonGroup.right
            right: rightButtonGroup.left
            top: root.top
            topMargin: decoration.client.maximized ? AuroraeTheme.titleEdgeTopMaximized : (AuroraeTheme.titleEdgeTop + root.padding.top)
            leftMargin: AuroraeTheme.titleBorderLeft
            rightMargin: AuroraeTheme.titleBorderRight
        }
        Behavior on color {
            enabled: root.animate
            ColorAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: innerBorder
        anchors {
            fill: parent
            leftMargin: parent.padding.left + parent.borders.left - margins.left
            rightMargin: parent.padding.right + parent.borders.right - margins.right
            topMargin: parent.padding.top + parent.borders.top - margins.top
            bottomMargin: parent.padding.bottom + parent.borders.bottom - margins.bottom
        }
        visible: parent.borders.left > fixedMargins.left
            && parent.borders.right > fixedMargins.right
            && parent.borders.top > fixedMargins.top
            && parent.borders.bottom > fixedMargins.bottom

        imagePath: backgroundSvg.imagePath
        prefix: "innerborder"
        opacity: (decoration.client.active && !decoration.client.maximized && backgroundSvg.supportsInnerBorder) ? 1 : 0
        Behavior on opacity {
            enabled: root.animate
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: innerBorderInactive
        anchors {
            fill: parent
            leftMargin: parent.padding.left + parent.borders.left - margins.left
            rightMargin: parent.padding.right + parent.borders.right - margins.right
            topMargin: parent.padding.top + parent.borders.top - margins.top
            bottomMargin: parent.padding.bottom + parent.borders.bottom - margins.bottom
        }

        visible: parent.borders.left > fixedMargins.left
            && parent.borders.right > fixedMargins.right
            && parent.borders.top > fixedMargins.top
            && parent.borders.bottom > fixedMargins.bottom

        imagePath: backgroundSvg.imagePath
        prefix: "innerborder-inactive"
        opacity: (!decoration.client.active && !decoration.client.maximized && backgroundSvg.supportsInnerBorderInactive) ? 1 : 0
        Behavior on opacity {
            enabled: root.animate
            NumberAnimation {
                duration: AuroraeTheme.animationTime
            }
        }
    }
    KSvg.FrameSvgItem {
        id: maskItem
        anchors.fill: parent
        // This makes the mask slightly smaller than the frame. Since the svg will have antialiasing and the mask not,
        // there will be artifacts at the corners, if they go under the svg they're less evident
        anchors.margins: 1
        imagePath: backgroundSvg.imagePath
        opacity: 0
        enabledBorders: KSvg.FrameSvg.TopBorder | KSvg.FrameSvg.BottomBorder | KSvg.FrameSvg.LeftBorder | KSvg.FrameSvg.RightBorder
    }
}
