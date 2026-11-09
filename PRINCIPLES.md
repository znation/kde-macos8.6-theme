# Principles

Design principles this project holds — what a senior engineer on this team always does. Every
role's prompt carries them; uphold them in everything you produce. Only the director and steward
roles edit this file, phrasing rules positively. Rationale and provenance: docs/principles-rationale.md.

- Prefer the standard library over a new dependency.
- Keep each file focused on one responsibility, and small enough to read in one sitting.
- Every behavior change ships with a test.
- Keep routine checks off the user's desktop: GUI probes run on an isolated, non-visible display
  or only when explicitly requested, never presenting windows in the user's session.
  (User, 2026-11-09.)
- Small, complete and correct beats big and half-done: one focused change per tick.
- Preserve the user's keyboard mappings; keyboard remapping is outside the theme's scope.
  (User, 2026-11-04.)
- SIGKILL recovery and cleanup is an accepted project-wide Won't Fix: close reports whose sole
  failure needs SIGKILL, don't build recovery machinery or reopen them without a new direction.
  Guarantees for ordinary failures and catchable signals stand; bugs reproducible without SIGKILL
  stay triageable. The limitation covers partial publication across files and leftover temporary
  or backup files. (User, 2026-11-02.)
- Present the theme as "Platinum" with oblique references and original placeholders. Keep Apple
  assets, logos and trademarked names ("MacOS", "Mac OS", "Apple") out of theme-owned UI labels and
  artwork; track placeholders in PLACEHOLDERS.md. Screenshots are measurement evidence only, never
  shipped assets — this outranks pixel fidelity. Selectors get neutral display names; historical
  provenance and internal compatibility identifiers are not UI branding. (User, 2026-10-29.)
- Ground each visual value in the reference screenshots: sample palette and metrics from a lossless
  image and pin each with a test that re-derives that pixel. For any platform-required value the
  references don't show (KDE, GTK, Firefox), record its provenance, naming the missing reference
  surface and the value's source. (Steward, 2026-10-25, scope per QUESTIONS.md.)
- Ship widget art at exactly the size the engine draws it: steer the engine to the art's native
  size first (e.g. Kvantum's `indicator.size`) so art draws 1:1; only if the engine can't be
  steered, re-derive the art at the drawn size and record the deviation. Never let the engine
  resample shipped art. (User, 2026-10-30.)
- Draw unfocused windows as the reference set does: one active window (the frontmost), all others
  inactive with a flat bar, no title-bar boxes, no separate focus look. KWin already realizes
  active=frontmost, so only the inactive decoration art is needed. (User, 2026-11-04.)
