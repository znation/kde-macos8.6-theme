# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role):** The
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
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
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

### Firefox Platinum chrome: connect arrow-panel colours to consumed popup tokens (planned 2026-10-25 by the plan role; independent of square arrow-panel corners)

**Goal.** Make arrow-panel bodies use the intended Platinum face, text and border through Firefox's current popup colour tokens. This is one consumer-mapping correction, independently mergeable from the queued square-corners plan.

**Grounding.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css` sets three `--arrowpanel-*` colour properties on `:root`. Searching CSS in the installed `/usr/lib/firefox-esr/omni.ja` and `browser/omni.ja` found no occurrences of those three names. Toolkit `chrome/toolkit/skin/classic/global/popup.css` instead consumes `--panel-background-color`, `--panel-text-color` and `--panel-border-color` in `:is(menupopup, panel)::part(content)`. The sheet supplies these on `menupopup` but not arrow panels. The finished menu-colour plan explicitly left root arrow-panel tokens alone; the waiting arrow-panel plan changes radius only.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: remove `--arrowpanel-background`, `--arrowpanel-color` and `--arrowpanel-border-color` from `:root`. Set `--panel-background-color: #DDDDDD !important`, `--panel-text-color: #000000 !important` and `--panel-border-color: #000000 !important` on `panel[type="arrow"]`. Extend that rule if the corners plan has merged; otherwise create it. Preserve its radius if present and the existing menu declarations. Leave panel contents, shadows, padding and general non-arrow panels outside this change.
- Extend the sheet's provenance comment: no reference screenshot shows Firefox arrow panels; this is a platform adaptation dated 2026-10-25, sourcing the face and black from the existing Platinum menu mapping and naming the toolkit popup.css consumer. Retain the palette evidence in `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_menu_bar_face` and `test_window_chrome_foreground`; introduce no colour or metric.
- `tests/test_firefox_theme.py`: replace the three root expectations in `REQUIRED_RULES` with the consumed tokens on `panel[type="arrow"]`, using `FACE` and `BLACK`. Update `TestFirefoxChrome.test_consumed_popup_colour_tokens_are_scoped_to_menu_popups` and its name to require each of the three consumed colour tokens on exactly `menupopup` and `panel[type="arrow"]`. Keep its obsolete menu-token assertions, and add assertions that the three old arrow-panel properties occur in no parsed rule. Do not change the radius scope test or require host Firefox files.
- `docs/invariants.md`: update the standalone-sheet row under `## firefox` to include arrow-panel body colours, the two permitted selectors, the removed arrow-panel token names and the dated consumer/provenance exception. Preserve the independent radius guarantee as it stands when implementing.

**Acceptance criteria.**
- Required-rule checks reject a missing consumed arrow-panel token, incorrect palette value or missing `!important`; scope checks reject moving these overrides to `:root` or general `panel`, dropping the menu mapping or retaining old arrow-panel properties.
- Existing palette and standalone-sheet checks, reference palette tests and `make check` pass. The correction works as a declaration change whether or not the square-corners plan has merged.
- Report declaration validation separately from live rendering; these tests do not establish rendered Firefox pixels. The face/text/border mapping is one cohesive change, with no new panel-content styling.

## Done
