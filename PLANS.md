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

### Firefox Platinum chrome: use Platinum hover and pressed fills for address-bar buttons (planned 2026-10-25 by the plan role; independent of the address-bar results dropdown plan)

**Goal.** Give Firefox's address-bar buttons the same #EEEEEE hover and #CCCCFF pressed/open fills as the sheet's toolbar buttons. The current sheet sets `--toolbarbutton-background-color-hover` and `--toolbarbutton-background-color-active`, but not the separate `--urlbar-box-background-color-hover` and `--urlbar-box-background-color-active` tokens those controls consume. This is one state-palette change, independent of the queued results-row styling.

**Grounding.** In `/usr/lib/firefox-esr/browser/omni.ja`, `chrome/browser/skin/classic/browser/urlbar/urlbar.tokens.css` defines these two tokens on `:root, :host` using Firefox button colours and dark-mode colour mixing. `identity-block/identity-block.css` under the same browser skin consumes them for `.identity-box-button`, `#trust-icon-container` and `#tracking-protection-icon-container` hover and pressed/open states. `urlbar-searchbar.css` consumes them for `.urlbar-page-action`, the go buttons, search-mode close buttons and `#urlbar-zoom-button`. The theme does not override these tokens; searches of Planned and the finished-plan archive found no plan covering them.

No reference screenshot shows Firefox address-bar buttons. This is a platform adaptation of the existing toolbar state mapping, not a claim of reference-exact Firefox chrome. Its values come from `tests/support/platinum_palette.py`: `TROUGH` is re-derived by `TestReferenceAnchors.test_view_background_alternate` in `tests/test_colorscheme_reference.py` from `setup_emaculation.png` at (200, 470); `SELECTION` is re-derived by `test_selection_background` from the Introduction banner in `firstboot_betawiki.png`. Keep those pixel tests as the palette evidence.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: add `--urlbar-box-background-color-hover: #EEEEEE !important` and `--urlbar-box-background-color-active: #CCCCFF !important` to `:root`. Extend the header's adaptation provenance to name address-bar button states and their reuse of the toolbar state mapping. Use the shared tokens so Firefox's existing disabled, hover and open selectors continue deciding when a fill applies.
- `tests/test_firefox_theme.py`: add both declarations to `REQUIRED_RULES[":root"]`, using `TROUGH` and `SELECTION`. `TestFirefoxChrome.test_required_rules` must pin each value and its `!important`. Retain the existing palette set.
- `docs/invariants.md`: add address-bar button state fills to the `## firefox` standalone-sheet guarantee and retain its no-reference-screenshot provenance exception.

**Scope.** Change these two background tokens only; idle/focus fills, security glyph colours, outlines, geometry and results-row tokens are outside this plan. The shared tokens also affect Firefox's search go button; this is intentional consistency with the address-bar go button. No new dependency or profile preference is needed.

**Acceptance criteria.**
- `TestFirefoxChrome.test_required_rules` fails when either token is absent, has the wrong value, or lacks `!important`.
- `test_palette_is_exact`, `test_sheet_has_no_at_rule_or_import` and `test_selectors_are_not_universal` pass; the existing reference-anchor tests continue to derive the two reused colours from PNG pixels.
- `make check` passes, including the invariant register checks. Tests pin declarations and palette evidence, not a live Firefox chrome render; retain that limitation in implementation reporting.

## Done
