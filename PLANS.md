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

_None yet._

### Platinum GTK 4 linked groups: extend the strip to menubutton, colorbutton, fontbutton and tabbutton members (planned 2026-10-30 by the plan role; plain follow-up on the landed GTK 4 linked-group plan in PLANS-DONE.md whose strip rules and tests this plan extends; independent of the waiting GTK 3 overshoot-glow plan — it edits the GTK 4 sheet and `tests/test_gtk4_theme.py` while that plan edits the GTK 3 sheet and `tests/test_gtk_theme.py`)

**Goal.** In GTK 4 applications running the installed Platinum theme, a linked group that
chains a `menubutton`, `colorbutton`, `fontbutton` or `tabbutton` (GTK's containers that wrap
their member inside a child button node) still paints the doubled seam: the landed GTK 4
linked plan stripped the trailing border for `button`, `entry`, `spinbutton:not(.vertical)`
and `dropdown > button` only, while these four members match the sheet's generic `button`
rules and keep their full 1px black borders on both sides, so the seam between such a member
and its neighbour reads 2px. Every linked member must share one black line, whatever container
its button lives in.

**Verified facts, method and values (checked 2026-10-30).** The stock resource
`/org/gnome/Adwaita/styles/base.css` inside `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`
(extracted with `gresource extract`) carries linked arms for exactly the four member
spellings this plan adds — `menubutton > button`, `colorbutton > button`, `fontbutton >
button`, `tabbutton > button` in their `.linked:not(.vertical) >` and `.linked.vertical`
forms — so the stock member list beyond the landed four is these four plus
`appchooserbutton > combobox > box > button.combo`. The stock mechanism is the one the landed
plan already recorded: flatten the radii and overlap full borders with `margin-left: -1px`
(and `margin-top: -1px` vertically), not a border-style strip, and the horizontal arms are
doubled per direction (`:dir(ltr)`/`:dir(rtl)` pairs) while the vertical member arms use
descendant combinators. This sheet runs the landed GTK 3 mechanism — `border-right-style:
none` with a `:last-child` restore (`border-bottom-style` vertically) — so, as the landed
plan decided, the arms are translated into the strip's shapes rather than copied verbatim;
the child combinator stays under `.linked.vertical >` so the whole strip keeps one shape, a
recorded adaptation since no collected screenshot shows a vertical chained group. Our own
sheet's generic `button` rule borders every one of these members' inner buttons, which is
why they double the seam today; the sheet's pill rules (`menubutton.pill > button`,
`menubutton.suggested-action.pill`, `menubutton.opaque.pill`) declare only `border-radius`,
so nothing out-ranks the strip on border style for them. No reference screenshot in
`macos8.6-screenshots/` shows a GTK linked group — the same platform-adaptation footing as
the landed plan. No palette value is new: the declarations are the landed strip's `none` and
`solid`.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, extend in place
the four landed strip rules under the `/* Linked groups share one black border between
members; the stock GTK 4 scheme sources the selector spellings */` comment: add the four
spellings `.linked:not(.vertical) > menubutton > button`, `.linked:not(.vertical) >
colorbutton > button`, `.linked:not(.vertical) > fontbutton > button` and
`.linked:not(.vertical) > tabbutton > button` to each of the two horizontal rules, and the
same four spellings under `.linked.vertical >` to the two vertical rules. The
`:last-child` restore rules take the same four spellings each, mirroring the landed lists.
Extend the comment by one dated sentence naming the added members; keep library names out of
the sheet (`tests/test_gtk4_theme.py`'s sheet-content assertions reject the stock scheme's
name). The strip's selector lists grow, but no new rule text is needed — the sheet-rule
parser (`tests/support/gtk_css.py::parse_css` with `_split_selector_list`) keys grouped
rules per selector, so the tests read each selector as its own rule. In
`tests/test_gtk4_theme.py`, extend the member loops of `TestGtk4Theme::
test_linked_members_strip_their_trailing_border` and
`test_linked_last_member_restores_the_border` with `"menubutton > button",
"colorbutton > button", "fontbutton > button", "tabbutton > button"` and the matching
`:last-child` spellings; leave `test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines`
untouched (the guard nodes are different members) and leave every landed assertion
unchanged. In `docs/invariants.md`, extend the GTK 4 linked-group row (or append one
sentence to it) under `## gtk`: no collected screenshot shows a GTK linked group; the four
added member spellings' stock arms come from the `/org/gnome/Adwaita/styles/base.css`
resource in `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`, inspected 2026-10-30; the stock
sharing mechanism (radius flattening plus negative margins, direction-doubled horizontal
arms) differs from the sheet's trailing-border strip, which is the landed adaptation;
`appchooserbutton > combobox > box > button.combo` stays out of scope because the sheet
names no `combobox` member nodes; vertical strips keep the landed child combinator; the
declaration checks do not establish rendered pixels.

**Acceptance criteria.** All four added member spellings strip their trailing border in a
linked group and restore it on `:last-child`, horizontally and vertically, so menubutton,
colorbutton, fontbutton and tabbutton members share one black line per seam exactly like
the landed four; deleting one added selector, adding an undeclared property, or widening
the strip to any fifth member fails one of the two extended tests. The landed
four-member assertions, the protection test's guards and the landed
stack-switcher/path-bar/tab recipes pass byte-for-byte unchanged. Scope is the three named
files; right-to-left groups, focus-seam colour propagation, the `appchooserbutton`
member and rendered pixels stay out of scope. No new palette value, artwork or dependency.
`make check` passes.

## Done
