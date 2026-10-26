# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-eight widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
`PLACEHOLDERS.md` records no remaining placeholders); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme.py::TestFirefoxChrome` checks stylesheet declarations;
those checks do not establish rendered Firefox pixels. Keep this distinction when assessing
progress toward pixel-perfect application chrome. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces and their status are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style pointer set (black-face, white-outline arrow,
text I-beam, pointing hand, busy hourglass, move cross, horizontal and vertical resize arrows,
NW-SE and NE-SW diagonal resize arrows, crosshair, circle-slash, drag-and-drop copy plus,
open and closed hands, the help question-mark arrow, the progress arrow with a small hourglass,
a pencil, the `zoom-in`/`zoom-out` magnifiers, and the drag-and-drop/forbidden aliases, not
traced from Apple's artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both are being implemented in series.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed, and part 3/4 has landed as three entries — the opt-in install (parts 1/3 and 2/3) and
the selection (part 3/3) — while part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) has landed and part 2/2 (the profile install plus the
preference) has landed. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed and selected by the global theme); part 2/3
(a Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) has landed for the Lato
body face only, because Lato is the only family the package installs. KDE, Plasma and Qt
applications now use Lato for the general, menu, toolbar, smallest-readable and window-title
fonts, and monospaced text keeps the user's fixed font; GTK and Firefox
applications keep their own chrome unless the opt-in GTK targets or the Firefox userChrome
install are used (the GTK entries have landed, and Firefox chrome is part 1/2, which has
landed, while its profile install is part 2/2, which has landed).

_None yet._

### Firefox Platinum chrome: paint the downloads panel rows like a Platinum list (planned 2026-10-26 by the plan role; independent of the waiting all-tabs panel rows paint)

**Goal.** Give the downloads panel's rows Mac OS 8.6 list behaviour: a hovered non-selected row keeps the `#DDDDDD` panel face with black text and no violet hover wash, the selected row takes the flat `#CCCCFF` selection fill with black text, and every row in the panel is square. Scope the change to `#downloadsPanel #downloadsListBox > richlistitem`: Firefox's content-area downloads view (`chrome/browser/content/browser/downloads/contentAreaDownloadsView.xhtml`) names its own `#downloadsListBox`, and its rows stay Firefox's, as do the row's `.downloadButton` action button, the `#downloadsHistory` footer button and the `.downloadMainArea`'s own paint.

**Grounding.** No reference screenshot shows Firefox chrome or its downloads panel. The row behaviour adapts the reference-grounded `widgets/listitem.svg`, whose comment records that Mac OS 8.6 has no hover highlight and whose `pressed` (selected) row is a flat `#CCCCFF` rectangle with square corners, no bevel and no outline; `tests/test_desktoptheme_listitem.py::TestListItem` pins that art and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` pins the `#CCCCFF` sample. The GTK sheets make the same adaptation (transparent hover, flat `#CCCCFF` black-text selection, square corners) for tree, list and column rows (`docs/invariants.md`, `## gtk`), and this sheet already paints menu items, bookmark items and address-bar result rows `#CCCCFF`. Record the missing Firefox downloads reference and the dated adaptation (2026-10-26).

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<panel id="downloadsPanel" type="arrow">`, whose `<panelview id="downloadsPanel-mainView">` holds `<richlistbox id="downloadsListBox">` with the footer's `#downloadsHistory` button below it; `moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs`'s `connect()` builds each row as a `richlistitem` containing an `hbox.downloadMainArea` (with `.downloadTypeIcon`, `.downloadContainer`, `.downloadTarget` and the detail descriptions) plus a `button.downloadButton`, and `chrome/browser/content/browser/downloads/downloads.js` selects rows through `richListBox.selectedIndex`. `browser/omni.ja` `chrome/browser/skin/classic/browser/downloads/downloads.inc.css` gives `#downloadsListBox > richlistitem` `border-radius: var(--border-radius-small)` and paints its hover states (`.hoveringMainArea:hover`, `.openWhenFinished:hover`, `[verdict]:hover`) with `--button-background-color-ghost-hover` and `--button-text-color-ghost-hover`; toolkit `chrome/toolkit/skin/classic/global/richlistbox.css` paints `richlistitem[selected="true"]` with `-moz-cellhighlight` (and `SelectedItem` when the list is focused); `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` maps `--button-background-color-ghost-hover` to `--button-background-color-hover`, `light-dark(var(--color-violet-desaturated-20), var(--color-violet-desaturated-50))`, and `--border-radius-small` to 4px. The sheet's `panel[type="arrow"]` rule already sets the panel face `#DDDDDD`, and nothing in the sheet targets these rows, so today a hovered row shows the violet wash instead of the panel face.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `#statuspanel-label` rule and before the `panel[type="arrow"]` rule, add three rules with a short comment: `#downloadsPanel #downloadsListBox > richlistitem { border-radius: 0 !important; }`; `#downloadsPanel #downloadsListBox > richlistitem:not([selected]):hover { background-color: #DDDDDD !important; color: #000000 !important; }`; and `#downloadsPanel #downloadsListBox > richlistitem[selected] { background-color: #CCCCFF !important; color: #000000 !important; }`. The selected rule comes after the hover rule and the hover selector excludes `[selected]`, so a hovered selected row keeps `#CCCCFF`. `#DDDDDD` is the panel face `panel[type="arrow"]` already sets, so a hovered row paints the same face rather than a wash, and the `#downloadsPanel` ancestor keeps the change off the content-area `#downloadsListBox`. Add no declaration for `.downloadButton`, `#downloadsHistory`, `.downloadMainArea`, margin, padding, border, font or box-shadow: those controls keep Firefox's paint and geometry. In the header, insert a provenance paragraph between the sidebar paragraph (ending "the sidebar's inner document is not userChrome territory.") and the install-instructions paragraph (starting "Install it opt-in"): no reference shows Firefox's downloads panel; the row face, black text and flat selection adapt `widgets/listitem.svg`, pinned by `tests/test_desktoptheme_listitem.py::TestListItem`, and the GTK row mapping (platform colour adaptation 2026-10-26); Firefox's `chrome/browser/skin/classic/browser/downloads/downloads.inc.css` gives the rows their radius through `--border-radius-small` and paints `--button-background-color-ghost-hover` on hover, `chrome/toolkit/skin/classic/global/richlistbox.css` paints `richlistitem[selected="true"]`, `chrome/browser/content/browser/browser.xhtml` defines the panel and `moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs` builds each row, and Firefox's own violet ghost hover and the toolkit's system-colour selection are suppressed on these panel rows only; declaration checks do not establish rendered pixels.
- `tests/test_firefox_theme.py`: add the three selectors to `REQUIRED_RULES` after the `#sidebar-header` entry and before the `.tab-background` entry, with the declarations above (`FACE`, `BLACK` and `SELECTION` from `support.platinum_palette`). Add `TestFirefoxChrome.test_downloads_panel_row_paint_is_scoped_to_the_panel_list`: it asserts the selectors naming `downloadsListBox` are exactly those three, each starts with `#downloadsPanel #downloadsListBox > richlistitem`, each equals its `REQUIRED_RULES` entry, the hover selector carries `:not([selected])` and `:hover`, and the selected rule follows the hover rule in `self.selectors` order. Extend `test_header_names_provenance_and_preference` between the `"modules/ThemeVariableMap.sys.mjs"` entry and the `"the sidebar's inner document is not userChrome territory"` entry with the new provenance strings: `"No reference shows Firefox's downloads panel"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"chrome/browser/skin/classic/browser/downloads/downloads.inc.css"`, `"chrome/toolkit/skin/classic/global/richlistbox.css"`, `"chrome/browser/content/browser/browser.xhtml"`, `"moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs"`, `"--button-background-color-ghost-hover"`, `"richlistitem[selected=\"true\"]"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md`: add a row to the `## firefox` table between the menu-bar title-box row and the sidebar-frame row whose guarantee is: the downloads panel's rows (`#downloadsPanel #downloadsListBox > richlistitem`) are square; a hovered non-selected row keeps the `#DDDDDD` panel face with black text instead of Firefox's violet ghost wash; the selected row is flat `#CCCCFF` with black text; the row's action button, footer button and the content-area downloads list stay Firefox's. Its test column names the new test, and its provenance records the missing Firefox-downloads reference, the `widgets/listitem.svg` and GTK row adaptation, the installed Firefox ESR 153.5.1 files, selectors and tokens above, and that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- Required-rule validation fails when the radius, hover or selected rule is missing, carries a different colour, or loses its `!important`; the scope test fails when a `downloadsListBox` rule sits outside `#downloadsPanel #downloadsListBox > richlistitem`, when the hover selector loses `:not([selected])` or `:hover`, or when the selected rule precedes the hover rule.
- The `#statuspanel-label`, `panel[type="arrow"]`, tab, toolbar, menu-bar, menu, bookmark, urlbar, find bar, search field, sidebar, tooltip and other existing rules keep their current declarations, so their surfaces keep their current paints; the downloads row's action and footer buttons and the content-area downloads list keep Firefox's paint; no `.downloadButton` or `#downloadsHistory` rule is added.
- A hovered non-selected panel row paints the `#DDDDDD` panel face with black text; the selected panel row paints flat `#CCCCFF` with black text; every panel row is square. The content-area downloads list is unchanged.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Split the render scratch session out of the render CLI (planned 2026-10-26 by the organize role)

**Goal.** Give `tools/render_surface.py` one job -- parse the CLI, run the capture and publish the PNG -- and move the throwaway session it prepares (scratch root, sanitized environment, theme install, session config and in-session command) into a new `tools/render_session.py`. `make render`, its options, exit statuses, diagnostics, scratch cleanup and rendered bytes stay unchanged.

**Cost today.** `tools/render_surface.py` is the second-largest production Python module at 329 lines, and its 127-line `_render` mixes two layers: it creates the scratch XDG root and its environment, runs `make install`, writes `kwinrc`/`plasmarc`, builds the `dbus-run-session`/`kwin_wayland` command, then reads and publishes the PNG. A reader changing the capture has to read through the session setup, and `tests/test_render_surface.py` patches `render_surface.run_logged` and `render_surface.write_configs` to exercise session preparation that has no module of its own. The CLI's unit tests reach into session internals (`_session_script`, `COLOR_SCHEME`) from `render_surface`.

**Target structure.** New `tools/render_session.py` owns the throwaway session:
- move `COLOR_SCHEME`, `SOCKET`, `INSTALL_TIMEOUT` and `CONFIG_FILES` out of `render_surface`;
- move `_session_script` as `session_script()`, returning the same shell text;
- a `Session` value or context manager that creates the `rt/`, `cfg/` and `data/` directories, makes `rt/` mode `0700`, names `surface.png`, and builds the environment that drops `WAYLAND_DISPLAY`, `DISPLAY`, `DESTDIR`, `MAKEFLAGS` and `XDG_CONFIG_DIRS` and sets `XDG_RUNTIME_DIR`, `XDG_CONFIG_HOME` and `XDG_DATA_HOME`; its cleanup replaces the `_render` `finally` that removes the scratch root;
- `install_theme(session)` running `make install XDG_DATA_HOME=...` through `run_logged` and returning the status and install-log path, and `write_session_configs(session)` calling `theme_defaults.write_configs(session.config, CONFIG_FILES)`;
- `session_command(session, applet, settle, width, height, timeout)` returning the `dbus-run-session -- kwin_wayland ... sh -c <script> ...` argv and render-log path.

`tools/render_surface.py` keeps `TOOL`, `REQUIRED_TOOLS`, the argument types, `main` and `_render`; `_render` becomes create session, install, configure, launch, read the capture, check its size and publish, with every diagnostic still reported under `TOOL`. Keep the CLI at `tools/render_surface.py`: README.md, the Makefile and `docs/invariants.md` name that path as the entry point.

**Files touched.** `tools/render_surface.py`, new `tools/render_session.py`, `tests/test_render_surface.py`, `tests/test_render_surface_units.py`. `docs/invariants.md` keeps its rows and test names unless the render-session tests move to a new module, in which case update the affected rows in the same change.

**Acceptance criteria.**
- `tools/render_session.py` imports no `render_surface`; `render_surface._render` no longer creates scratch directories, builds the session environment, calls `make install`/`write_configs`, or builds the `dbus-run-session` argv; grep finds no `_session_script`, `COLOR_SCHEME`, `SOCKET`, `INSTALL_TIMEOUT` or `CONFIG_FILES` left in `render_surface`.
- The session script text, scratch layout and modes, environment, install/config order, session argv, exit codes, diagnostic text and cleanup on success and failure are the same before and after; no external dependency or CLI option changes.
- The session-script and environment tests import the moved names from `render_session`, and the install/config/session failure tests patch `render_session.run_logged` or `render_session.write_configs`; CLI, argument and output-publication tests stay on `render_surface`.
- `make check` passes, and a grep over the sources, tests and markdown docs finds no stale reference to a moved name or path outside the archives.

## Done
