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

### Platinum GTK 4 linked groups: share one border between adjacent members (planned 2026-10-29 by the plan role; completes the landed GTK 3 linked-group sibling in PLANS-DONE.md and depends on no waiting entry)

**Goal.** In a GTK 4 container carrying the `linked` class (the groups GTK 4 builds around
entries-plus-buttons, horizontal spin buttons inside a chained group and dropdowns chained to
one), the sheet's generic 1px black borders double up exactly as they did on GTK 3: two members
meeting edge to edge paint a 2px black band, while every separate control the sheet draws uses
one line. Give linked members one shared black border between themselves, without touching the
landed recipes that already style specific linked containers.

**Verified facts, method and values (checked 2026-10-29).** The stock GTK 4 scheme inside
`/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`, resource `/org/gnome/Adwaita/styles/base.css`
(extracted with `gresource extract`; lines 1116-1162 of the extract), shares linked-group
borders differently from GTK 3: it flattens member radii (`border-*-radius: 0` on
`:not(:first-child)`/`:not(:last-child)` arms over `button`, `menubutton > button`, `dropdown >
button`/`combobox > button`, `colorbutton > button`, `fontbutton > button` and `tabbutton >
button`, and their `.linked.vertical` variants) and overlaps full borders with negative margins
(`margin-left: -1px` horizontally, `margin-top: -1px` vertically). The extraction names GTK 4's
member spellings — including the `dropdown` node, GTK 4's combobox — but not the sharing
mechanism this project uses: this sheet paints real 1px solid black borders on real radii-0
members, so the landed GTK 3 scheme (drop the trailing border style, restore it on
`:last-child`; PLANS-DONE.md, the landed linked-group plan and its
`tests/test_gtk_theme.py::TestGtkTheme::test_linked_members_strip_their_trailing_border` suite)
transfers unchanged in mechanism. Adopt the GTK 3 mechanism with GTK 4's member spellings: the
strip names `button`, `entry`, `spinbutton:not(.vertical)` and `dropdown > button` — generic
node names the landed sheet rules at `button` and `entry, spinbutton:not(.vertical),
spinbutton.vertical > text` already cover; `dropdown > button` mirrors the stock member list
(the landed `combobox arrow, dropdown arrow` rule already names that node). Vertical members
keep the same four-name list under `.linked.vertical >`. A vertical spin button's field border
lives on the `spinbutton.vertical > text` child node, not on a direct child of the linked
container, so vertical spin-button fields keep their full borders inside a vertical group — a
recorded decided adaptation, since no collected reference screenshot shows a vertical linked
spin group. Protection: the landed tab recipes must win over
the strip — `stackswitcher > button` ((0,0,2), PyGObject probe 2026-10-29 with GTK 4.18.6
confirmed the stack-switcher node carries the `linked` class) and `pathbar > scrolledwindow >
viewport > box > button` ((0,0,6), the sheet's own provenance header records the `linked` class
among the path bar's GTK-required classes on that box end of the hierarchy) both fall under the
strip's (0,2,1) on specificity, so two guards re-assert the outlines: `stackswitcher.linked >
button:not(:last-child)` ((0,2,2)) and `pathbar > scrolledwindow > viewport > box.linked >
button:not(:last-child)` ((0,2,5)), each restoring `border-right-style` and `border-bottom-style`
regardless of file position, mirroring the landed GTK 3 guard's shape. Members keep their landed
bevels (`button`'s `inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`; the entry field's `inset 1px
1px #999999`) — the seam shows the following member's highlight shoulder beside the shared black
line, the decided adaptation already recorded in the landed GTK 3 plan. No reference
screenshot in `macos8.6-screenshots/` shows a GTK linked group, so this is a platform
adaptation: the stock resource sources the selector spellings (the `linked` class is
GTK-required), while the shared-seam values are the landed button/entry border declarations.
Right-to-left direction subtleties and focus-seam color propagation stay out of scope; no
collected screenshot shows either.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: (1) append one
sentence to the provenance header comment immediately before its closing `*/`: "A linked group
shares one black border between its members; no reference screenshot shows a GTK linked group,
and the linked class is GTK-required." (2) After the final `.navigation-sidebar > flowboxchild`
rule that ends the file, add a `/* Linked groups share one black border between members; the
stock GTK 4 scheme sources the selector spellings (2026-10-29) */` comment plus the rules: the
horizontal strip rule naming the four member spellings under `.linked:not(.vertical) >` with
`border-right-style: none`, the same selector list with `:last-child` restoring
`border-right-style: solid`, the same two rules over `.linked.vertical >` with
`border-bottom-style`, and the two protection rules above that restore both styles for the
stack-switcher and path-bar members. Keep library names outside the CSS: the sheet test asserts
no "adwaita" string (`tests/test_gtk4_theme.py`, the sheet-content assertions after the index
probe). In `tests/test_gtk4_theme.py`, add three `TestGtk4Theme` tests mirroring the landed GTK
3 trio: `test_linked_members_strip_their_trailing_border` (asserts `border-right-style: none`
on the four horizontal strip selectors and `border-bottom-style: none` on the four vertical
ones), `test_linked_last_member_restores_the_border` (asserts both `:last-child` rules) and
`test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines` (asserts both guards'
declarations and that the landed `stackswitcher > button` and `pathbar > scrolledwindow >
viewport > box > button` recipes still declare `border: 1px solid #000000`, keeping the landed
tab recipe intact). In `docs/invariants.md`, append a row under `## gtk` mirroring the GTK 3
linked-group row: no collected screenshot shows a GTK linked group, so this is a platform
adaptation; the stock `/org/gnome/Adwaita/styles/base.css` resource in
`/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`, inspected 2026-10-29, sources the selector
spellings while its own negative-margin sharing mechanism differs; the 1px black seam values are
the landed button/entry border declarations; the declaration checks do not establish rendered
pixels.

**Acceptance criteria.** Every linked member except the last declares its trailing edge
border-less, and the last declares it solid, so a group paints one black line between members;
removing a strip rule, flipping a side, or widening the strip to the stack switcher or path bar
fails one of the three new tests, and the landed stack-switcher and path-bar recipes stay
byte-for-byte unchanged (pinned by the existing shared `TAB_STATES` case plus the new
protection test). Vertical spin-button fields keep their full borders (the `text` child node is
not the strip's member); no test pins a strip rule on them — the four-name vertical list stays
symmetrical with the horizontal one. Scope is the three named files; right-to-left groups,
focus-seam color propagation, `menubutton`/`colorbutton`/`fontbutton`/`tabbutton` members, GTK 3
CSS (already landed) and rendered pixels stay out of scope. No new palette value, artwork or
dependency. `make check` passes.


## Done
