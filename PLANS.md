# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-19 by the clean role):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's; `PLACEHOLDERS.md` is empty);
and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-20 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); and **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them). The shipped work should not be treated
as the whole of the prompt.

Two answers on 2026-10-19 expand the scope again, and neither has a plan yet.
**GTK applications and Firefox** are now in scope (QUESTIONS.md, answered 2026-10-19): a
KDE/Qt global theme cannot reach them, so this needs a GTK 4 CSS theme and a Firefox
`userChrome.css` plus profile preference, installed by separate opt-in `make` targets — a
multi-part series of its own. **The UI font** is now to be vendored (QUESTIONS.md, answered
2026-10-19): the theme should ship a Chicago/Charcoal-style font with a checked redistribution
licence and recorded provenance, select it for KDE, Plasma and Qt applications, and the answer
leaves open whether one face serves both Chicago and Charcoal. The plan queue carries neither
surface yet; until it does, the menu bar and dialog text keep the user's desktop font, and GTK
and Firefox applications keep their own chrome.

### Ship a GTK 3 Platinum theme for GTK applications (planned 2026-10-21 by the plan role; part 1/4)

**Goal.** No GTK theme exists in the repository (no `theme/gtk` directory), so GTK 3
applications -- including Firefox's GTK chrome -- keep the desktop's Breeze GTK theme. Ship a
user-installable `org.macos8.desktop` GTK 3 theme whose windows, header bars, buttons, entries,
notebook tabs, menus, scroll bars and toolbars paint the Platinum palette and square bevels.
This is part 1/4 of the GTK and Firefox application-chrome series; it ships the artwork only.
Part 2/4 will ship the GTK 4/libadwaita CSS, part 3/4 installs and selects both, and part 4/4
adds the opt-in Firefox chrome. Those sibling plans are not in this queue yet and will be added
as separate entries.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget. Take every
colour from the already reference-grounded Platinum palette in
`tests/support/platinum_palette.py`: `FACE` `#DDDDDD`, `WHITE`, `GREY` `#999999`, `BLACK`,
`BUTTON_SHADOW` `#AAAAAA` (the raised push button's shadow), `TROUGH` `#EEEEEE` and `SELECTION`
`#CCCCFF`. The `#888888` etched-separator dark half is the value
`tests/test_desktoptheme_line.py` pins to the reference. Record in the CSS header and in
`docs/invariants.md` that the palette is reference-grounded while the GTK-specific geometry is
this theme's adaptation; do not claim a GTK reference crop.

**Approach.**
- `theme/gtk/org.macos8.desktop/index.theme`: `[Desktop Entry]` with `Type=X-GNOME-Metatheme`,
  `Name=Mac OS 8.6 Platinum`, `Encoding=UTF-8` and a short `Comment=`, plus an
  `[X-GNOME-Metatheme]` group naming the same theme.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: write a standalone sheet -- **do not**
  `@import` Adwaita. The rejected implementation imported Adwaita and then tried to out-specify
  its reorderable-tab rules; a standalone theme has no imported sheet whose
  `.reorderable-page` selectors can win, so the tab face cannot fall back to Adwaita's
  translucent or transparent fills. Define the theme colours with
  `@define-color theme_bg_color #DDDDDD;`, `theme_fg_color #000000`,
  `theme_base_color #FFFFFF`, `theme_text_color #000000`, `theme_selected_bg_color #CCCCFF`,
  `theme_selected_fg_color #000000`, `borders #000000` and `unfocused_borders #999999`.
  Write exactly these scoped rules (no `*` selector):
  - `window, .background`: `#DDDDDD` background, `#000000` text.
  - `headerbar, .titlebar`: `#DDDDDD` face, no background image, `1px solid #000000` border,
    `border-radius: 0`, no box shadow; `headerbar` keeps only its 1px black bottom rule.
  - `button`: `#DDDDDD` face, no background image, `1px solid #000000` border,
    `border-radius: 0`, `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`;
    `button:hover` keeps the same face; `button:active, button:checked` inverts the bevel to
    `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF`.
  - `entry`: white face, `1px solid #000000` border, `border-radius: 0`, sunken
    `box-shadow: inset 1px 1px #999999`, black text.
  - `notebook > header`: `#DDDDDD` background, black border. Every tab state carries the
    raised `#DDDDDD` face with `1px solid #000000`, `border-radius: 0` and
    `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`; the checked states drop the
    bottom border to `#DDDDDD` and the bevel shadow. Cover both the plain and `.reorderable-page`
    forms in each state: base (`tab, tab.reorderable-page`), hover (`tab:hover,
    tab.reorderable-page:hover`), checked (`tab:checked, tab.reorderable-page:checked`),
    checked+hover (`tab:checked:hover, tab.reorderable-page:checked:hover`), backdrop
    (`tab:backdrop, tab.reorderable-page:backdrop`) and backdrop+checked
    (`tab:backdrop:checked, tab.reorderable-page:backdrop:checked`). The checked and backdrop
    states explicitly paint the face rather than leaving it to a default: the rejected diff left
    a non-hovered checked reorderable tab translucent and a backdrop one transparent.
  - `menu, .menu, popover, .popover`: `#DDDDDD` face, `1px solid #000000` border,
    `border-radius: 0`; `menuitem:hover, .menuitem:hover` paints `#CCCCFF`.
  - `scrollbar`: `#EEEEEE` trough with a `1px solid #000000` border; `scrollbar slider` is the
    raised `#DDDDDD` thumb with a `1px solid #000000` border, `border-radius: 0` and
    `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`.
  - `toolbar, menubar`: `#DDDDDD` face with the reference's etched rule,
    `border-bottom: 1px solid #888888` and `box-shadow: inset 0 -1px #FFFFFF`.
- `tests/test_gtk_theme.py` (new): `TestGtkTheme` reads the two files as text. Pin the
  `index.theme` keys above; pin every `@define-color` name/value, and every selector/property
  above (a parser over brace blocks or explicit substring checks is fine). Assert the CSS
  contains no `@import` and no `Adwaita` text, so a future edit cannot reintroduce the imported
  rules that outranked the tabs. Assert the six tab-state selector groups above each exist with
  the raised face and bevel, and that each checked group also drops the bottom border and bevel,
  so neither a missing state nor a translucent/transparent fallback passes. Assert
  the only six-digit hex literals in the CSS are exactly
  `{BLACK, WHITE, GREY, FACE, BUTTON_SHADOW, TROUGH, SELECTION, ETCH_DARK}`, importing the
  palette constants from `support.platinum_palette` and defining `ETCH_DARK = "#888888"` beside
  the existing line-test value, so a stray Breeze colour fails. Assert the rules for
  `headerbar, .titlebar`, `button`, `entry`, `notebook > header > tabs > tab`,
  `menu, .menu, popover, .popover` and `scrollbar slider` each carry `border-radius: 0`, and
  that no rule uses the universal `*` selector.
- `docs/invariants.md`: add a `## gtk` section (a `theme/gtk` subsystem needs its own section;
  do not fold this into `tooling`) with one row: "The standalone GTK 3 Platinum theme redefines
  the Platinum palette and paints the scoped Platinum control rules, including every plain and
  reorderable tab state, without importing Adwaita." pinned to
  `tests/test_gtk_theme.py::TestGtkTheme`, provenance exception: no reference screenshot shows a
  GTK widget, so the palette comes from the pinned Platinum values and the geometry is this
  theme's adaptation.

**Files touched.** `theme/gtk/org.macos8.desktop/index.theme` (new),
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (new), `tests/test_gtk_theme.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- The two new files exist under `theme/gtk/org.macos8.desktop/`; the CSS imports nothing,
  defines the eight theme colours with the values above, and carries every scoped control rule
  and all six plain/reorderable tab-state groups.
- `make check CHECK_TESTS=test_gtk_theme` passes, and adding an `@import`, removing any
  `@define-color`, any listed selector or tab-state group, a bevel shadow or the scoped
  `border-radius: 0` makes it fail.
- The parsed CSS hex set is exactly the eight pinned colours; no Breeze or other colour is
  introduced.
- `tests/invariants.py`'s cross-check accepts the new `## gtk` section and
  `tests/test_gtk_theme.py::TestGtkTheme`.
- No install target, GTK selection, `kdeglobals` write or Firefox change is added in this part;
  `make check` is green.

### Vendor the Lato body font and install it (planned 2026-10-21 by the plan role; part 1/3)

**Needs replan 2026-10-21 by feature: rejected after 5 review rounds**

> 1. (prior 2) The commit body still misdescribes the README change. At the measured base `015eaf1a`, the status line named only `BUGS-FIXED.md`; this diff edits it to add `PLANS-DONE.md`. Revision 5's RISK nevertheless says that line “already” names `PLANS-DONE.md` and that “no edit was needed,” and it…
> 2. The new `fonts` family was not fully documented. `tests/support/install_lifecycle_cases.py`'s module docstring still lists only the look-and-feel, desktop-theme, Aurorae, wallpaper and icon-theme suites, omitting the new font suite, and the `Makefile`'s uninstall comment still omits `fonts` from th…

**Goal.** QUESTIONS.md's font answer (2026-10-19) directs the theme to vendor a Chicago/Charcoal-style
font, but no `theme/fonts` directory exists and `make install` copies no font. Ship Lato Regular and
Bold (SIL OFL 1.1, already installed on this machine, so no network fetch) as the Charcoal-style
body face under a new `theme/fonts/org.macos8.desktop` artifact, installed to
`$XDG_DATA_HOME/fonts/org.macos8.desktop`, so a later selection part can name the `Lato` family.
This is part 1/3 of the UI-font series: it vendors and installs the body face only. Part 2/3 will
vendor a Chicago-style menu face once a redistribution licence is confirmed (the ChicagoFLF
provenance is still unresolved, so it is deliberately not shipped here); part 3/3 will select the
installed families in KDE/Plasma/Qt. Neither sibling is in the queue yet, and this part does not
depend on them.

**Reference grounding.** `aboutsystem_betawiki.png`'s dialog body draws Charcoal's narrower
humanist forms at 12px, but the theme ships no Apple font and samples no font pixel: Lato is this
theme's substitute for Charcoal, and `PROVENANCE.md` records it as an approximation rather than a
reference anchor. The two screenshot crops (the menu bar in `desktop_betawiki.png` and the
`System` dialog body in `aboutsystem_betawiki.png`) are recorded there as context for the later
Chicago/selection parts, not copied.

**Approach.**
- Add `theme/fonts/org.macos8.desktop/Lato-Regular.ttf` and `Lato-Bold.ttf`, copied byte for byte
  from `/usr/share/fonts/truetype/lato/`, plus `LICENSE-Lato.txt` copied from
  `/usr/share/doc/fonts-lato/copyright` (the full SIL OFL 1.1 text with the upstream copyright
  notice). `PROVENANCE.md` records the local source paths, the upstream source
  (`http://www.latofonts.com`, Debian package `fonts-lato`), both SHA-256 digests, the internal
  family name `Lato`, and why the face is an approximation of Charcoal.
- `Makefile`: add `FONT_ID := org.macos8.desktop`, `FONT_PACKAGE := theme/fonts/$(FONT_ID)` and
  `FONT_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/fonts`; add `fonts` to `INSTALL_FAMILIES` and to
  the default `INSTALL_PACKAGES`; in `_install` create `$(FONT_INSTALL_DIR)` and copy the package
  with the existing `install_package` swap; in `_uninstall` remove
  `$(FONT_INSTALL_DIR)/$(FONT_ID)` together with its `.staging` and `.old` siblings. Update the
  `help` line's default family list (the default is compared against the `?=` value by
  `tests/test_make_help.py`).
- `tests/support/installed_paths.py`: add `installed_fonts_dir(destdir)` returning
  `$DESTDIR/share/fonts` and `installed_font_package(destdir, package_id)` returning its
  `org.macos8.desktop` child, matching the Makefile paths.
- `tests/test_fonts.py` (new): `TestFontFiles` parses each TTF's sfnt `name` table (name ID 1) with
  `struct` and asserts the family is `Lato` and the subfamily is `Regular`/`Bold`; pins the SHA-256
  of both files and asserts `PROVENANCE.md` names both digests; asserts `LICENSE-Lato.txt` contains
  `SIL OPEN FONT LICENSE` and the OFL version. `TestFontsInstall` subclasses `InstallLifecycleCases`
  with `MAKE_PACKAGES = "fonts"`, `PACKAGE_DIR = "theme/fonts/org.macos8.desktop"`,
  `INSTALLED_FILES` naming the four files, and `installed_parent`/`installed_package_dir` overridden
  to the new helpers, so it gets the byte-for-byte, registry-coverage, repeat-install and
  uninstall-leftover checks once.
- `tests/test_theme_install.py`: include the font package in `TestWhitespaceInInstallPaths`'
  round trip and in `TestInstallPackages.test_one_family_installs_only_that_family`'s absent list
  (installing `color-scheme` must leave `fonts/` absent); update the "seven artifacts" docstrings
  to eight.
- `README.md`: change the Installing/Status/uninstall/apply "seven artifacts" counts to eight and
  describe the font package's path, its OFL licence and its approximation status; note that this
  part installs the family but does not select it, so the desktop font is unchanged until the
  selection part lands.
- `docs/invariants.md`: add a `## fonts` section (every `theme/` subsystem needs one) with a row for
  the shipped Lato family/digests pinned to `tests/test_fonts.py::TestFontFiles` and a row for the
  install/uninstall lifecycle pinned to `tests/test_fonts.py::TestFontsInstall`, with the provenance
  exception stating that Lato is a Charcoal substitute, not a sampled reference face.

**Files touched.** `theme/fonts/org.macos8.desktop/Lato-Regular.ttf` (new),
`theme/fonts/org.macos8.desktop/Lato-Bold.ttf` (new),
`theme/fonts/org.macos8.desktop/LICENSE-Lato.txt` (new),
`theme/fonts/org.macos8.desktop/PROVENANCE.md` (new), `Makefile`,
`tests/support/installed_paths.py`, `tests/test_fonts.py` (new), `tests/test_theme_install.py`,
`README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `make install INSTALL_PACKAGES=fonts DESTDIR=<tmp>` writes exactly the four files above under
  `$XDG_DATA_HOME/fonts/org.macos8.desktop/`; a default `make install DESTDIR=<tmp>` writes them
  too; `make uninstall` removes that directory and its `.staging`/`.old` leftovers while leaving a
  sibling font family's directory in place.
- `make check CHECK_TESTS=test_fonts` passes; removing either TTF, changing a byte, renaming the
  family in the font, or dropping the OFL text makes it fail.
- `tests/invariants.py` accepts `theme/fonts` with its `## fonts` section, and
  `make check CHECK_TESTS=test_theme_install test_make_help` passes with the new family.
- No `kdeglobals` write, global-theme `contents/defaults` change, `tools/apply_*` change, GTK or
  Firefox change is made in this part; `make check` is green.

## Done
