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
| The Aurorae package's `metadata.json` / `metadata.desktop` pair is what KPackage and KWin's Aurorae discovery read, `make install` copies the package byte for byte, and `make uninstall` removes it. | `tests/test_aurorae_package.py` | none |
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
| `widgets/lineedit.svg`'s corner tiles reproduce the reference field's outline and top-right notch, including the bottom outline row and the face-coloured outer corner. | `tests/test_desktoptheme_lineedit.py::TestLineEditReference::test_corners_match_the_reference` | none |
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

## fonts

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The shipped Lato Regular and Bold faces name the `Lato` family, and the fonts, licence and provenance record carry the pinned source digests; the licence is the Debian copyright file byte for byte, including its missing final newline. | `tests/test_fonts.py::TestFontFiles` | Lato is this theme's substitute for Charcoal, not a face sampled from a reference screenshot; no Mac OS 8.6 reference in the set supplies a font pixel. |
| `make install` copies the font package into `$XDG_DATA_HOME/fonts/org.macos8.desktop` byte for byte, a repeat install succeeds, and `make uninstall` removes it and its staging/old leftovers while leaving a sibling font family in place. | `tests/test_fonts.py::TestFontsInstall` | none |
| The global theme selects the installed Lato family for the general, menu, toolbar, smallest-readable and window-title fonts. | `tests/test_lookandfeel.py::TestDefaults` | Lato is a Charcoal substitute, the point sizes are KDE defaults, and monospace keeps the user's fixed font. |

## firefox

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The standalone `userChrome.css` paints the Platinum palette on Firefox's tab strip, navigation bar, toolbars, menus and status panel with no at-rule and no import. | `tests/test_firefox_theme.py::TestFirefoxChrome` | No reference screenshot shows Firefox chrome, so the palette comes from the pinned Platinum values and the geometry is this theme's adaptation of the Platinum controls. |
| The opt-in install copies the sheet byte-for-byte, adds only the marker-delimited preference while preserving foreign `user.js` lines and endings, refuses a foreign `userChrome.css`, and removal reverses only those two changes. | `tests/test_firefox_install.py::TestInstall`, `tests/test_firefox_install.py::TestRemove` | No reference screenshot shows Firefox chrome; the profile layout and preference name are Firefox-required. |

## gtk

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The standalone GTK 3 Platinum theme redefines the Platinum palette and paints the scoped Platinum control rules, including every plain and reorderable tab state, without importing Adwaita. | `tests/test_gtk_theme.py::TestGtkTheme` | No reference screenshot shows a GTK widget, so the palette comes from the pinned Platinum values and the geometry is this theme's adaptation. |
| The standalone GTK 4 stylesheet redefines the Platinum palette and opaque GTK 4 surface colours and paints the scoped Platinum control rules, including every tab state, without importing another stylesheet. | `tests/test_gtk4_theme.py::TestGtk4Theme` | No reference screenshot shows a GTK widget, so the palette comes from the pinned Platinum values and the geometry is this theme's adaptation. |
| The GTK 3 suite reads the theme's `index.theme` and its `gtk.css`, and the GTK 4 suite reads its `gtk.css`, through the shared containment reader, so a checked-in symlink that escapes the repository is refused instead of leaking a private file's text into a failing test's diagnostic. | `tests/test_gtk_theme.py::TestGtkTheme::test_theme_read_refuses_a_symlink_escape` | none |
| The shared GTK stylesheet parser removes comments and pairs rule blocks without the quadratic backtracking of the regular expressions it replaced, so a contributor-supplied `gtk.css` with many unterminated comment starts or a long unbraced run cannot stall the suite. | `tests/test_gtk_css.py::TestHostileStylesheet` | none |
| The opt-in GTK install copies the three GTK theme files byte-for-byte, is repeatable, leaves previous files intact on a failed install, and writes no GTK files by default; `make uninstall` removes only the three files, their `.staging` siblings and the emptied `gtk-3.0`/`gtk-4.0` directories, leaving `Kvantum/` and the theme directory itself. | `tests/test_gtk_install.py::TestInstall`, `tests/test_gtk_install.py::TestUninstall` | No reference screenshot shows a GTK widget; the directory layout is GTK-required. |
| The opt-in GTK selection in `[Settings]` of both GTK settings files and the marker `gtk-4.0/gtk.css` that imports the installed GTK 4 sheet preserve every foreign line and file; a missing installed sheet is refused, and `make remove-gtk` removes only our `gtk-theme-name` lines and marker. Removal needs only the config home, so an unresolvable data home does not block clearing the selection. | `tests/test_gtk_apply.py` | No reference screenshot shows a GTK widget; the settings keys, the config path and the libadwaita user-CSS path are GTK-required. |
| `tools/gtk_settings.py` edits only the `gtk-theme-name` line and keeps every other line's own ending, so a CRLF, lone-CR or mixed-ending `settings.ini` keeps its line endings through `apply_gtk` and `remove-gtk`; the exceptions are that inserting after an unterminated header or appending a section must terminate that line first, and a file without a final line ending still has none after removal. | `tests/test_gtk_settings.py::TestLineEndings`, `tests/test_gtk_apply.py::TestLineEndings` | none |
| A GTK settings or user-CSS file that cannot be read or written is reported as one `apply_gtk: error:` line naming the path with exit status 2 instead of a traceback escaping `main`; every settings and user-CSS file is read and every write is staged before any is committed, so a file that cannot be read or staged leaves all of them unchanged, while a rename that fails during the commit step is reported by name and is not rolled back after earlier renames; a failed user-CSS removal leaves the settings unchanged; a FIFO at a settings or user-CSS path is refused by name as not a regular file before anything is written or removed rather than being read or replaced, checking the opened descriptor so a regular file swapped for a FIFO before the open cannot block the read. | `tests/test_gtk_apply.py::TestSettingsErrors`, `tests/test_gtk_apply.py::TestUnreadableConfig`, `tests/test_gtk_staging.py::TestCommit` | none |

## icons

| Guarantee | Test | Provenance exception |
| --- | --- | --- |
| The icon theme names our own final Platinum art, ships exactly the tracked icons, and declares each icon's size directory. | `tests/test_icon_theme.py::TestIndex` | The art is our own drawing, not Apple's; the reference set has no pixel ground truth for it. |
| Every shipped icon draws its pinned drawing elements in document order, and the `inode-directory` alias shares the folder art. | `tests/test_icon_theme.py::TestIconGeometry` | The art is our own drawing, not Apple's; the reference set has no pixel ground truth for it. |
| The icon theme's `cursors/` ships `left_ptr`, `xterm`, `hand2`, `watch` and `fleur`, each drawing its own black-face, white-outline Platinum art at nominal sizes 16/24/32 with its pinned hotspot, and every X-name alias (`arrow`, `default`, `top_left_arrow`, `text`, `ibeam`, `hand1`, `pointer`, `pointing_hand`, `wait`, `move`, `all-scroll`, `size_all`) is byte-identical to its canonical file. | `tests/test_cursors_theme.py::TestCursorArtifact`, `tests/test_cursors_theme.py::TestCursorSet` | No reference screenshot shows the mouse pointer, so the pointer set is our own Platinum-style art on the pinned #000000 face and #FFFFFF outline; the nominal sizes, Xcursor binary layout, canonical names and X-name aliases are KDE/X-required values. |
| The opt-in cursor selection exposes the installed icon theme at `$HOME/.icons/org.macos8.desktop` and selects it with `plasma-apply-cursortheme org.macos8.desktop`; a missing installed theme, `index.theme` or `cursors/left_ptr` is refused, a foreign path is left untouched, and removal unlinks only our symlink (including a dangling one), leaving `~/.icons` and `kcminputrc` in place. | `tests/test_apply_cursor.py::TestInstall`, `tests/test_apply_cursor.py::TestRemove`, `tests/test_apply_cursor.py::TestSelection` | No reference screenshot shows the mouse pointer, so no pixel is sampled; the `~/.icons` path, the `org.macos8.desktop` theme name and the `plasma-apply-cursortheme` selector are Xcursor/KDE-required values. |
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
| The global theme's `contents/defaults` selects the color scheme, desktop theme, icon theme, window decoration, wallpaper, Kvantum widget style and the `Lato` font family. | `tests/test_lookandfeel.py::TestDefaults` | Lato is a Charcoal substitute and the point sizes are KDE defaults; monospace keeps the user's fixed font. |
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
| The installed-template copy shared by `installed_destdir` and `FailedInstallPreservesPackage._install_ok` refuses a symlink that resolves outside the template before writing anything into the copy destination, and preserves an inner symlink as a link, so a package symlink cannot copy a private file's bytes into a test's DESTDIR. | `tests/test_theme_install.py::TestInstalledDestdirSharing::test_an_escaping_template_symlink_is_refused`, `tests/test_theme_install.py::TestInstalledDestdirSharing::test_a_contained_template_symlink_is_copied_as_a_link`, `tests/test_theme_install.py::TestFailedInstallSharing::test_install_ok_refuses_an_escaping_template_symlink` | none |
| Every provenance citation is a well-formed absolute RFC 3986 URI: the scheme, authority, path, query and fragment each hold to the RFC's grammar, including case-insensitive IPvFuture, no IPv6 zone identifier, and a valid userinfo, bracketed host and port. | `tests/test_url_check.py` | none |
| The render session resolves configuration only from its scratch data and config homes and the system defaults, never the caller's `XDG_CONFIG_DIRS`, so an ambient KDE configuration cannot change the rendered surface. | `tests/test_render_surface.py::TestFailurePaths::test_session_ignores_a_config_search_path_from_the_environment` | none |
| No contributor-file reader reimplements the containment guard; each routes through the shared `tools.containment` module. | `tests/test_containment.py::TestGuardIsShared` | none |
| The reference-screenshot and shipped-wallpaper PNG readers refuse a checked-in symlink that resolves outside the repository before the image is decoded, including when a decode was already cached under that path. | `tests/test_reference_image.py::TestReadReferenceContainment`, `tests/test_wallpaper.py::TestImageReadContainment` | none |
| The wallpaper generator refuses a reference screenshot that resolves outside the repository before it is decoded, so a checked-in symlink cannot copy a private file's pixels into the wallpaper package. | `tests/test_make_wallpaper.py::TestReferenceContainment::test_a_reference_symlinked_outside_the_repository_is_refused` | none |
| The wallpaper generator refuses an images directory that resolves outside the repository (a checked-in symlink) before it writes, so the generated images stay inside the wallpaper package and cannot overwrite same-named files in a directory outside it. | `tests/test_make_wallpaper.py::TestOutputContainment::test_an_images_directory_symlinked_outside_the_repository_is_refused` | none |
| The invariant register's referenced test-module reader reads through the shared containment reader, so an oversize module is refused by name instead of being loaded whole. | `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_an_oversize_module_instead_of_loading_it_whole` | none |
| The lexical containment boundary accepts the root itself and every path below it, including a filesystem root and a POSIX double-leading-slash spelling of the same directory, while rejecting a sibling directory that shares the root's prefix. | `tests/test_containment.py::TestIsWithin` | none |
| The shared containment guard's refusal names the operation the escape would have reached: a read by default, and the write a caller was about to perform when it passes one. | `tests/test_containment.py::TestRefusalNamesTheOperation` | none |
| The three KDE INI readers (`support.kde_config.read`, `theme_defaults.defaults_groups` and the `uninstall` recipe's `awk`) agree on one shared corpus's `[General] ColorScheme` selection: `=` is the only key/value delimiter (a colon-delimited line is ignored), each line is trimmed, section and key names are case-sensitive, the last duplicate key wins, a leading UTF-8 BOM is stripped, a present but empty value is distinct from a missing key, and a group header with no closing `]` is ignored (the open section continues). An empty `[]` header starts its own group, so the following key does not join the previous section, and `support.kde_config.read` keeps a key before the first heading in KDE's `<default>` root group instead of treating it as invalid. `defaults_groups` instead refuses a malformed heading because its headings name output files. | `tests/test_kde_ini_parity.py::TestReadersAgree` | none |
| The shared contributor-file readers refuse a FIFO or device by name, checking the opened descriptor so a path swapped for a FIFO cannot block the read. | `tests/test_containment.py` | none |
| The KDE INI test reader reads through the shared containment reader, so a FIFO at a theme INI or `contents/defaults` is refused instead of blocking. | `tests/test_kde_config.py::TestReadKdeConfig::test_refuses_a_fifo_instead_of_blocking` | none |
| The global theme's `contents/defaults` reader refuses a FIFO or device by name instead of blocking on open. | `tests/test_theme_defaults.py::TestDefaultsGroups` | none |
| The render's `write_configs` validates every config name before writing: it refuses a bare `str`/`bytes` sequence, a non-`str` name, and a name that is not a bare filename (empty, `.`, `..`, a path separator or a NUL byte), so no file is written inside or outside the config home when a name is refused. | `tests/test_theme_defaults.py::TestWriteConfigs` | none |
| The package-metadata test reader reads through the shared containment reader, so a `metadata.json` FIFO is refused instead of blocking and an oversize one is refused instead of being loaded whole. | `tests/test_package_metadata.py::TestLoadMetadata` | none |
| The splash QML test reader reads through the shared containment reader, so a FIFO at its path is refused instead of blocking and an oversize file is refused instead of being loaded whole. | `tests/test_splash_qml.py::TestSplashQmlContainment` | none |
| The placeholder marker and register readers read through the shared containment reader, so a FIFO at a theme asset or the register is refused instead of blocking and an oversize one is refused instead of being loaded whole. | `tests/test_placeholders.py::TestHelpers` | none |
| The README theme-file reader reads through the shared containment reader, so a FIFO at `README.md` is refused instead of blocking and an oversize one is refused instead of being loaded whole. | `tests/test_readme_theme_files.py::TestReadmeTextContainment::test_refuses_a_fifo_instead_of_blocking` | none |
| The desktop-theme provenance header reader reads through the shared containment reader, so a FIFO at an SVG path is refused instead of blocking and an oversize one is refused instead of being loaded whole. | `tests/test_desktoptheme_provenance.py::TestHeaderCommentContainment::test_refuses_a_fifo_instead_of_blocking` | none |
| The Aurorae decoration test reader refuses a FIFO or device by name instead of blocking the read: `decoration.svg` is parsed through the shared SVG guard (`SvgCase.setUp`), and `decoration.svgz` is decompressed through the shared containment guard. | `tests/test_aurorae_frame.py::TestReadCappedContainment::test_refuses_a_fifo_instead_of_blocking` | none |
| The external-command supervisor's timeout bounds the whole run: after killing a command's process group, the reap wait is bounded too, so a child the kernel has not released yet does not stall the caller, and a reap timeout never replaces the timeout result or an in-flight `SystemExit`/`KeyboardInterrupt` from the first wait. | `tests/test_process_group.py::TestRunLogged` | none |
| Every archived `no-observability` or `unclear-invariant` validation gap maps to a test-side reproduction that confirms its failure offline (and, for `unclear-invariant`, the register row that states the guarantee), and each tag's record count does not exceed its baseline, so a new unrecorded gap fails the suite instead of growing the gap. | `tests/test_validation_gaps.py::TestNoObservabilityLedger`, `tests/test_validation_gaps.py::TestUnclearInvariantLedger` | none |
| The suite's process-group cleanup bounds its reap wait too: a child the kernel has not released cannot stall `make check` from the cleanup path, and a reap timeout is reported on stderr instead of replacing the exception the block was unwinding. | `tests/test_process_runner.py::TestSubprocessTimeout::test_running_bounds_the_reap_of_a_child_the_kernel_does_not_release` | none |
| Every test module carries the `unittest.main()` entry-point guard as its last statement, so a module run directly runs its own tests instead of exiting 0 silently. | `tests/test_entry_point_guards.py::TestEntryPointGuard` | none |
| The child the FIFO guards run writes the parent's own pending output once, from the parent: the parent flushes it before the fork, so the child's copy of the buffer is empty and the bytes are not written twice. | `tests/test_snippet_child.py::TestParentsOutput::test_the_parents_pending_output_is_written_once` | none |
| The FIFO guard's child is never signalled once it has been reaped, and the reap that follows the guard's kill is bounded, so a child the kernel does not release cannot stall `make check` from the cleanup path. | `tests/test_snippet_child.py::TestTimeoutPath::test_a_child_that_has_exited_is_not_signalled`, `tests/test_snippet_child.py::TestTimeoutPath::test_the_reap_after_the_kill_is_bounded` | none |
| The reference-set checker refuses a reference directory that resolves outside the repository (a checked-in symlink) before it lists or reads anything inside it, so the directory cannot become the containment base for paths outside the repository. | `tests/test_check_references_io.py::TestSymlinkEscape::test_reference_directory_symlink_outside_repository_is_not_read` | none |
| The checker-mutation scratch copy refuses a `tests/` tree that resolves outside the repository before copying it, copies an inner symlink as a link instead of dereferencing it, and refuses a scratch write whose symlinks resolve outside the scratch root, so a private file's bytes never enter the scratch tree and a mutation never writes through a preserved link. | `tests/test_checker_mutations.py::TestCheckerMutations::test_tests_tree_symlink_outside_the_repository_is_refused`, `tests/test_checker_mutations.py::TestCheckerMutations::test_an_inner_tests_symlink_is_preserved_not_dereferenced` | none |
| The RGBA PNG codec round-trips alpha byte for byte, applies a palette, greyscale or truecolor `tRNS` chunk to the decoded alpha byte, and leaves `encode_png`'s output unchanged. | `tests/test_png_rgba.py` | none |
| A PNG chunk stream carrying a second IHDR, PLTE or tRNS chunk is refused by name instead of letting the later chunk silently redefine the image. | `tests/test_png_chunks.py::TestChunkFraming` | none |
| A PNG chunk stream whose IDAT chunks are not consecutive, or whose PLTE or tRNS chunk follows the image data, is refused by name rather than decoded as if its chunk order were valid. | `tests/test_png_chunks.py::TestChunkFraming` | none |
| A PNG chunk stream carrying a complete chunk, or a shorter trailing fragment that cannot form one, after IEND is refused by name instead of decoded while silently dropping those bytes, because IEND must be the last chunk. | `tests/test_png_chunks.py::TestChunkFraming` | none |
| A PNG chunk stream whose IEND chunk carries a payload is refused by name instead of its non-empty data field being silently dropped, because IEND's data field must be empty. | `tests/test_png_chunks.py::TestChunkFraming` | none |
| A PNG's `tRNS` chunk is refused unless the header's color type and palette can carry it — never for the alpha color types 4 and 6, only at its exact length for the greyscale and truecolor sample types, and only for 1 to the palette's entry count for color type 3 — on both the RGB and RGBA decode paths. | `tests/test_png_malformed.py::TestTrnsColorTypeValidation` | none |
| A PNG's `tRNS` chunk that precedes a `PLTE` chunk which is present is refused on both decode paths for every color type — the palette image's required palette and a truecolor image's suggested palette alike — while a color type 3 image with no `PLTE` at all keeps its missing-palette diagnosis. | `tests/test_png_malformed.py::TestTrnsColorTypeValidation` | none |
| A PNG's `PLTE` chunk is refused for the greyscale color types 0 and 4, where the PNG spec prohibits it, while a suggested palette on the truecolor color types 2 and 6 and the required palette on color type 3 still decode, on both the RGB and RGBA decode paths. | `tests/test_png_malformed.py::TestPlteColorTypeValidation` | none |
| The PNG decoder refuses bytes after the end of the IDAT zlib stream instead of silently dropping them, so the concatenated IDAT payload holds exactly one zlib stream. | `tests/test_png_malformed.py::TestMalformedImageData::test_rejects_trailing_bytes_after_the_zlib_stream` | none |
