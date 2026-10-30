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

### Platinum GTK 3 vertical spin buttons: declare a focused outline (planned 2026-10-29 by the plan role; independent of every waiting entry — it completes the horizontal spin-button outline plan, done 2026-10-29, which explicitly excluded vertical spin buttons)

**Goal.** Give focused vertical GTK 3 spin-button fields an explicit Platinum outline. The completed plans outline `entry` and `spinbutton:focus:not(.vertical)`; a focused vertical spin button draws no outline at all, because the sheet imports nothing and replaces the stock theme, so Adwaita's universal focus outline never applies (`TestGtkTheme.test_imports_nothing_and_does_not_mention_adwaita` pins the standalone-sheet guarantee).

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, immediately after the `spinbutton:focus:not(.vertical)` rule in the entry/spin-button field block, add a separate `spinbutton.vertical:focus` rule declaring `outline: 1px dotted #000000`, `outline-offset: 0` and `-gtk-outline-radius: 0` — declare it as its own selector rather than widening the landed horizontal one, so the horizontal expectations stay untouched. Add a dated adaptation comment naming the missing GTK vertical spin-button keyboard-focus reference and the reuse of `button:focus`'s outline, offset and square outline corners. In `docs/invariants.md`, append a row under `## gtk`: no collected screenshot shows a focused GTK spin button, so this is a platform adaptation, not a screenshot measurement. Cite the installed `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` resource `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`, inspected 2026-10-29: it styles vertical spin buttons only for `:disabled`, `:backdrop:disabled` and `:drop(active)` (selectors `spinbutton.vertical:disabled`, `spinbutton.vertical:backdrop:disabled`, `spinbutton.vertical:drop(active)`), it declares no vertical focus rule, and its universal rule supplies `outline-color: alpha(currentColor,0.3)`, `outline-style: dashed`, `outline-offset: -3px`, `outline-width: 1px` and `-gtk-outline-radius: 3px` to every node — that resource sources the selector spelling, while the dotted-black values come from the landed horizontal rule. Keep library names outside the CSS for the standalone-sheet check.

**Tests.** In `tests/test_gtk_theme.py`, add `TestGtkTheme.test_vertical_spinbutton_focus_outline` (pattern: `test_horizontal_spinbutton_focus_outline`): `assert_rule` the three declarations on `spinbutton.vertical:focus` with the `BLACK` constant, then compare each of the three property values against `spinbutton:focus:not(.vertical)` so the two orientations stay equal. Keep `test_horizontal_spinbutton_focus_outline`, `test_entry_focus_outline`, the shared `tests/support/gtk_rule_cases.py` cases and the field-paint expectations unchanged.

**Acceptance criteria.** `spinbutton.vertical:focus` explicitly declares a 1px dotted black outline, zero offset and zero GTK outline radius; removing the rule or changing any declaration fails the new test, and a change to one de-linked orientation also fails the cross-comparison. Scope is the three named files (`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme.py`, `docs/invariants.md`); GTK 4 CSS, GTK 3 rendered focus pixels and keyboard traversal stay out of scope. No new palette value, artwork or dependency. `make check` passes.

### Platinum GTK 3 linked groups: share one border between adjacent members (planned 2026-10-29 by the plan role; independent of the waiting vertical spin-button outline plan)

**Goal.** In a GTK 3 container carrying the `linked` class (the groups GTK builds around
entries-plus-buttons, horizontal spin buttons inside a chained group and combo boxes chained to
one), the sheet's generic 1px black borders double up: two members meeting edge to edge paint a
2px black band, while every separate control the sheet draws uses one line. Give linked members
one shared black border between themselves, without touching the landed recipes that already
style specific linked containers.

**Verified facts, method and values (checked 2026-10-29).** The stock GTK 3 stylesheet inside
`/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, resource `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`
(extracted with `gresource extract`), shares borders in linked groups: its members
drop `border-right-style` in horizontal groups (`filechooser .path-bar.linked > button`,
`.linked:not(.vertical) > combobox > box > button.combo`, `.linked:not(.vertical) >
spinbutton:not(.vertical)`, `.linked:not(.vertical) > entry`, `.linked > button`) and restore it
on `:last-child`, and its vertical variants drop `border-bottom-style` over the same members
(`.linked.vertical > ...`, lines 403-417 of the extract). This plan adopts that selector and
side-sharing scheme with the sheet's own values: the shared seam stays the landed 1px black
(`button`'s `border: 1px solid #000000`), and no `border-radius` or `-gtk-outline-radius`
declarations are needed because every member already declares radius 0. Members keep their
landed bevels (`button`'s `inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`) — the seam shows the
following member's highlight shoulder beside the shared black line, which this plan records as
the decided adaptation rather than a design question. No reference screenshot in
`macos8.6-screenshots/` shows a GTK linked group, so this is a platform adaptation; the stock
resource sources the selector spelling (the `linked` class is GTK-required), while the values are
the landed button/entry declarations. Two landed GTK 3 recipes already style specific linked
containers and must win over the new strip: the file chooser's path bar (`.path-bar > button`,
tab recipe; the `GtkPathBar` node carries the `linked` class with the folder buttons as direct
children) and the stack switcher (`stackswitcher > button`; its node carries the `linked` class
per the landed stack-switcher plan's PyGObject probe). The strip selector
`.linked:not(.vertical) > button` out-ranks `.path-bar > button` on specificity ((0,2,1) vs
(0,1,1)), so the protection re-asserts the outlines with a higher-specificity rule:
`.path-bar.linked > button:not(:last-child), stackswitcher.linked > button:not(:last-child)`
((0,3,1)), which restores `border-right-style` and `border-bottom-style` regardless of the
block's file position. A focused member's propagated seam color (the stock file re-colors the
following member's border under `:focus` and `:drop(active)`) and right-to-left direction
subtleties stay out of scope; no collected screenshot shows either.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: (1) append one
sentence to the provenance header comment immediately before the closing `*/`: "A linked group
shares one black border between its members; no reference screenshot shows a GTK linked group,
and the linked class is GTK-required." (2) Append, after the `placessidebar
row.sidebar-new-bookmark-row` rule that ends the file, a `/* Linked groups share one black
border between members; the stock Adwaita scheme sources the selector spelling (2026-10-29) */`
comment plus the rules: a horizontal strip rule naming `button`, `entry`,
`spinbutton:not(.vertical)` and `combobox > box > button.combo` under
`.linked:not(.vertical) >` with `border-right-style: none`, the same selector list with
`:last-child` restoring `border-right-style: solid`, the same two rules over
`.linked.vertical >` with `border-bottom-style`, and the protection rule above that restores
both styles for the path bar and stack switcher members. Keep library names outside the CSS for
the standalone-sheet check (`TestGtkTheme.test_imports_nothing_and_does_not_mention_adwaita`).
In `tests/test_gtk_theme.py`, add three `TestGtkTheme` tests: `test_linked_members_strip_their_trailing_border`
(asserts `border-right-style: none` on the four horizontal strip selectors and
`border-bottom-style: none` on the four vertical ones), `test_linked_last_member_restores_the_border`
(asserts both `:last-child` rules) and `test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines`
(asserts the protection rule's two declarations and that `.path-bar > button` still declares
`border: 1px solid #000000`, keeping the landed tab recipe intact). In `docs/invariants.md`,
append a row under `## gtk`: no collected screenshot shows a GTK linked group, so this is a
platform adaptation with the stock `<...>/Adwaita/gtk-contained.css` resource inspected
2026-10-29 sourcing the selector scheme; the declaration checks do not establish rendered
pixels.

**Acceptance criteria.** Every linked member except the last declares its trailing edge
border-less, and the last declares it solid, so a group paints one black line between members;
removing a strip rule, flipping a side, or widening the strip to the path bar or stack switcher
fails one of the three new tests, and the landed path-bar and stack-switcher recipes stay
byte-for-byte unchanged (pinned by the existing shared `TAB_STATES` case plus the new
protection test). Scope is the three named files; right-to-left groups, focus-seam color
propagation, GTK 4 CSS and rendered pixels stay out of scope. No new palette value, artwork or
dependency. `make check` passes.



## Done
