# Invariants

What each shipped surface guarantees, in one sentence, and the test that pins it.
Read the matching row before changing a surface; when a change adds or alters a
guarantee, update this register in the same change. Every `theme/` subsystem has a
section, and the render/fidelity tooling lives under [tooling](#tooling) because it
is not a `theme/` subsystem. `tests/invariants.py` cross-checks this file
against the repository: a `theme/` subsystem with no section, a section naming
no `theme/` subsystem or extra section, a repeated section heading, a row naming
a test that does not exist, a row naming no test, a malformed table row, or a
blank guarantee or provenance-exception cell fails `make check`.

## aurorae

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The active title-bar boxes are re-derived from the reference screenshots; the inactive greyed boxes are KDE-required because the reference's inactive windows draw no close, zoom or collapse box. | `tests/test_aurorae_buttons.py::TestButtons` | The reference's inactive windows draw no close, zoom or collapse box in their title bars, so the inactive boxes' flat #CCCCCC face has no reference pixel (`macos8.6-screenshots/sources.txt`). |
| The active frame nine-slice is re-derived from the reference screenshots, the inactive nine-slice from `desktop_fandom.png`'s four unfocused windows, and the gzipped `decoration.svgz` matches the uncompressed artwork. | `tests/test_aurorae_frame.py::TestDecorationSvg` | none |
| The title-bar height and border widths the Aurorae engine reads are re-derived from the reference screenshots. | `tests/test_aurorae_rc.py::TestRc` | none |
| The package metadata and install lifecycle are what KPackage and Aurorae discovery read. | `tests/test_aurorae_package.py::TestMetadata` | none |
| The beta `aboutsystem_betawiki.png` window chrome is pixel-identical to the retail `systemprofiler_betawiki.png`. | `tests/test_aurorae_reference_equivalence.py::TestReferenceEquivalence` | `aboutsystem_betawiki.png` is a beta build used as a window-chrome proxy; the render gate's bottom-border crop stays on it because the set has no other lossless window-bottom crop (README, `macos8.6-screenshots/sources.txt`). |

## color-schemes

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| Every sampled palette anchor is still the pixel it was sampled from in a retail screenshot. | `tests/test_colorscheme_reference.py::TestReferenceAnchors` | none |
| The scheme's sections, keys and palette anchors are complete and well-formed. | `tests/test_colorscheme.py::TestStructure` | none |
| The tooltip token is documented as a KDE-required role with no reference screenshot. | `tests/test_colorscheme.py::TestProvenanceNote` | `[Colors:Tooltip] BackgroundNormal` has no Mac OS 8.6 reference in the set; its value comes from the classic Platinum palette (QUESTIONS.md, answered 2026-10-08). |

## desktoptheme

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| Every shipped desktop-theme SVG shares one root canvas. | `tests/test_desktoptheme.py::TestSvgRootCanvas` | none |
| `widgets/actionbutton.svg` draws the Platinum round action button. | `tests/test_desktoptheme_actionbutton.py::TestActionButton` | none |
| `widgets/action-overlays.svg` draws the Platinum desktop icon action buttons. | `tests/test_desktoptheme_actionoverlays.py::TestActionOverlays` | none |
| `widgets/arrows.svg` draws the popup and dropdown arrows. | `tests/test_desktoptheme_arrows.py::TestArrows` | none |
| `widgets/background.svg` draws the Platinum menu body, and its `widgets/translucentbackground.svg` copy is byte-identical. | `tests/test_desktoptheme_background.py::TestBackground` | none |
| `widgets/busywidget.svg` draws the Platinum busy indicator ring. | `tests/test_desktoptheme_busywidget.py::TestBusyWidget` | none |
| `widgets/button.svg` draws the normal and pressed push button. | `tests/test_desktoptheme_button.py::TestButton` | none |
| `widgets/button.svg`'s raised bevel shadow is the reference's #AAAAAA. | `tests/test_desktoptheme_button_reference.py::TestButtonReference` | The reference's raised button bevel is the Get Info popup button (`aboutsystem_betawiki.png`), a beta build; the reference's rounded push buttons are only in the lossy `opendialog_macrumors86.jpg`. |
| `widgets/checkmarks.svg` draws the black check and the radio indicator dot. | `tests/test_desktoptheme_checkmarks.py::TestCheckmarks` | none |
| `dialogs/background.svg` draws the Platinum window body. | `tests/test_desktoptheme_dialog.py::TestDialogBackground` | none |
| `dialogs/background.svg`'s raised bevel shadow and mixed corners are the reference Get Info body's #AAAAAA and #DDDDDD. | `tests/test_desktoptheme_dialog.py::TestDialogBackgroundRaisedReference` | The reference window body is the beta `aboutsystem_betawiki.png` Get Info window inside the 6px Aurorae frame; the retail sunken fields keep #999999. |
| `widgets/frame.svg` draws the Platinum plain, raised and sunken frames. | `tests/test_desktoptheme_frame.py::TestFrame` | none |
| `widgets/lineedit.svg` draws the white sunken text field. | `tests/test_desktoptheme_lineedit.py::TestLineEdit` | none |
| `widgets/line.svg` draws the etched separator. | `tests/test_desktoptheme_line.py::TestLine` | none |
| `widgets/listitem.svg` draws the selection row. | `tests/test_desktoptheme_listitem.py::TestListItem` | none |
| `widgets/menubaritem.svg` draws the menu-bar title background. | `tests/test_desktoptheme_menubaritem.py::TestMenuBarItem` | none |
| `widgets/panel-background.svg` draws the menu bar, including its top-panel north state, and its `solid/` copy is byte-identical. | `tests/test_desktoptheme_panel.py::TestPanelBackground` | none |
| `widgets/plasmoidheading.svg` draws the popup band. | `tests/test_desktoptheme_plasmoidheading.py::TestPlasmoidHeading` | none |
| `widgets/bar_meter_horizontal.svg` draws the Platinum progress bar. | `tests/test_desktoptheme_progressbar.py::TestProgressBar` | none |
| `widgets/radiobutton.svg` draws the white radio face and its selection dot. | `tests/test_desktoptheme_radiobutton.py::TestRadioButton` | none |
| `widgets/scrollbar.svg` draws the Platinum scroll bar trough and thumb. | `tests/test_desktoptheme_scrollbar.py::TestScrollbar` | none |
| `widgets/slider.svg` draws the Platinum slider groove and handle. | `tests/test_desktoptheme_slider.py::TestSlider` | none |
| `widgets/switch.svg` draws the Platinum toggle track and thumb. | `tests/test_desktoptheme_switch.py::TestSwitch` | none |
| `widgets/tabbar.svg` draws the Platinum tab bar. | `tests/test_desktoptheme_tabbar.py::TestTabBar` | none |
| `widgets/tabbar.svg`'s `*-active-tab` face and top/left bevel are the reference active-window selected tab's (`#EEEEEE` face, `#CCCCCC` mid-tone, `#FFFFFF` highlight). | `tests/test_desktoptheme_tabbar.py::TestTabBarReference` | The reference tab is a trapezoid; the nine-slice is rectangular (PLANS-DONE.md). |
| `widgets/toolbar.svg` draws the Platinum toolbar background. | `tests/test_desktoptheme_toolbar.py::TestToolBar` | none |
| `widgets/tooltip.svg` draws the Platinum tooltip. | `tests/test_desktoptheme_tooltip.py::TestTooltip` | none |
| `widgets/viewitem.svg` draws the generic item highlight. | `tests/test_desktoptheme_viewitem.py::TestViewItem` | none |
| The `viewitem.svg`, `menubaritem.svg` and `arrows.svg` provenance comments name the reference screenshot their claim rests on and do not claim the set shows no such surface. | `tests/test_desktoptheme_provenance.py::TestProvenance` | none |

## gtk

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The standalone GTK 3 Platinum theme redefines the Platinum palette and paints the scoped Platinum control rules, including every plain and reorderable tab state, without importing Adwaita. | `tests/test_gtk_theme.py::TestGtkTheme` | No reference screenshot shows a GTK widget, so the palette comes from the pinned Platinum values and the geometry is this theme's adaptation. |
| The standalone GTK 4 stylesheet redefines the Platinum palette and opaque GTK 4 surface colours and paints the scoped Platinum control rules, including every tab state, without importing another stylesheet. | `tests/test_gtk4_theme.py::TestGtk4Theme` | No reference screenshot shows a GTK widget, so the palette comes from the pinned Platinum values and the geometry is this theme's adaptation. |
| The GTK 3 and GTK 4 suites read their `index.theme` and `gtk.css` through the shared containment reader, so a checked-in symlink that escapes the repository is refused instead of leaking a private file's text into a failing test's diagnostic. | `tests/test_gtk_theme.py::TestGtkTheme::test_theme_read_refuses_a_symlink_escape` | none |
| The shared GTK stylesheet parser removes comments and pairs rule blocks without the quadratic backtracking of the regular expressions it replaced, so a contributor-supplied `gtk.css` with many unterminated comment starts or a long unbraced run cannot stall the suite. | `tests/test_gtk_css.py::TestHostileStylesheet` | none |

## icons

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The icon theme names our own final Platinum art, ships exactly the tracked icons, and declares each icon's size directory. | `tests/test_icon_theme.py::TestIndex` | The art is our own drawing, not Apple's; the reference set has no pixel ground truth for it. |
| Every shipped icon draws its pinned drawing elements in document order, and the `inode-directory` alias shares the folder art. | `tests/test_icon_theme.py::TestIconGeometry` | The art is our own drawing, not Apple's; the reference set has no pixel ground truth for it. |
| The submenu arrow is the reference's 5x9 solid black right triangle. | `tests/test_icon_arrow_reference.py::TestSubmenuArrowReference` | The 16px canvas is KDE-required; the reference menu row is ~17px. |

## kvantum

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| Every `GeneralColors` entry is grounded in the color scheme or the Platinum palette. | `tests/test_kvantum_config.py::TestGeneralColors` | none |
| Every core and special control section resolves to the grounded frame margin. | `tests/test_kvantum_config.py::TestFrameMargins` | none |
| Every core control section maps to the pinned SVG element it draws. | `tests/test_kvantum_config_elements.py::TestCoreControlElements` | none |
| Every `.kvconfig` section is pinned by a frame-margin, element-mapping or frameless table. | `tests/test_kvantum_config.py::TestSectionCoverage` | none |
| Every non-element `.kvconfig` setting (indicator sizes, label colours, text margins, `min_height`, shadow flags, `composite`) is pinned to its value. | `tests/test_kvantum_config.py::TestValueKeys` | none |
| The SVG ships each frame element's centre and eight slices. | `tests/test_kvantum_svg.py::TestSvg` | none |
| Each indicator arrow draws its pinned triangle and its per-state fill. | `tests/test_kvantum_svg.py::TestSvg` | none |
| Each check box and radio button interior draws its pinned child shapes in document order. | `tests/test_kvantum_svg.py::TestSvg` | none |
| The check box face is the reference's raised Platinum square. | `tests/test_kvantum_checkbox_reference.py::TestCheckBoxReference` | The reference's check box is a beta build (`aboutsystem_betawiki.png`, `systeminfo_betawiki.png`); no retail screenshot shows a check box. |
| The button bevel is the reference's raised popup-button bevel. | `tests/test_kvantum_button_reference.py::TestButtonReference` | The reference's popup button is a beta build (`aboutsystem_betawiki.png`); it is the set's only lossless raised-button bevel. |
| The combo box indicator is the reference's double up/down arrow in a 12x12 `#DDDDDD` cell. | `tests/test_kvantum_combobox_reference.py::TestComboBoxReference` | The popup is from an 8.6a3c2 beta build (`systeminfo_betawiki.png`), and the cell's divider and right bevel are frame art, not indicator art. |
| The tab face is the reference System Profiler tabs' unselected #CCCCCC and selected #EEEEEE Platinum palette. | `tests/test_kvantum_tab_reference.py::TestTabReference` | none |
| The line edit is the reference's sunken field: the bevel outside the #000000 outline. | `tests/test_kvantum_lineedit_reference.py::TestLineEditReference` | none |
| The item view is the reference's sunken field: the bevel outside the #000000 outline. | `tests/test_kvantum_itemview_reference.py::TestItemViewReference` | The reference item view's top-right and bottom-right corners sit under the status header and the scrollbars, so its bottom-right corner follows the line edit's grounded corner (`macos8.6-screenshots/sources.txt`). |
| Each slider cursor, progress-bar pattern, splitter grip and grip interior draws its pinned child shapes in document order. | `tests/test_kvantum_svg.py::TestSvg` | none |

## look-and-feel

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The global theme's `contents/defaults` selects the color scheme, desktop theme, icon theme, window decoration, wallpaper and Kvantum widget style. | `tests/test_lookandfeel.py::TestDefaults` | none |
| The desktop layout's panel, widget order, clock format and desktop icons match the reference. | `tests/test_lookandfeel_layout.py::TestLayout` | none |

## wallpapers

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The shipped wallpaper tile reproduces the reference desktop pattern. | `tests/test_wallpaper.py::TestReferenceTile` | none |

## tooling

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The fidelity gate passes only when no pixel differs beyond its tolerance, or within an aggregate budget when one is given. | `tests/test_fidelity_cli.py::TestCli` | none |
| The rendered window's title-bar strip is byte-identical to the same strip of the reference screenshot. | `tests/test_render_surface.py::TestRender::test_title_bar_matches_the_reference` | none |
| The rendered window's side and bottom border strips are byte-identical to the same strips of the reference screenshot. | `tests/test_render_surface.py::TestRender::test_frame_borders_match_the_reference` | none |
| The rendered window's title-bar boxes (close, zoom, collapse) are byte-identical to the same regions of the reference screenshots. | `tests/test_render_surface.py::TestRender::test_title_bar_boxes_match_the_reference` | none |
| `INSTALL_PACKAGES` names only known artifact families, so `make install` copies at least one artifact or refuses before creating the data home. | `tests/test_theme_install.py::TestInstallPackagesGuard` | none |
| No contributor-file reader reimplements the containment guard; each routes through the shared `tools.containment` module. | `tests/test_containment.py::TestGuardIsShared` | none |
| The lexical containment boundary accepts the root itself and every path below it, including a filesystem root and a POSIX double-leading-slash spelling of the same directory, while rejecting a sibling directory that shares the root's prefix. | `tests/test_containment.py::TestIsWithin` | none |
| The three KDE INI readers (`support.kde_config.read`, `theme_defaults.defaults_groups` and the `uninstall` recipe's `awk`) agree on one shared corpus's `[General] ColorScheme` selection: `=` is the only key/value delimiter (a colon-delimited line is ignored), each line is trimmed, section and key names are case-sensitive, the last duplicate key wins, a leading UTF-8 BOM is stripped, a present but empty value is distinct from a missing key, and a group header with no closing `]` is ignored (the open section continues). An empty `[]` header starts its own group, so the following key does not join the previous section, and `support.kde_config.read` keeps a key before the first heading in KDE's `<default>` root group instead of treating it as invalid. `defaults_groups` instead refuses a malformed heading because its headings name output files. | `tests/test_kde_ini_parity.py::TestReadersAgree` | none |
| The shared contributor-file readers refuse a FIFO or device by name, checking the opened descriptor so a path swapped for a FIFO cannot block the read. | `tests/test_containment.py` | none |
| The KDE INI test reader reads through the shared containment reader, so a FIFO at a theme INI or `contents/defaults` is refused instead of blocking. | `tests/test_kde_config.py::TestReadKdeConfig::test_refuses_a_fifo_instead_of_blocking` | none |
| The global theme's `contents/defaults` reader refuses a FIFO or device by name instead of blocking on open. | `tests/test_theme_defaults.py::TestDefaultsGroups` | none |
| The package-metadata test reader reads through the shared containment reader, so a `metadata.json` FIFO is refused instead of blocking and an oversize one is refused instead of being loaded whole. | `tests/test_package_metadata.py::TestLoadMetadata` | none |
| The splash QML test reader reads through the shared containment reader, so a FIFO at its path is refused instead of blocking and an oversize file is refused instead of being loaded whole. | `tests/test_splash_qml.py::TestSplashQmlContainment` | none |
| The placeholder marker and register readers read through the shared containment reader, so a FIFO at a theme asset or the register is refused instead of blocking and an oversize one is refused instead of being loaded whole. | `tests/test_placeholders.py::TestHelpers` | none |
| The Aurorae decoration test reader refuses a FIFO or device by name instead of blocking the read: `decoration.svg` is parsed through the shared SVG guard (`SvgCase.setUp`), and `decoration.svgz` is decompressed through the shared containment guard. | `tests/test_aurorae_frame.py::TestReadCappedContainment::test_refuses_a_fifo_instead_of_blocking` | none |
