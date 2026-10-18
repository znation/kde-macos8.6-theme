# Invariants

What each shipped surface guarantees, in one sentence, and the test that pins it.
Read the matching row before changing a surface; when a change adds or alters a
guarantee, update this register in the same change. Every `theme/` subsystem has a
section, and the render/fidelity tooling lives under [tooling](#tooling) because it
is not a `theme/` subsystem. `tests/test_invariants.py` cross-checks this file
against the repository: a `theme/` subsystem with no section, a row naming a test
that does not exist, or a blank guarantee cell fails `make check`.

## aurorae

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The active and inactive title-bar boxes are re-derived from the reference screenshots. | `tests/test_aurorae_buttons.py::TestButtons` | none |
| The active and inactive frame nine-slices and the gzipped `decoration.svgz` are re-derived from the reference screenshots. | `tests/test_aurorae_frame.py::TestDecorationSvg` | none |
| The title-bar height and border widths the Aurorae engine reads are re-derived from the reference screenshots. | `tests/test_aurorae_rc.py::TestRc` | none |
| The package metadata and install lifecycle are what KPackage and Aurorae discovery read. | `tests/test_aurorae_package.py::TestMetadata` | none |

## color-schemes

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| Every sampled palette anchor is still the pixel it was sampled from in a retail screenshot. | `tests/test_colorscheme_reference.py::TestReferenceAnchors` | none |
| The scheme's sections, keys and palette anchors are complete and well-formed. | `tests/test_colorscheme.py::TestStructure` | none |
| The tooltip token is documented as a KDE-required role with no reference screenshot. | `tests/test_colorscheme.py::TestProvenanceNote` | `[Colors:Tooltip] BackgroundNormal` has no Mac OS 8.6 reference in the set; its value comes from the classic Platinum palette (QUESTIONS.md, answered 2026-10-08). |

## desktop-themes

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| Every shipped desktop-theme SVG shares one root canvas. | `tests/test_desktoptheme.py::TestSvgRootCanvas` | none |
| `arrows.svg` draws the popup and dropdown arrows. | `tests/test_desktoptheme_arrows.py::TestArrows` | none |
| `widgets/background.svg` draws the Platinum menu body. | `tests/test_desktoptheme_background.py::TestBackground` | none |
| `busywidget.svg` draws the Platinum busy indicator ring. | `tests/test_desktoptheme_busywidget.py::TestBusyWidget` | none |
| `button.svg` draws the normal and pressed push button. | `tests/test_desktoptheme_button.py::TestButton` | none |
| `checkmarks.svg` draws the black check and the radio indicator dot. | `tests/test_desktoptheme_checkmarks.py::TestCheckmarks` | none |
| `dialogs/background.svg` draws the Platinum window body. | `tests/test_desktoptheme_dialog.py::TestDialogBackground` | none |
| `frame.svg` draws the Platinum plain, raised and sunken frames. | `tests/test_desktoptheme_frame.py::TestFrame` | none |
| `lineedit.svg` draws the white sunken text field. | `tests/test_desktoptheme_lineedit.py::TestLineEdit` | none |
| `line.svg` draws the etched separator. | `tests/test_desktoptheme_line.py::TestLine` | none |
| `listitem.svg` draws the selection row. | `tests/test_desktoptheme_listitem.py::TestListItem` | none |
| `menubaritem.svg` draws the menu-bar title background. | `tests/test_desktoptheme_menubaritem.py::TestMenuBarItem` | none |
| `widgets/panel-background.svg` draws the menu bar, including its top-panel north state. | `tests/test_desktoptheme_panel.py::TestPanelBackground` | none |
| `plasmoidheading.svg` draws the popup band. | `tests/test_desktoptheme_plasmoidheading.py::TestPlasmoidHeading` | none |
| `bar_meter_horizontal.svg` draws the Platinum progress bar. | `tests/test_desktoptheme_progressbar.py::TestProgressBar` | none |
| `radiobutton.svg` draws the white radio face and its selection dot. | `tests/test_desktoptheme_radiobutton.py::TestRadioButton` | none |
| `scrollbar.svg` draws the Platinum scroll bar and its arrows. | `tests/test_desktoptheme_scrollbar.py::TestScrollbar` | none |
| `slider.svg` draws the Platinum slider groove and handle. | `tests/test_desktoptheme_slider.py::TestSlider` | none |
| `switch.svg` draws the Platinum toggle track and thumb. | `tests/test_desktoptheme_switch.py::TestSwitch` | none |
| `tabbar.svg` draws the Platinum tab bar. | `tests/test_desktoptheme_tabbar.py::TestTabBar` | none |
| `widgets/toolbar.svg` draws the Platinum toolbar background. | `tests/test_desktoptheme_toolbar.py::TestToolBar` | none |
| `widgets/tooltip.svg` draws the Platinum tooltip. | `tests/test_desktoptheme_tooltip.py::TestTooltip` | none |
| `viewitem.svg` draws the generic item highlight. | `tests/test_desktoptheme_viewitem.py::TestViewItem` | none |

## icons

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The icon theme names our own final Platinum art, ships exactly the tracked icons, and declares each icon's size directory. | `tests/test_icon_theme.py::TestIndex` | The art is our own drawing, not Apple's; the reference set has no pixel ground truth for it. |

## kvantum

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| Every `GeneralColors` entry is grounded in the color scheme or the Platinum palette. | `tests/test_kvantum.py::TestGeneralColors` | none |
| Every core and special control section resolves to the grounded frame margin. | `tests/test_kvantum.py::TestFrameMargins` | none |
| The SVG ships each frame element's centre and eight slices. | `tests/test_kvantum.py::TestSvg` | none |

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
