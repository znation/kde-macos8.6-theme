"""The GTK 4 user-CSS marker spells one string across apply and uninstall.

``tools/gtk_user_files.py``'s ``GTK4_CSS_MARKER`` is the first line
``make apply-gtk`` publishes into ``$XDG_CONFIG_HOME/gtk-4.0/gtk.css`` and
the spelling ``make remove-gtk`` recognizes the sheet by. ``make uninstall``
reaches the same literal through the Makefile's ``GTK_USER_CSS_MARKER``
definition, which its recipe passes as ``uninstall_diagnostics.py``'s
``--css-marker`` so the dangling-selection warning recognizes a published
sheet. The two sides are separate files that no shared import joins: a
spelling edited on one side alone would leave the uninstall diagnostic
permanently silent about a gtk.css the apply really published, with every
fixture-based family test still green: the GTK family's fixtures read the
publisher's constant and follow that side only, and the uninstall-diagnostic
fixtures hand-copy their own literal, so neither tie reaches the Makefile.
These tests pin the Makefile's definition to the publisher's constant and
pin the recipe to the variable, so the marker can only change on both sides
at once.
"""

import os
import re
import unittest

from support import repo_root
from tools.gtk_user_files import GTK4_CSS_MARKER

MAKEFILE = os.path.join(repo_root.ROOT, "Makefile")
# One simple definition per line, e.g. ``GTK_USER_CSS_MARKER := /* ... */``.
DEFINITION = re.compile(r"^GTK_USER_CSS_MARKER\s*:=\s*(.+?)\s*$", re.MULTILINE)
UNINSTALL_RECIPE = re.compile(
    r"^\t.*tools/uninstall_diagnostics\.py.*$",
    re.MULTILINE,
)


def read_makefile():
    with open(MAKEFILE, "r", encoding="utf-8") as handle:
        return handle.read()


class TestMarkerAgreement(unittest.TestCase):
    def test_the_makefiles_marker_is_the_published_first_line(self):
        # The publisher's constant is the source of truth: the sheet a
        # reader must recognize is the one apply wrote. The Makefile
        # definition is spelled out fully on one line, so the agreement is
        # exact rather than a prefix match.
        definitions = DEFINITION.findall(read_makefile())
        self.assertEqual(1, len(definitions), definitions)
        self.assertEqual(GTK4_CSS_MARKER, definitions[0])

    def test_the_uninstall_recipe_takes_its_marker_from_that_variable(self):
        # The recipe must pass the definition, not a second hand-copied
        # literal: a second spelling inside the recipe line would drift from
        # the definition while this file's first test stayed green.
        text = read_makefile()
        recipes = [
            line
            for line in UNINSTALL_RECIPE.findall(text)
            if "uninstall_diagnostics.py" in line
        ]
        self.assertEqual(1, len(recipes), recipes)
        self.assertIn('--css-marker "$(GTK_USER_CSS_MARKER)"', recipes[0])
        # Exactly two spellings of the name exist in the Makefile -- the
        # definition and the recipe's reference -- so the diagnostic's
        # marker has one source in the file make runs.
        self.assertEqual(2, text.count("GTK_USER_CSS_MARKER"))


if __name__ == "__main__":
    unittest.main()
