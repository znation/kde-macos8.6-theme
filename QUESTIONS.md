# Questions

Open questions loops have posted for a human decision — each with context, the options, and the
loop's recommendation. Answer by moving an entry to ## Answered with your decision (or tell the
director). Loops never block on their own questions; they check here at the start of each tick.

## Open

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

**Actioned (2026-10-08) by bugfix.** With no retail 8.6 tooltip screenshot available, the loop
applied option 2: the scheme header and the `TestAnchors` docstring now state that
`[Colors:Tooltip]` is the classic Platinum pale-yellow token with no reference in the set, and
`TestProvenanceNote` pins that exception. The BUGS.md entry moved to Fixed. A human who can supply
a retail balloon screenshot can still re-ground the anchor (option 1) and reopen the entry.

## Answered

_None yet._
