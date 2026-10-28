# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
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
selected by `apply-gtk`; `make install` copies no GTK files); the standalone Firefox Platinum
sheets under `theme/firefox/` (its `userChrome.css` and `userContent.css` copied, and its
profile preference written, only by the opt-in `install-firefox` target); and the render and
fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme_*.py` modules check stylesheet declarations;
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
landed, while its profile install is part 2/2, which has landed). Firefox work since that
series landed as single-surface chrome plans (the downloads-panel and all-tabs rows, the
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows), and it now
reaches a content page: the `userContent.css` sheet paints the about:downloads
list (part 1/2), and its opt-in profile install as part 2/2 has also landed. That is an
extension of the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

_None yet._

### Firefox Platinum content: paint about:support's tables, column-header cells and buttons as the Platinum sunken list field, raised headers and push buttons (planned 2026-10-27 by the plan role; Library parts 5/6 and 6/6 landed 2026-10-27 — they touched `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py` and `tests/test_firefox_theme_library.py`, and their `docs/invariants.md` rows were appended with the last firefox row in place, so this plan's append-one-row edit and its disjoint file set (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py`, where `userContent.css`'s last `@-moz-document` block is still the about:preferences block the plan names) stand on their own; parenthetical re-stamped 2026-10-27 by the steward role; no other content surface or page waits behind it)

**Goal.** After the landed content adaptations (about:downloads, about:config, the about:preferences series), the troubleshooting page Firefox builds at `about:support` is stock: its tables keep `chrome/toolkit/skin/classic/global/in-content/info-pages.css`'s hairline-bordered `--table-*` paint and rounded `var(--border-radius-small)` corners, and its ten buttons keep the stock button face. This plan repaints the page as the Platinum window body's content: each `#contents` table as the landed sunken list field with `#EEEEEE` alternate rows, each `th` header cell as the Library content-tree's raised column-header face, and every page button as the landed Platinum push button. The page body, its `h1`/`h2` section headings, the loaded-about paragraphs, the pre-existing `.action-box` card, the codec table's supported/unsupported washes and the `tree`, `details` and generated sub-table helpers stay Firefox's.

**Verified facts (checked 2026-10-27 against the installed Firefox ESR 153.5.1, browser/toolkit `omni.ja`).**
- `chrome/toolkit/content/global/aboutSupport.xhtml` is the page loaded at `about:support` (its `aboutSupport.js` self-references `about:support` in its error paths) — one light-DOM HTML document: `grep -c attachShadow` returns 0 for both `aboutSupport.xhtml` and `aboutSupport.js`, so every node the rules touch is reachable from a document-level rule (unlike `about:logins` and `about:addons`, whose rows and search fields live in shadow roots with no `::part`, so they are out of this plan — recorded here so the next plan run does not re-open them).
- The markup defines exactly ten `<button id="…">` elements: `#copy-raw-data-to-clipboard` and `#copy-to-clipboard` in the page header, `#reset-box-button`, `#restart-in-safe-mode-button` and `#clear-startup-cache-button` inside `.action-box`, and `#profile-dir-button`, `#enumerate-database-button`, `#verify-place-integrity-button`, `#place-database-stats-toggle` and `#support-printing-clear-settings-button` inside `#contents`. Its tables are plain `<table>` elements inside `div#contents` (26 `<table>` tags statically — most rows are built by `aboutSupport.js`'s `$.new` helper with no row classes — with 59 `th class="column"` header cells plus four `th class="name"`/`th class="value"`), and and `chrome/toolkit/skin/classic/global/aboutSupport.css` styles `#codec-table`'s cells with green/cream supported/unsupported washes painted on the `td`s themselves.
- `info-pages.css` (the page's imported skin base) paints `table { background-color: var(--table-background-color); … border-radius: var(--border-radius-small); border-spacing: 0; }`, `th { background-color: var(--table-header-background-color); border: 1px solid var(--table-border-color); }` and `td { border: 1px solid var(--table-border-color); }` — rules the sheet must override per arm; `body.wide-container` paints no background of its own, so `body` stays Firefox's and this plan paints no page-background rule (the landed about:config and about:downloads precedents likewise paint widget faces only).

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot in `macos8.6-screenshots/` shows any Firefox surface, so this page samples no reference pixel: the face, outline and sunken shadow adapt `widgets/lineedit.svg`'s line-edit recipe, pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference` (grounded in `macos8.6-screenshots/firstboot_betawiki.png`); the `#EEEEEE` alternate rows reuse the pinned `[Colors:View] BackgroundAlternate` trough, re-derived by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_view_background_alternate`; the `th` header face and bevel copy the landed Library column-header recipe byte-for-byte, whose raise is `widgets/tabbar.svg`'s raised tab face, pinned by `tests/test_desktoptheme_tabbar.py::TestTabBar` and `TestTabBarReference`; the `#CCCCFF` selected/hover wash reuses the pinned `[Colors:Selection]`, re-derived by `TestReferenceAnchors.test_selection_background`; and the push-button face/bevel is the shared `widgets/button.svg` recipe, pinned by `tests/test_desktoptheme_button.py::TestButton` and `tests/test_desktoptheme_button_reference.py::TestButtonReference`.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, after the landed `@-moz-document url("about:preferences")` block (the file's last control adaptation), add the block comment `/* about:support tables and buttons adaptation 2026-10-27 (see the header's provenance paragraph) */` and then exactly this block:

```css
@-moz-document url("about:support") {
  #contents table {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #contents table tr:nth-child(2n) {
    background-color: #EEEEEE !important;
  }

  #contents table th,
  #contents table td {
    border: 0 !important;
    border-radius: 0 !important;
  }

  #contents table th {
    background-color: #DDDDDD !important;
    color: #000000 !important;
    box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
  }

  #contents table th:hover {
    background-color: #CCCCFF !important;
    color: #000000 !important;
    box-shadow: none !important;
  }

  #copy-raw-data-to-clipboard,
  #copy-to-clipboard,
  .action-box button,
  #profile-dir-button,
  #enumerate-database-button,
  #verify-place-integrity-button,
  #place-database-stats-toggle,
  #support-printing-clear-settings-button {
    background-color: #DDDDDD !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
  }

  #copy-raw-data-to-clipboard:hover:not(:disabled),
  #copy-to-clipboard:hover:not(:disabled),
  .action-box button:hover:not(:disabled),
  #profile-dir-button:hover:not(:disabled),
  #enumerate-database-button:hover:not(:disabled),
  #verify-place-integrity-button:hover:not(:disabled),
  #place-database-stats-toggle:hover:not(:disabled),
  #support-printing-clear-settings-button:hover:not(:disabled) {
    background-color: #CCCCFF !important;
    color: #000000 !important;
    box-shadow: none !important;
  }
}
```

The zebra arm lands beneath the codec table's own `td` washes, so `#codec-table`'s supported/unsupported cells keep their status colours while their outer face and outline become the field's; the header paragraph states this. The last two `th`-adjacent cells (`th.name`/`th.value`) take the same header face, so the whole palette paints one raised header run.

In `tests/test_firefox_content_theme.py`: insert module constants and a `REQUIRED_SUPPORT_RULES` dict after the landed `REQUIRED_PREFERENCES_RULES` dict and before `class SheetCase` — `SUPPORT_LIST = "#contents table"`, `SUPPORT_ZEBRA = SUPPORT_LIST + " tr:nth-child(2n)"`, `SUPPORT_CELL = SUPPORT_LIST + " th, " + SUPPORT_LIST + " td"`, `SUPPORT_HEADER = SUPPORT_LIST + " th"`, `SUPPORT_HEADER_HOVER = SUPPORT_HEADER + ":hover"`, `SUPPORT_BUTTONS` (the eight-arm id/`.action-box button` face selector above), `SUPPORT_BUTTONS_HOVER` (its `:hover:not(:disabled)` companion) — with dict values copied from the landed `FIELD_RULE`, `BUTTON_RULE` and `BUTTON_HOVER_RULE` shared arms so the new arms are byte-identical to the landed recipes; the `SUPPORT_ZEBRA` value is `"background-color": f"{TROUGH} !important"` as `CONFIG_ODD` already records, and the `SUPPORT_CELL` value is `{"border": "0 !important", "border-radius": "0 !important"}`.

Then add `class TestFirefoxSupportTheme(SheetCase)` after the landed preferences field/menulist class, with at least: `test_support_rules_match_the_required_rules` (each arm equals its `REQUIRED_SUPPORT_RULES` entry byte-for-byte and the at-rule register gains the `about:support` body — extend whichever landed test enumerates the sheet's `@-moz-document` bodies, currently `test_sheet_has_the_downloads_config_and_preferences_at_rules`, to name the fourth URL); `test_support_table_rules_scope_to_the_contents_div` (via `support.selector_matching`'s `element`/`matches`: the selectors match a `table`/`th`/`tr` inside `#contents` and carry no token from `FORBIDDEN_PAGE_CHROME`, keeping the landed `body`/`h1` guard intact); `test_support_buttons_scope_to_the_page_ids` (the face selector matches `element("button", "copy-to-clipboard")` and the `.action-box` arm, not a chrome-scope element — and its hover arm excludes a `:disabled` button); `test_support_rules_use_the_pinned_palette` (every hex in `{BLACK, WHITE, GREY, FACE, TROUGH, SELECTION}` plus `BUTTON_SHADOW` resolves to the constants' pinned values and introduces no token outside the pre-existing sheet member set); and `test_header_names_support_provenance` (pattern: the landed `test_header_names_preferences_provenance`) asserting the new header paragraph carries the strings named below.

In the same file extend no other class's assertions: none of the landed selectors or arms change.

The header comment gains exactly one paragraph, after the landed about:preferences paragraph and before the closing `*/`, naming: `aboutSupport.xhtml`/`aboutSupport.js`'s light-DOM markup (the ten ids and the `th` classes as verified above), the recipes and pinned tests from the grounding list, the sentence that the codec table's status washes survive beneath the field Zebra, the sentences that the page body, headings, `.action-box` card and generated helper tables stay Firefox's, the note that `about:logins` and `about:addons` are shadow-DOM pages this document-level sheet cannot reach, the applicability sentence (the page loads top-level in a tab like the landed about:config, and the implementer performs the same headless ESR run with a temporary profile and a `@-moz-document url("about:support")` recolour rule the sheet's about:downloads paragraph records, stating what it showed), and the sheet's standard "declaration checks do not establish rendered pixels" close.

In `docs/invariants.md`, in the `## firefox` table: append exactly one row after the last firefox row with the guarantee in one sentence (the `#contents` tables are the `#FFFFFF` sunken list field with square `1px` `#000000` outline, the `#999999` top-left shadow and `#EEEEEE` alternate rows, their `th` cells the raised `#DDDDDD` header face with the flat `#CCCCFF` hover, and the page's ten buttons plus `.action-box`'s buttons the Platinum push button with that hover while disabled buttons keep Firefox's paint) and the test column naming `tests/test_firefox_content_theme.py::TestFirefoxSupportTheme`; trim no landed row (this plan closes no other surface).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet gains exactly the seven rule blocks above inside one new `@-moz-document url("about:support")` block after the about:preferences block, introducing no hex outside the pre-existing sheet member set (`{#DDDDDD, #000000, #888888, #999999, #FFFFFF, #AAAAAA, #CCCCFF, #EEEEEE}`), changing no landed rule's text, and introducing no `body`/`h1`-scoped selector (`FORBIDDEN_PAGE_CHROME` stays green).
- `TestFirefoxSupportTheme`'s tests pass; the `REQUIRED_SUPPORT_RULES` entries and the extended at-rule enumeration test pass without edits to any landed arm.
- The header gains exactly one paragraph after the about:preferences paragraph and before `*/`, carrying the provenance strings above (pinned by `test_header_names_support_provenance`), with the headless-run sentence stating what the run showed.
- `docs/invariants.md` gains exactly one appended row after the last `## firefox` row with `TestFirefoxSupportTheme` in its test column and no landed row's wording changed; `tests/support/invariants.py`'s register stays in step.
- `make check` passes.


## Done
