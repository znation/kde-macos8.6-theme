/*
    Platinum KWin decoration package theme metrics, one QtObject singleton
    resolved through the package directory's qmldir implicit import.

    KWin 6.3.6's Decoration::init() sets only the `decoration` and
    `decorationSettings` context properties for a `KWin/Decoration` KPackage,
    so the package resolves the theme metrics itself (upstream
    src/plugins/kdecorations/aurorae/src/aurorae.cpp). Every named value is
    derived the way the engine's SVG-Aurorae path derives it from the
    installed org.macos8.desktoprc (upstream Aurorae::ThemeConfig::load),
    with the measurement provenance a per-property source comment spells:
    - `rc:` the org.macos8.desktoprc key the value re-derives from;
    - `engine:` the upstream v6.3.6 derivation when the rc names no key
      (themeconfig.cpp's readEntry defaults and AuroraeTheme's own
      derivation);
    - `path:` the aurorae art relative walk to the SVG family `make install`
      places beside this package, resolved at load time into a local path
      string for the KSvg.FrameSvg `imagePath` the copies feed.

    `ui/` -> `contents/` -> `org.macos8.desktop/` -> `decorations/` ->
    `kwin/` -> the data home `make install` places both families under, so
    the five-level walk below is independent of DESTDIR and XDG_DATA_HOME.
    Upstream distinguishes file existence: AuroraeTheme::BUTTON_PATH returns
    an empty string for a widget SVG the aurorae package does not ship, so
    the path set spells the walk only for the files the aurorae family
    ships (decoration, close, maximize, restore, shade) and leaves the
    others empty.

    The values below are the 96 dpi derivation (upstream ThemeConfig::load
    scales every Layout read by the primary screen's dpi/96, and the
    borders() prefactors default to KDecoration3::BorderSize::Normal): the
    render-gate sessions this project targets.
*/
// 2026-11-04: the singleton's only import. A KWin/Decoration QML package
// loads this file through the package qmldir's implicit import alone, which
// provides no types: QtObject and the color valuetype live on QtQuick, the
// import every engine QML file names.
pragma Singleton
import QtQuick

QtObject {
    id: auroraeTheme

    // `path:` converts the package-relative walk into a local path string
    // for the KSvg.FrameSvg `imagePath` the copies feed.
    function asLocalPath(name) {
        // Qt.resolvedUrl answers a QUrl here, not a string (TypeError: slice
        // is not a function on the 2026-11-04 session probe), so stringify
        // before the prefix walk below.
        var url = Qt.resolvedUrl(name).toString();
        var prefix = "file://";
        if (url.slice(0, prefix.length) === prefix) {
            return decodeURIComponent(url.slice(prefix.length));
        }
        return url;
    }

    // General group
    // rc: ActiveTextColor=0,0,0
    property color activeTextColor: "#000000"
    // rc: InactiveTextColor=119,119,119
    property color inactiveTextColor: "#777777"
    // rc: TitleAlignment=Center -> upstream ThemeConfig::load maps Center
    // to Qt::AlignHCenter (int 4)
    property int horizontalAlignment: 4
    // rc: TitleVerticalAlignment=Center -> upstream maps Center to
    // Qt::AlignVCenter (int 128)
    property int verticalAlignment: 128
    // rc: Animation=0
    property int animationTime: 0
    // engine: upstream AuroraeTheme::buttonSizeFactor() returns 1.0 for the
    // default ButtonSize (KDecoration3::BorderSize::Normal)
    property real buttonSizeFactor: 1.0
    // engine: upstream defaultExplicitButtonSpacer() = 10
    property int explicitButtonSpacer: 10

    // Layout group: buttons
    // rc: ButtonWidth=13
    property int buttonWidth: 13
    // rc: ButtonHeight=13
    property int buttonHeight: 13
    // rc: ButtonWidthMaximizeRestore=21
    property int buttonWidthMaximizeRestore: 21
    // engine: upstream defaults every per-button width to ButtonWidth when
    // the rc names no key (themeconfig.cpp's readEntry defaults), and
    // AppMenu to ButtonWidthMenu
    // engine: default ButtonWidth=13
    property int buttonWidthMinimize: 13
    // engine: default ButtonWidth=13
    property int buttonWidthClose: 13
    // engine: default ButtonWidth=13
    property int buttonWidthAllDesktops: 13
    // engine: default ButtonWidth=13
    property int buttonWidthKeepAbove: 13
    // engine: default ButtonWidth=13
    property int buttonWidthKeepBelow: 13
    // engine: default ButtonWidth=13
    property int buttonWidthShade: 13
    // engine: default ButtonWidth=13
    property int buttonWidthHelp: 13
    // engine: default ButtonWidth=13
    property int buttonWidthMenu: 13
    // engine: default ButtonWidthAppMenu = ButtonWidthMenu = 13
    property int buttonWidthAppMenu: 13
    // rc: ButtonSpacing=0
    property int buttonSpacing: 0
    // rc: ButtonMarginTop=4
    property int buttonMarginTop: 4
    // Reference: title-bar boxes begin 4px below the maximized bar's top edge.
    property int buttonMarginTopMaximized: 4

    // Layout group: borders -- upstream AuroraeTheme::borders() derives the
    // exposed values from the rc metrics and never reads the rc BorderTop
    // key; the side values are the rc's clamped to BorderSize::Normal's
    // 4..6 range
    // engine: rc BorderLeft=6 clamped 4..6 -> 6
    property int borderLeft: 6
    // engine: rc BorderRight=6 clamped 4..6 -> 6
    property int borderRight: 6
    // engine: rc BorderBottom=6 clamped 4..6 -> 6
    property int borderBottom: 6
    // engine: title = max(TitleHeight=22, ButtonHeight=13 * factor 1.0 +
    // ButtonMarginTop=4 -> 17) + TitleEdgeTop=0 + TitleEdgeBottom=1 -> 23
    property int borderTop: 23
    // engine: maximized title = max(22, 17) + TitleEdgeTopMaximized=0 +
    // TitleEdgeBottomMaximized=0 -> 22
    property int borderTopMaximized: 22
    // engine: maximized DecorationTop -> no side borders
    property int borderBottomMaximized: 0
    // engine: maximized DecorationTop -> no side borders
    property int borderLeftMaximized: 0
    // engine: maximized DecorationTop -> no side borders
    property int borderRightMaximized: 0

    // Layout group: title
    // rc: TitleHeight=22
    property int titleHeight: 22
    // rc: TitleEdgeTop=0
    property int titleEdgeTop: 0
    // rc: TitleEdgeLeft=4
    property int titleEdgeLeft: 4
    // rc: TitleEdgeRight=4
    property int titleEdgeRight: 4
    // engine: upstream defaultTitleEdgeTopMaximized() = 0
    property int titleEdgeTopMaximized: 0
    // engine: upstream defaultTitleEdgeLeftMaximized() = 0
    property int titleEdgeLeftMaximized: 0
    // engine: upstream defaultTitleEdgeRightMaximized() = 0
    property int titleEdgeRightMaximized: 0
    // engine: upstream defaultTitleBorderLeft() = 5
    property int titleBorderLeft: 5
    // engine: upstream defaultTitleBorderRight() = 5
    property int titleBorderRight: 5

    // Layout group: padding -- engine: upstream default Padding* = 0; the
    // rc names no Padding key
    // engine: default 0
    property int paddingTop: 0
    // engine: default 0
    property int paddingBottom: 0
    // engine: default 0
    property int paddingLeft: 0
    // engine: default 0
    property int paddingRight: 0

    // Paths: the aurorae art family make install places beside this package.
    // path: decoration.svg
    property string decorationPath: asLocalPath("../../../../../aurorae/themes/org.macos8.desktop/decoration.svg")
    // path: close.svg
    property string closeButtonPath: asLocalPath("../../../../../aurorae/themes/org.macos8.desktop/close.svg")
    // path: maximize.svg
    property string maximizeButtonPath: asLocalPath("../../../../../aurorae/themes/org.macos8.desktop/maximize.svg")
    // path: restore.svg
    property string restoreButtonPath: asLocalPath("../../../../../aurorae/themes/org.macos8.desktop/restore.svg")
    // path: shade.svg
    property string shadeButtonPath: asLocalPath("../../../../../aurorae/themes/org.macos8.desktop/shade.svg")
    // engine: the aurorae package ships no minimize.svg -> empty (upstream
    // BUTTON_PATH returns an empty string)
    property string minimizeButtonPath: ""
    // engine: no alldesktops.svg -> empty
    property string allDesktopsButtonPath: ""
    // engine: no keepabove.svg -> empty
    property string keepAboveButtonPath: ""
    // engine: no keepbelow.svg -> empty
    property string keepBelowButtonPath: ""
    // engine: no help.svg -> empty
    property string helpButtonPath: ""
    // engine: no appmenu.svg -> empty
    property string appMenuButtonPath: ""
}
