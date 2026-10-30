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
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
the 2026-10-29 user decision supersedes its final-art status and queues placeholder tracking
below); the `org.macos8.desktop` Kvantum widget
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
Firefox's `tests/test_firefox_theme_*.py` and `tests/test_firefox_content_*.py` modules
check stylesheet declarations and selector behavior;
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
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows). The
`userContent.css` sheet now styles surfaces within six internal pages:
about:downloads, about:config, about:preferences, about:support, about:networking
and about:telemetry. These include preferences navigation and controls, support
tables and buttons, and telemetry navigation, tables and histograms; this is
surface coverage, not a claim of complete page theming. The opt-in profile install
copies this sheet alongside `userChrome.css`. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### Platinum GTK 4 overlay scrollbar thumbs: retain the ordinary minimum breadth (planned 2026-10-29 by the plan role; independent of the queued ordinary trough margin plan) — done 2026-10-29 by the feature role

**Goal.** Through the supported `make apply-gtk` user stylesheet import, give overlay thumbs the ordinary thumb's 12px transverse minimum in hovering and non-hovering states. The finished 2026-10-24 breadth plan explicitly excluded overlays; stock libadwaita selectors still supply smaller transverse minima.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, add a group for `scrollbar.overlay-indicator.horizontal.hovering > range > trough > slider` and `scrollbar.overlay-indicator.horizontal:not(.hovering) > range > trough > slider` declaring only `min-height: 12px`; add the corresponding two vertical selectors declaring only `min-width: 12px`. These selectors tie or exceed the stock state specificity. Add a dated adaptation comment: no reference shows GTK overlay scrollbars; reuse the ordinary thumb minimum derived from the reference band minus the existing borders. In `tests/test_gtk4_theme.py`, add `TestGtk4Theme.test_scrollbar_overlay_thumb_breadth` using `assert_rule` for these four selectors, comparing each transverse value to the base slider's corresponding minimum. Extend `TestScrollbarBreadthReference.test_thumb_band_matches_reference` to assert those four values equal `f"{band - 4}px"`, using its existing sampled band, and assert that the base thumb and trough borders are each `1px solid #000000` through `BLACK`. Under `## gtk` in `docs/invariants.md`, record the declaration guarantee, tests and missing overlay reference surface. Cite the ordinary-band source (`setup_emaculation.png`, x=200, y=462..477) and `/org/gnome/Adwaita/styles/base.css` in `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`, inspected 2026-10-29: non-hovering overlay thumbs have 3px minima in both axes, hovering horizontal thumbs have an 8px minimum height and hovering vertical thumbs an 8px minimum width. Keep library provenance outside CSS for `test_stands_alone`.

**Acceptance criteria.** Each orientation/state selector explicitly declares the 12px transverse minimum; removing one or restoring its stock 3px/8px value fails the new declaration test and the reference-derived assertion. Existing scrollbar paint, outline and base breadth coverage passes. The invariant states that these are minimum-size declarations, not proof of rendered overlay breadth: inherited trough margins, allocation and overlay visibility remain outside this plan. Preserve toolkit longitudinal minimum-length rules; change no overlay spacing or visibility policy. Limit implementation to these three files. This can merge independently of the ordinary trough margin reset. `make check` passes.

_None yet._

### Platinum GTK 3 overlay scrollbar thumbs: declare a reference-derived minimum (planned 2026-10-29 by the plan role; independent of the GTK 4 overlay breadth plan)

**Goal.** Give GTK 3 overlay thumbs an explicit minimum when the theme disables their steppers. The GTK 3 sheet currently gives `scrollbar slider` borders and paint but no minimum dimensions; the finished GTK 4 breadth work does not cover this sheet. This is a declaration guarantee, not a claim about current rendered allocation.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, add `scrollbar.overlay-indicator slider { min-width: 12px; min-height: 12px; }`. Add a dated adaptation comment: the reference set has no GTK overlay scrollbar; reuse the ordinary 16px reference band minus the scrollbar's and slider's two 1px borders, as in GTK 4. Keep ordinary GTK 3 sizing and the overlay stepper policy intact. In `tests/test_gtk_theme.py`, add `TestGtkTheme.test_overlay_scrollbar_thumb_minimum` using `assert_rule` for the new selector. Add `TestScrollbarStepperReference.test_overlay_thumb_minimum_matches_reference`: sample the black boundaries at x=200, y=462 and y=477 and the intervening `TROUGH` pixels from `setup_emaculation.png`; derive `band = bottom - top + 1`, parse the sheet with the existing guarded `gtk_css.read_theme_text` and `parse_css`, assert both scrollbar and slider borders are `1px solid {BLACK}`, and compare both new minima with `f"{band - 4}px"`. Under `## gtk` in `docs/invariants.md`, record this minimum-size guarantee and both tests; identify the missing GTK overlay reference surface and the existing GTK 4 reference-band calculation as the adaptation source.

**Acceptance criteria.** The overlay selector explicitly declares both 12px minima; deleting either declaration or changing its value fails the declaration and reference-derived checks. The reference test re-derives the band from lossless pixels rather than asserting a standalone size constant. Existing ordinary scrollbar and stepper tests pass. Limit implementation to these three files; introduce no visibility policy or rendered-geometry claim. `make check` passes.

## Done
