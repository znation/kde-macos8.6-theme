# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._


### Platinum GTK 4 OSD checks and radios: restate the stock dark indicator arms with the landed check and radio recipes (planned 2026-10-30 by the plan role; independent of the waiting GTK 3 OSD check-and-radio plan — it appends four check-and-radio arm groups to `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, adds one test beside `test_osd_container_bands` in `tests/test_gtk4_theme.py` and appends one row to the `## gtk` invariants table, while that entry edits only the GTK 3 sheet and `tests/test_gtk_theme.py`; the shared documents are `docs/invariants.md`, where each entry appends its own row, and `tests/support/gtk_theme_spec.py`, from which both import `CHECK`/`RADIO` and neither edits, plus the shared base case both cite — no sheet selector, test function or suite overlaps)

**Goal.** The landed GTK 4 OSD container plan (`PLANS-DONE.md`, "Platinum
GTK 4 OSD overlay containers") repainted every stock OSD overlay container,
but the checks and radios inside those opaque Platinum `#DDDDDD` overlays
still paint the toolkit's dark indicators: the GTK 4 sheet declares nothing
for `.osd check` or `.osd radio` (grep: the sheet's OSD rests are `video
image.osd`, the two `progressbar.osd` trough groups and the landed
`.osd switch:checked` track, plus the landed container block), so the
Default resource's four `.osd` check-radio arms supply translucent dark
bubbles over an accent-tinted focus outline instead of the landed raised
`#DDDDDD` check face and flat white round radio. Restate all four arms with
the landed recipes, so a check or radio inside a Platinum OSD overlay draws
like one everywhere else.

**Verified facts (probed 2026-10-30, `gresource extract
/usr/lib/x86_64-linux-gnu/libgtk-4.so.1
/org/gtk/libgtk/theme/Default/Default-dark.css` and `Default-light.css`,
libgtk-4 4.18.6).** Both resources carry exactly four `.osd
check`/`.osd radio` arms: base and `:hover` (identical declarations in both
resources — dark: `color: #eeeeec`, `outline-color: rgba(21,83,158,0.7)`,
`border-color: rgba(0,0,0,0.7)`, `background-color: transparent`,
`background-image: image(rgba(38,38,38,0.7))`, `background-clip:
padding-box`; light: `outline-color: rgba(53,132,228,0.5)`,
`background-image: image(rgba(53,53,53,0.7))`, otherwise identical);
`:active` (adds `color: white`, `background-image: image(rgba(0,0,0,0.7))`
dark / `rgba(2,2,2,0.7)` light, `box-shadow: none`); `:disabled`
(`color: #8a8a89`, `background-image: image(rgba(58,58,57,0.5))` dark /
`color: #919190`, `image(rgba(71,71,71,0.5))` light). Neither resource
carries a `:backdrop` arm or any `:checked`/`:indeterminate` spelling on the
arm family. No arm sets geometry — `min-*`, `margin` — or an
`-gtk-icon-source`, or recolours the glyph, so the landed plain `check,
radio`, `check`, `radio` and `check:checked`/`radio:checked`/
`check:indeterminate`/`radio:indeterminate` rules (all governed beyond these
arms at equal or lower specificity) keep drawing the shipped assets and the
14px geometry, and the restatement needs no colour, glyph or geometry
decision beyond the recipes below. The platform style library carries no
`.osd check`/`.osd radio` arm at all (`gresource extract
/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0
/org/gnome/Adwaita/styles/base.css`, libadwaita 1.7.6, probed 2026-10-30);
its only `.osd` check/radio rule is the `.osd popover.menu check, .osd
popover.menu radio { background: none; color: inherit; }` popover-menu
transparency override, which this plan leaves untouched alongside the other
libadwaita OSD descendants (buttons, progress, scale, cards) recorded as
later surfaces. No collected reference screenshot shows a GTK OSD
indicator, so this is a platform adaptation reusing the landed recipes —
`CHECK` and `RADIO` in `tests/support/gtk_theme_spec.py` (the raised
`#DDDDDD` check face with the `inset 1px 1px #FFFFFF, inset -1px -1px
#888888` etch, square corners and `margin: 0 4px`; the flat `#FFFFFF` round
radio) — pinned by the landed
`tests/support/gtk_rule_cases.py::GtkSheetRuleCases::test_check_and_radio`,
and the arm selectors and state names are GTK-required (they spell the
toolkit resources' rules).

**Approach and files.** (1) In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`,
append directly after the landed grouped OSD container block a dated
provenance comment naming the missing reference surface, both `gresource`
probes (libgtk-4 Default-dark/Default-light and the libadwaita no-arm fact),
the reuse of the `CHECK`/`RADIO` recipes and the cleared
`outline-color`, followed by four groups — one per stock state — each
restating the stock arm at `.osd check, .osd radio` with the two-rule
recipe shape (a base pair plus the radio override pair). The base group is
literally:

```css
.osd check, .osd radio {
  min-height: 14px;
  min-width: 14px;
  margin: 0 4px;
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #888888;
  outline-color: #000000;
}
.osd radio {
  background-color: #FFFFFF;
  border-radius: 50%;
  box-shadow: none;
}
```

and the `:hover`, `:active` and `:disabled` groups repeat the identical
two-rule shape at the stock spellings `.osd check:hover, .osd radio:hover`
and so on — no stock arm carries a `:backdrop` spelling, and since the
state arms in both resources carry identical paints state-to-state (only
`color` and the translucent bubble differ, both overridden or void), every
state group repeats the recipes byte-for-byte, so a checked arm draws the
shipped glyph over the landed face exactly as it does outside an overlay.
The one clear riding in every group is `outline-color: #000000`: stock
claims an accent-tinted ring (`rgba(21,83,158,0.7)` dark,
`rgba(53,132,228,0.5)` light) in every arm, while the sheet's landed focus
black is `checkbutton:focus:focus-visible { outline-color: #000000 }`, so
black keeps the focus ring like the rest of the sheet (recorded in the
provenance comment). Stock's leftover `color`, `background-clip:
padding-box` and shadow claims stay undeclared: the shipped glyph assets
never recolour or shadow, the check node's node colour reaches no label
(sibling of the check box), and the 1px opaque black border already paints
the padding-box clip's border band — the same call the waiting GTK 3
sibling plan records. Touch no landed rule: not the landed container block,
plain `check`/`radio`/glyph rules, `video image.osd`, the two
`progressbar.osd` trough groups, `.osd switch:checked`, `MENU_CHECK` or the
`.osd popover.menu` transparency override; leave the `button.osd`, grouped
`.osd button`/flat/suggested-action/destructive-action, `.osd entry` and
`.osd spinbutton` field, `.osd progress`/scale, `.scale-popup button.flat`
and libadwaita OSD families for later surface plans (recorded here, not
this change). (2) In `tests/test_gtk4_theme.py`, add
`TestGtk4Theme::test_osd_check_radio` beside `test_osd_container_bands`: add
`CHECK` and `RADIO` to the existing `support.gtk_theme_spec` import list,
build one expected check dictionary (`{**CHECK, "outline-color": BLACK}` —
`BLACK` is already imported from `support.platinum_palette`; `CHECK` already
carries the geometry, margins, `background-image: none`, square corners and
the etch) and one expected radio dictionary (`{**RADIO, "outline-color":
BLACK}`), assert each of the eight per-state, per-node selectors
`tests/support/gtk_css.py::parse_css` splits out of the four groups against
its node's dictionary, assert the four `.osd check` dicts are mutually
equal and the four `.osd radio` dicts are mutually equal (the state arms
are byte-for-byte the recipes), and add the scope assertion that the set of
parsed sheet selectors containing `.osd check` or `.osd radio` equals
exactly those eight. In the same change, extend `test_osd_container_bands`'s
scope filter — the `landed` set that already holds `video image.osd`, the
two `progressbar.osd` trough selectors and `.osd switch:checked` — with the
eight new arm selectors, or the new arms fail that landed test's selector
tokens scan (`.osd check` contains the scanned `osd` token). (3) In
`docs/invariants.md`, in the `## gtk` table, append one row: the guarantee —
every stock GTK 4 OSD check and radio indicator arm draws the landed raised
`#DDDDDD` check face and flat white round radio with black borders, the
etched check shadow and black focus-outline colour, under whatever toolkit
resource loads, identical in all four stock states — with the test column
naming `tests/test_gtk4_theme.py::TestGtk4Theme::test_osd_check_radio` (the
register parser resolves the column only against tests defined in the named
module, so cite the shared base case
`tests/support/gtk_rule_cases.py::GtkSheetRuleCases::test_check_and_radio`
in the provenance cell, not the test column); the provenance cell records
the missing reference surface, the `gresource` probes (libgtk-4 4.18.6
Default-dark/Default-light and libadwaita 1.7.6 base.css, probed
2026-10-30), the reused `CHECK`/`RADIO` specs and their pinning test, the
GTK-required arm spellings, the black outline-colour clear, the geometric
and glyph rules the plain arms keep governing, the untouched libadwaita
`.osd popover.menu` transparent override, and the close-out that
declaration checks do not establish rendered pixels. Trim no landed row;
`tests/test_invariants.py` parses the register.

**Acceptance criteria.** The GTK 4 sheet carries the four groups whose
complete parsed dictionaries are the eight selectors at exactly the two
recipe dictionaries above; changing any of the eight selectors, deleting a
group, dropping the outline-colour clear or the etched check shadow, or
letting stock keep its dark bubbles or accent focus rings fails
`test_osd_check_radio`; `test_osd_container_bands` (with its extended
`landed` set), `test_check_and_radio`, `test_switch_osd_checked_track_color`,
`test_video_osd_image_corners`, `test_progressbar_osd_trough_paint`,
`test_only_palette_hex_literals`, `test_no_universal_selector`,
`test_icon_sources_point_at_shipped_assets` and
`test_no_status_or_translucent_shade_roles` stay green, and the landed
container, plain check/radio and remaining OSD rules keep their landed
text. Scope is the GTK 4 sheet, `tests/test_gtk4_theme.py`,
`docs/invariants.md` and nothing else: no GTK 3 rule, no Firefox sheet, no
new asset, colour literal beyond the landed `#DDDDDD`, `#FFFFFF`,
`#888888` and `#000000`, dependency or `!important`. `make check` passes.


## Done
