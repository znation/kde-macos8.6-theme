# Principles

Design principles this project holds — the codified answer to "what would a senior engineer on
this team always do." Every loop's prompt carries these; uphold them in everything you produce.
Only the director and steward roles may edit this file. Phrase new principles positively: state
what to do, not what to avoid. This list is a starting point: the director and steward own it
and will tune it to this project.

- Prefer the standard library over a new dependency.
- Keep each file focused on one responsibility, and small enough to read in one sitting.
- Every behavior change ships with a test.
- Small, complete, and correct beats big and half-done: one focused change per tick.
- Preserve the user's keyboard mappings when installing or applying Platinum. Keyboard
  remapping is outside the theme's scope; remove the shipped modifier-swap feature.
  (Directed by the user 2026-11-04; recorded by the director role.)
- Treat recovery and cleanup after SIGKILL as an accepted Won't Fix limitation across the
  project. Roles should close reports whose sole failure requires SIGKILL as covered by this
  decision, rather than file duplicates, plan recovery machinery, or reopen them without a new
  user direction. Preserve existing guarantees for ordinary failures and catchable signals;
  bugs reproducible without SIGKILL remain eligible for triage. The accepted limitation includes
  partial publication across files and leftover temporary or backup files after SIGKILL.
  (Directed by the user 2026-11-02; recorded by the director role.)
- Present the theme as "Platinum" using oblique references and original placeholder graphics
  for now. Keep Apple graphical assets, logos, and Apple trademarked names or phrases
  (including "MacOS", "Mac OS" and "Apple") out of theme-owned UI labels and artwork.
  Track placeholder artwork in PLACEHOLDERS.md until the user approves replacement work.
  Reference screenshots serve as measurement evidence, never as shipped graphical assets;
  this constraint takes precedence over pixel fidelity. Historical provenance and internal
  compatibility identifiers are distinct from UI branding; give selectors neutral display names.
  (Directed by the user 2026-10-29; recorded by the director role.)
- Ground each visual value in the reference screenshots: sample palette and metric values from a
  lossless image, pin each with a test that re-derives that pixel, and record the provenance of
  any platform-required value the reference set does not show (including KDE, GTK and Firefox).
  For such adaptations, name the missing reference surface and the source of the chosen value.
  (Clarified 2026-10-25 by the steward role for the GTK and Firefox scope approved in QUESTIONS.md.)
- Ship widget art at exactly the size the engine draws it: first try steering the engine to
  render at the design's native size (an explicit size setting matching the art's canvas, as in
  the Kvantum config's `indicator.size`), so shipped art draws 1:1; only when the engine cannot
  be steered do this the other way round — re-derive the art at the size the engine actually
  draws and record the resized cell's deviation from the reference. Never leave shipped art
  somewhere the engine resamples it. (Directed by the user 2026-10-30; recorded by the director
  role.)
- Draw unfocused windows exactly as the reference set's unfocused windows appear: one active
  window (the frontmost one), every other window inactive with a flat bar and no title-bar
  boxes, and no separate focus look. Platinum's model is active=frontmost; KWin already
  realizes it, so emulating it needs no focus machinery — only the inactive decoration art.
  (Directed by the user 2026-11-04; recorded by the director role.)
