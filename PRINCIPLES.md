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
