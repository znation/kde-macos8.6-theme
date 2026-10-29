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

_None yet._


_None yet._

_None yet._

_None yet._

_None yet._

### Platinum GTK 4 pill buttons: square painted corners (planned 2026-10-29 by the plan role)

**Goal.** Extend the existing square-button treatment to GTK 4 pill buttons, including the painted menu-button wrapper.

**Grounding.** Searches of `theme/gtk`, `tests/test_gtk4_theme.py` and plan headings in `PLANS.md` and `PLANS-DONE.md` found no pill-button treatment or plan. The installed `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0` resource `/org/gnome/Adwaita/styles/base.css` gives `menubutton.pill > button` and `button.pill` a 9999px radius, and separately gives `menubutton.suggested-action.pill` and `menubutton.opaque.pill` that radius. No reference screenshot shows a GTK pill button; zero radius adapts the sheet's existing `button` and `frame > border, .frame` treatment, as a platform adaptation rather than a sampled pill metric.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, add one grouped rule for those four exact selectors declaring only `border-radius: 0`, beside the frame adaptations. Add a dated comment naming the absent reference surface and existing square-button source; keep the library name out of CSS comments because `TestGtk4Theme.test_stands_alone` rejects its substring. In `tests/test_gtk4_theme.py`, add `TestGtk4Theme.test_pill_button_corners` following `test_card_corners`. In `docs/invariants.md` under `## gtk`, record the missing surface, source selectors and library resource, the reused radius, and `make apply-gtk`'s user-import override path. Keep padding, size, color, focus and circular-button treatment outside this change.

**Acceptance.** Assert that selectors containing `.pill` are exactly the four named above, each complete parsed declaration dictionary is `{"border-radius": "0"}`, and each radius equals `button`, `frame > border` and `.frame`. Describe these as declaration checks without claiming rendered-pixel evidence. Run `make check`. Implementation stays within the three named files and comfortably below a few hundred changed lines including tests; the four selectors form one corner treatment for the same control variant.

### Platinum GTK 4 emoji completion: square suggestion-row corners (planned 2026-10-29 by the plan role; independent of the queued pill buttons)

**Goal.** Give GTK 4 emoji-completion suggestion rows square corners consistent with the existing Platinum frame treatment.

**Grounding.** Searches for `emoji` in `theme/gtk`, `tests/test_gtk4_theme.py` and `PLANS.md`, and related headings in `PLANS-DONE.md`, found no existing treatment or plan. The installed `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0` resource `/org/gnome/Adwaita/styles/base.css` gives `emoji-completion-row` a 9px radius; its focus, hover and active rules supply background paint without replacing that radius. No reference screenshot shows GTK emoji completion. Zero radius reuses `frame > border, .frame` as a platform adaptation rather than a sampled emoji metric.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, add `emoji-completion-row { border-radius: 0; }` beside the frame adaptations, with a dated comment naming the absent reference surface and the reused frame treatment. Keep the library name out of CSS comments because `TestGtk4Theme.test_stands_alone` rejects its substring. Add `TestGtk4Theme.test_emoji_completion_row_corners` in `tests/test_gtk4_theme.py`, following `test_card_corners`. In `docs/invariants.md` under `## gtk`, record the missing surface, library/resource selector provenance, reused radius, test, and `make apply-gtk` user-import override path. Limit this plan to suggestion-row corners; emoji-picker cells are an independently implementable surface, and paint, spacing and glyph sizing are outside this change.

**Acceptance.** Assert that the sheet's selectors containing `emoji-completion-row` are exactly the bare selector, that its complete parsed declaration dictionary is `{"border-radius": "0"}`, and that its radius equals both `frame > border` and `.frame`. Record these as declaration checks without claiming rendered-pixel evidence. Run `make check`. Implementation is limited to the three named files and a small rule, test and provenance entry.

### Split the parallel check coordinator by responsibility (planned 2026-10-29 by the organize role)

**Goal.** Make `tools/check_parallel.py` a small CLI coordinator by separating discovery and log naming, worker lifecycle, and result interpretation into focused modules.

**Why.** `tools/check_parallel.py` is 533 lines, the largest Python production module in `tools/` (the next is `tools/png/stream.py` at 359 lines). It currently combines unittest-compatible filesystem discovery, collision-safe log assignment, signal-safe subprocess spawning and supervision, log-based exit interpretation, output formatting, and CLI parsing in one module. These are distinct responsibilities with separate invariants; the worker lifecycle in particular carries signal and process-group guarantees that should be readable independently from reporting policy. Recent coordinator bug fixes have touched supervision and reporting behavior, so a full split should keep each concern directly inspectable.

**Target structure and files.** Keep `tools/check_parallel.py` for argument parsing and `main`; move `discover_modules` and `_log_paths` with their discovery constants into `tools/check_parallel_discovery.py`; move `_NeverStarted`, `_Worker`, `_spawn`, `_kill_group`, `_reap`, `_supervise` and their process constants into `tools/check_parallel_workers.py`; move `_plural`, no-tests verdict constants, and `_print_results` into `tools/check_parallel_results.py`. Update the coordinator to call these modules, preserving both package imports and direct-script execution. Update `tests/test_check_parallel.py` to import and patch the extracted helpers at their defining modules, and update this tooling row in `docs/invariants.md` to identify which tests pin each module's guarantees. Do not leave forwarding aliases that preserve the old private layout.

**Acceptance.** Keep discovery order, worker limits, log collision handling, timeout and signal cleanup, empty-run proof, output formatting, and exit codes unchanged. The tests cover the moved behavior at its new module paths, `python3 tools/check_parallel.py` still works directly, a source/test/docs search finds no stale helper references on `check_parallel`, and `make check` passes. Limit this to the four production modules, the existing coordinator test module, and the matching invariants row.

## Done
