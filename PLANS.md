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

### Platinum GTK 3 application notifications: paint the message band (planned 2026-10-28 by the plan role; independent of the queued color-swatch corners)

**Goal.** Give GTK 3's `.app-notification` message surface the existing Platinum infobar band. Keep this one small GTK 3 change; GTK 4/libadwaita toasts are a separate surface outside this plan.

**Grounding.** Searches of `theme/gtk`, the tests, this queue and `PLANS-DONE.md` found no `app-notification` implementation or plan. The installed GTK 3 resource `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` documents `.app-notification` and `.app-notification.frame`, including backdrop and border descendants, as notification styling hooks. Our standalone sheet does not import that sheet. No reference screenshot shows a GTK application notification: explicitly record this platform adaptation, sourcing its face, text and etched edge from the landed `infobar > revealer > box` recipe and its square, shadowless frame treatment from the landed frame/statusbar rules. The existing reference tests `TestReferenceAnchors.test_menu_bar_face` in `tests/test_colorscheme_reference.py` and `TestLineReference` in `tests/test_desktoptheme_line.py` pin the reused palette/etch; do not describe the notification layout as sampled.

**Approach.** After the GTK 3 statusbar rules, add one grouped rule for `.app-notification`, `.app-notification.frame`, `.app-notification:backdrop` and `.app-notification.frame:backdrop`: `background-color: #DDDDDD`, `background-image: none`, `color: #000000`, `border: 0`, `border-bottom: 1px solid #888888`, `border-radius: 0`, `box-shadow: inset 0 -1px #FFFFFF`, `text-shadow: none` and `-gtk-icon-shadow: none`. Put the border reset before the bottom border. The explicit `.frame` arm overrides the generic frame's sunken bevel. Add `.app-notification > border, .app-notification.frame > border { border-style: none; box-shadow: none; }` to clear a notification GtkFrame's own border node without clearing nested content frames. Do not introduce spacing, animation, button or label descendants, assets or dependencies: action buttons use the existing generic button rules. Include a short CSS provenance comment explaining the missing reference and the reused recipe.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme.py`, `docs/invariants.md`.

**Acceptance.** Add `TestGtkTheme.test_app_notification_band` using the existing `assert_infobar` helper for each of the four roots, plus exact parsed-rule dictionary equality for the full declarations above; add `test_app_notification_frame_border` checking exact declarations for the two direct-border selectors. Assert the selectors containing `.app-notification` equal those six selectors, and assert the border reset precedes `border-bottom` in the new block so the parser's dictionary check cannot mask a shorthand-order error. The existing frame, infobar, statusbar, button-state and palette tests stay green. Add a `## gtk` invariant row linking the new tests and recording the adaptation and class-hook source; these are declaration checks, not rendered-pixel evidence. Run `make check`. This is one band treatment, expected to fit well below a few hundred changed lines including tests.

### Platinum GTK 4 libadwaita toasts: square and recolor the message surface (planned 2026-10-28 by the plan role; independent of the queued GTK 3 application notifications)

**Goal.** Give libadwaita's toast container a square Platinum grey face with black text and an outline. This is one container treatment, independent of the GTK 3 notification band; toast buttons, custom title contents, placement and animation are outside its scope.

**Grounding.** Searches of `theme/gtk`, the GTK tests, this queue and `PLANS-DONE.md` found no GTK toast implementation or finished plan. The installed `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0` resource `/org/gnome/Adwaita/styles/base.css` styles `toast` with a `#505053` background, white text, a drop shadow and `150px` radius; its `toast:dir(ltr)` / `toast:dir(rtl)` rules adjust padding. No reference screenshot shows a libadwaita toast. Record this platform adaptation explicitly: reuse the existing GTK 4 `popover > contents, popover > arrow` face, outline, zero radius and shadow reset, with black text from `window, .background`. The face is reference-pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_menu_bar_face`; retain the existing palette/reference coverage rather than calling toast geometry sampled. The `toast` node comes from the named libadwaita resource.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, beside the popover rules, add `toast, toast:backdrop` with exactly `background-color: #DDDDDD`, `background-image: none`, `color: #000000`, `border: 1px solid #000000`, `border-radius: 0`, `box-shadow: none` and `text-shadow: none`. Include a dated provenance comment naming the missing reference surface and reused recipe. Leave stock spacing and directional padding in place; add no descendant overrides or new assets. Add coverage to `tests/test_gtk4_theme.py::TestGtk4Theme` and one matching row under `## gtk` in `docs/invariants.md`. No dependency on the queued GTK 3 implementation is needed.

**Acceptance.** Add `test_toast_surface` asserting exact parsed declaration dictionaries for both selectors and that the set of selectors containing `toast` is exactly those two. Check the shared face, outline, radius and shadow declarations against the parsed existing popover rule, and the text color against `window`, so the adaptation stays tied to its stated source. Existing `test_popover` and `test_only_palette_hex_literals` remain green. The sheet's raw-text test rejects the substring `adwaita` even in comments: call the surface a GTK toast in the CSS comment and put the full library/resource attribution in the invariant. The invariant must name the resource and adaptation and describe these as declaration checks, not rendered-pixel evidence. Run `make check`. Keep the change to these three files and comfortably below a few hundred lines including tests.

## Done
