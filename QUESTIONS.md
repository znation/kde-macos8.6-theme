# Questions

Open questions loops have posted for a human decision — each with context, the
options, and the loop's recommendation. Answer by moving an entry to ## Answered with your decision
(or tell the director). Loops never block on their own questions; they check here at the start of
each tick.

## Open

_None yet._

## Answered

### How should the tooltip palette anchor be grounded?

**Context.** `theme/color-schemes/MacOS8.colors` sets `[Colors:Tooltip]
BackgroundNormal=255,255,204`, and `tests/test_colorscheme.py::TestAnchors` pins that string, but
no collected reference screenshot shows a tooltip / Balloon Help balloon, so unlike the other
palette anchors it cannot be checked against a pixel. Decoding every PNG in
`macos8.6-screenshots/` finds `255,255,204` only as anti-aliasing fragments (a diagonal edge and
small glyph clusters), never as a balloon; the lossy JPEGs show no pale-yellow balloon either.
This is the open BUGS.md entry "Palette anchors are not re-derivable from the reference
screenshots", whose next step needs a reference image the repo does not have.

**Options.**
1. Add a retail Mac OS 8.6 screenshot that shows a Balloon Help balloon (with a legible version
   string, or a source that states 8.6), then sample the balloon fill and add the tooltip anchor
   to `TestReferenceAnchors`. This is the only way to make the anchor re-derivable.
2. Keep the value but drop the claim that it is sampled: record `[Colors:Tooltip]` as a
   KDE-required semantic role whose value comes from the classic Platinum palette, with no Mac OS
   8.6 reference in the set, and state that explicitly in the scheme/test/PLANS.md.
3. Accept a non-retail source (an 8.5 or emulator screenshot) as weak evidence for the tooltip
   colour only — conflicts with the retail-only reference policy.

**Recommendation.** Option 1 if a trustworthy retail screenshot can be supplied; the bugfix loop
could not source one it could visually verify. Otherwise option 2: the tooltip is the one palette
token with no Mac OS 8.6 ground truth, and saying so is better than an unverifiable anchor.

**Decision (2026-10-08):** Option 2. With no retail 8.6 tooltip screenshot available, keep
`[Colors:Tooltip] BackgroundNormal=255,255,204` but drop the claim that it is sampled: record
`[Colors:Tooltip]` as a KDE-required semantic role whose value comes from the classic Platinum
palette, with no Mac OS 8.6 reference in the set. Applied in this tick:
`theme/color-schemes/MacOS8.colors`, `tests/test_colorscheme.py`, and the color-scheme plan's
implementation note in `PLANS.md` now say so; the BUGS.md entry moved to Fixed. A human who can
supply a retail balloon screenshot can still re-ground the anchor (option 1) and reopen the entry.

### Should the close button's click area widen to clear the pinstripes beside it?

(asked 2026-10-17 by the plan role)

**Context.** In Mac OS 8.6 the title-bar pinstripes stop short of the close box. After its
white highlight column come 4 `#CCCCCC` columns, then one column where only the white stripe
rows resume (`aboutsystem_betawiki.png` x=24..28, `systemprofiler_betawiki.png` x=226..230).
Aurorae paints its title-bar tile uniformly under the buttons. The only way to draw that gap is
to widen the close widget to 18px (`ButtonWidthClose=18` in `org.macos8.desktoprc`, with the
gap drawn inside `close.svg`). Then a click up to 5px right of the box, which Mac OS treats as
title bar (a drag), would close the window. The planned zoom-box gap makes the same trade for
the zoom box, where a misclick only toggles maximize.

**Options.**
1. Widen the close button: pixel-exact title bar, slightly larger destructive click target.
2. Keep the close button 13px: the stripes run up to the close box's highlight, a 5-column
   difference from the reference.

**Recommendation.** Option 2. Closing a window by accident costs more than 5 columns of
pinstripe.

**Answered 2026-10-17 by the user:** Let's go with your recommendation of Option 2: Keep the close button 13px: the stripes run up to the close box's highlight, a 5-column difference from the reference.

### Should the theme ship a Kvantum Platinum Qt style, adding Kvantum as a dependency?

(asked 2026-10-18 by the plan role)

**Context.** `contents/defaults` selects Qt's built-in `Windows` widget style, which draws square
bevelled controls (matching systemprofiler_betawiki.png's general look) with no dependency. But
no built-in Qt style draws Platinum exactly — the 2px grey/white bevel, the exact shadow
colours, and the scroll-bar arrows at each end (the `Windows` style's scroll bar only
approximates the reference). A pixel-matched Platinum Qt style needs a style engine such as
Kvantum, whose theme this repo would ship and select with `widgetStyle=kvantum`.

**Options.**
1. Ship a Kvantum theme and select it: pixel-perfect KDE-app controls, but Kvantum must be
   installed separately (a theme cannot install a system package), and when it is absent the
   widgets fall back to another style.
2. Keep the built-in `Windows` style: square bevels, no dependency, not pixel-perfect.

**Recommendation.** Option 1 if the pixel-perfect goal outranks the no-dependency principle —
it is the only path to pixel-exact KDE-app controls — with the fallback documented. Otherwise
Option 2 keeps the current state and the scope-drift note's Qt-style line stays as it is.

**Answered 2026-10-18 by the user:** Let's go with option 1, ship a Kvantum theme and select it.

### May the icon theme reproduce Apple's Platinum icon art, and the Apple logo for the kicker?

(asked 2026-10-18 by the plan role)

**Context.** The scope-drift note in PLANS.md lists the icon theme as unthemed; the reference
desktop/dialog/Finder screenshots show Platinum 32x32 icons. The planned "Mac OS 8.6 Platinum
desktop icon theme" entry ships the hard-disk, folder, document and Trash icons in the Platinum
style — the same kind of reproduction of Apple's Platinum design the theme already ships for
chrome — and selects the theme from the global theme. Two parts are the user's call: whether to
reproduce Apple's Platinum icon art at all, and whether the kicker may use the Apple logo (a
registered trademark).

**Options.**
1. Ship the Platinum icon theme including the Apple logo for the kicker menu icon.
2. Ship the Platinum icon theme but omit the Apple logo (the kicker keeps a generic icon).
3. Do not ship an icon theme.

**Recommendation.** Option 2. The generic Platinum icons follow the project's established
reproduction of Platinum (the planned entry ships them regardless); the Apple logo mark is
deferred unless you explicitly allow it. Answer Option 1 if you want the menu bar's top-left to
match the reference exactly.

**Answered 2026-10-18 by the user:** No, we should come up with our own non-copyright-infringing icon art and logo. Let's use placeholders for now, and keep track of the placeholders so we don't forget to replace them all eventually.

### Which UI font should the theme select?

(asked 2026-10-19 by the director role)

**Context.** The screenshot shows KDE/Plasma text in the current desktop font
(Noto Sans), while Mac OS 8.6 draws its menus, dialogs and window titles in
Charcoal (Chicago in the menu bar); the widths, shapes and pixel rhythm differ
throughout. The theme's `theme/look-and-feel/org.macos8.desktop/contents/defaults`
sets no font keys and `tools/apply_theme.py` writes none, so the user's KDE
font choice is untouched. Fixing this means choosing a font and then writing
`[General] font`, `menuFont`, `toolBarFont` and `smallestReadableFont` plus
`[WM] activeFont` in `kdeglobals` (either through the global theme's defaults
or a `make apply` step; the implementing plan must verify which lookandfeeltool
honours). The font is a new shipped asset, so its licence and provenance
matter, just as they did for the icon art. This covers KDE, Plasma and Qt
applications only; Firefox and GTK applications use their own font stacks and
are the subject of the application-chrome question below.

**Options.**
1. Vendor a Chicago/Charcoal-style outline font whose licence clearly permits
   redistribution, install it with the theme, record its licence and
   provenance, and select it everywhere. Best fidelity; adds a font asset and
   an install/uninstall step; `ChicagoFLF` is the usual free clone candidate,
   but its licence must be checked before it is shipped.
2. Select a humanist sans already present on most desktops (for example Lato,
   which is installed on this machine) without shipping a file. No new asset,
   but only an approximate match to Charcoal.
3. Keep the current font and accept the difference.

**Recommendation.** Option 1 if a clone with a clear redistribution licence
can be sourced and recorded; otherwise option 2 rather than 3. A faithful
Platinum look depends on the text face as much as on the bevels.

**Answered 2026-10-19 by the user:** Let's go with Option 1, vendor a Chicago/Charcoal style font(s). Check for me whether ChicagoFLF license fits our usage, and if not, let's keep looking for a more permissively licensed font (or two? do we need one each for Chicago and Charcoal styles?)

### Should the theme also style GTK applications and Firefox?

(asked 2026-10-19 by the director role)

**Context.** The screenshot's Firefox window draws its own tab-in-titlebar
chrome: no Aurorae frame, rounded tabs and Firefox's own control glyphs. The
Ghostty window already wears our Aurorae frame, but its inner tab strip is
GTK4/libadwaita (`ghostty` links `libgtk-4.so.1` and `libadwaita-1.so.0`), so
it keeps the desktop's GTK theme. A KDE global theme/decoration controls
neither: Firefox switches to a KWin-drawn frame when
`browser.tabs.inTitlebar=0` is set in its profile, and GTK chrome needs a GTK
theme or user CSS. Both are new surfaces outside the current KDE/Qt theme.

**Options.**
1. Document the limits and the Firefox preference; keep the theme KDE/Qt-only.
   Cheap, does not edit a browser profile or change every GTK app.
2. Add opt-in helpers: a GTK 4 CSS theme and a Firefox `userChrome.css` plus
   the profile preference, installed by separate `make` targets. This can
   restyle Ghostty's tab strip and give Firefox Platinum tabs and frame, but
   it affects all GTK/libadwaita apps and edits browser profile files, and it
   is a multi-part series of its own.
3. Add the GTK theme only (no Firefox profile changes).
4. Add the Firefox userChrome only.

**Recommendation.** Option 1 now, as a small README/Installing note, so the
user knows the KDE theme cannot reach those surfaces and how to get the
Firefox frame with one preference. Revisit option 2 as a separate planned
series if full-desktop fidelity outranks keeping the theme KDE/Qt-only.

**Answered 2026-10-19 by the user:** Yes, I guess let's proceed to expand the scope of this project. We should also style GTK applications and Firefox.

### Should the theme ship a lock-screen override to remove the clock's drop shadow?

(asked 2026-10-21 by the director role)

**Context.** The supplied photo is the Plasma lock screen, and its time and date look blurred
because `LockScreenUi.qml` draws a hardcoded `DropShadow` (radius 6, samples 14, spread 0.3)
behind the Breeze `Clock`; the username and the other labels have no shadow. The lock screen is
shell QML, not a desktop-theme widget, and its `config.xml` exposes only `alwaysShowClock`, so
nothing in `theme/` can remove the shadow. BUGS.md records the details. The only project-owned
ways to change it are to ship a lock-screen QML override (or a full custom lock screen), or to
document the limitation and wait for an upstream KDE change. A lock-screen override is a new
Plasma-version-fragile surface, needs a system-level install/selection path, and has no Mac OS
8.6 reference screenshot to ground its layout.

**Options.**
1. Document the limitation and track the shadow removal upstream. No new surface; the blur stays
   until KDE changes the lock screen.
2. Ship a project-owned lock-screen override or custom lock screen with a crisp clock. Fixes the
   blur now, but forks Plasma shell QML and needs revalidation on Plasma updates.
3. Leave the lock screen alone and revisit it only as part of a broader login/lock-screen plan.

**Recommendation.** Option 1 now; option 2 only if the lock screen becomes an explicit scope
expansion, planned separately. The project has no lock-screen artifact and cannot reach the
hardcoded shadow through its existing theme files.

**Answered 2026-10-21 by the user:** Let's go with option 3. Leave the lock screen alone and revisit it only as part of a broader login/lock-screen plan.
