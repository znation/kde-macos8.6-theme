"""`make help` completeness: every public target and tunable-variable default.

`make help` is the discoverable index of the Makefile's targets and variables;
these tests derive the expected set from the Makefile and README and fail when
a target or variable is added, renamed or removed without updating the index.
"""

import os
import re
import subprocess
import sys
import unittest
from unittest import mock

from support import containment, repo_root, theme_install
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir


def _read_repo_file(name):
    """Return the UTF-8 text of the repository file *name*.

    ``Makefile`` and ``README.md`` are contributor-supplied, and a checked-in
    symlink at either path can point at a private file. The target and
    variable names parsed from the Makefile, and the README text itself, reach
    assertion diagnostics that echo them (``assertRegex`` prints the whole
    text it searched), so a path that resolves outside the repository is
    refused before it is opened.
    """
    return containment.read_text(
        os.path.join(repo_root.ROOT, name), repo_root.ROOT,
        encoding="utf-8",
    )


class TestReadFileContainment(unittest.TestCase):
    """The README/Makefile read refuses a symlink that escapes the repository.

    A checked-in symlink at ``Makefile`` or ``README.md`` can point at a
    private file, and the names parsed from it (and the README's whole text,
    which ``assertRegex`` echoes) reach failure diagnostics; the read must
    refuse such a path before it is opened rather than leak the private file.
    """

    def _symlinked_root(self, target_text):
        tmp = make_tmp_dir(self)
        root = tmp / "repo"
        root.mkdir()
        secret = tmp / "secret"
        secret.write_text(target_text, encoding="utf-8")
        (root / "README.md").symlink_to(secret)
        return root, root / "README.md"

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        root, link = self._symlinked_root("make private-target\n")
        with mock.patch.object(repo_root, "ROOT", root):
            with self.assertRaises(ValueError) as caught:
                _read_repo_file("README.md")
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        root = make_tmp_dir(self) / "repo"
        root.mkdir()
        target = root / "actual-readme.md"
        target.write_text("make check\n", encoding="utf-8")
        (root / "README.md").symlink_to(target)
        with mock.patch.object(repo_root, "ROOT", root):
            self.assertEqual(_read_repo_file("README.md"), "make check\n")

    def test_refuses_a_fifo_instead_of_blocking(self):
        # `test_readme_names_every_public_target` reads README through this
        # helper; a FIFO at that path would block open() forever. Run in a
        # child so the pre-fix hang is a bounded timeout, not a stalled suite.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        root = make_tmp_dir(self) / "repo"
        root.mkdir()
        os.mkfifo(root / "README.md")
        child = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys, test_make_help; "
                "test_make_help.repo_root.ROOT = sys.argv[1]; "
                "test_make_help._read_repo_file('README.md')",
                str(root),
            ],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(0, child.returncode, child.stdout + child.stderr)
        self.assertIn("not a regular file", child.stderr)
        self.assertIn(str(root / "README.md"), child.stderr)


class TestHelp(unittest.TestCase):
    """`make help` lists every public target and tunable-variable default.

    The Makefile documents each target and variable in a comment, but a
    contributor does not read those; the help target is the discoverable
    index. The public targets are the `.PHONY` names other than the
    `_`-prefixed internals, so reading that line catches a target added
    without a help line instead of pinning a hand-copied list here. Each
    `?=` variable's help line names its literal default, and that default is
    derived from the Makefile rather than copied here, so changing one
    without the other fails.
    """

    # The help output is one deterministic run of a static recipe, so the
    # class runs `make help` once instead of once per test method that reads
    # it. A failed run is not cached, so the next test retries and reports it.
    _help_output = None

    def _output(self):
        if TestHelp._help_output is None:
            env = theme_install.make_env("CHECK_PATTERN")
            result = theme_install.run_captured(
                ["make", "help"],
                cwd=repo_root.ROOT,
                env=env,
            )
            assert_succeeded(self, result)
            TestHelp._help_output = result.stdout
        return TestHelp._help_output

    def _public_targets(self):
        """Return the `.PHONY` targets other than the `_`-prefixed internals."""
        phony = next(
            line
            for line in _read_repo_file("Makefile").splitlines()
            if line.startswith(".PHONY:")
        )
        return [
            name
            for name in phony.split(":", 1)[1].split()
            if not name.startswith("_")
        ]

    def _question_variables(self):
        """Return every `?=` variable's ``(name, literal default)``.

        A `?=` assignment is the tunable-variable contract: the help target
        documents each one and states its default. Deriving both from the
        Makefile keeps these tests from pinning a second copy that could
        itself drift; only the literal right-hand side is read, so a value
        built from other variables (none today) is out of scope.
        """
        variables = []
        for line in _read_repo_file("Makefile").splitlines():
            match = re.match(
                r"([A-Za-z_][A-Za-z0-9_]*)\s*\?=(.*)$", line
            )
            if match:
                # A `#` starts a Make comment, so an inline note after the
                # value is not part of it; strip it before comparing.
                value = match.group(2).split("#", 1)[0].strip()
                variables.append((match.group(1), value))
        return variables

    def _tunable_defaults(self):
        """Return the literal defaults of the non-empty `?=` variables."""
        return {
            name: value
            for name, value in self._question_variables()
            if value
        }

    def _help_section(self, heading):
        """Return the non-empty lines after *heading* in the help output.

        The help target prints each section as a heading, its lines, then a
        blank line, so a section runs until the next blank (the last section
        has none).
        """
        lines = self._output().splitlines()
        if heading not in lines:
            self.fail(f"help output has no {heading!r} heading")
        section = []
        for line in lines[lines.index(heading) + 1 :]:
            if not line.strip():
                break
            section.append(line)
        return section

    def _help_targets(self):
        """Return the target names the help index lists."""
        return [line.split()[0] for line in self._help_section("Targets:")]

    def _help_variables(self):
        """Return the variable names the help index lists."""
        names = []
        for line in self._help_section("Variables (make VAR=value TARGET):"):
            name, separator, _ = line.split()[0].partition("=")
            if separator:
                names.append(name)
        return names

    def _used_variables(self):
        r"""Return the names the Makefile assigns or references in expansions.

        The inverse of `test_lists_every_tunable_variable`: a help line left
        behind after its variable is removed or renamed would send a
        contributor to a variable the Makefile no longer has. A name counts
        as used when a non-recipe line assigns it (``NAME =``, ``:=``,
        ``?=``, ``+=``) or any line references it in a make expansion
        (``$(NAME)``); ``DESTDIR`` is an external variable the Makefile only
        expands, so both forms are needed. The set is a superset of the
        Makefile's variables (a make function like ``$(call ...)`` also
        contributes its name), which is enough for the subset check below.
        Comments are stripped and make's ``$$`` escape is removed first, so a
        mention in a comment or a shell variable in a macro body does not
        count.
        """
        used = set()
        in_help = False
        for line in _read_repo_file("Makefile").splitlines():
            if line.startswith("help:"):
                in_help = True
                continue
            if in_help:
                # The recipe lines are tab-indented; the first line that
                # is not (the blank after it, or the next rule) ends it.
                if not line.startswith("\t"):
                    in_help = False
                else:
                    continue
            line = line.replace("$$", "")
            line = re.sub(r"(?<!\\)#.*$", "", line)
            if not line.startswith("\t"):
                match = re.match(
                    r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:?+]?=", line
                )
                if match:
                    used.add(match.group(1))
            used.update(
                re.findall(r"\$[({]([A-Za-z_][A-Za-z0-9_]*)[)}]", line)
            )
        return used

    def test_lists_every_public_target(self):
        lines = self._output().splitlines()
        for target in self._public_targets():
            with self.subTest(target=target):
                self.assertTrue(
                    any(line.startswith(f"  {target} ") for line in lines),
                    f"help does not list target {target!r}",
                )

    def test_every_help_target_is_a_phony_target(self):
        r"""The help index must not name a target the Makefile lacks.

        `test_lists_every_public_target` catches a target added without a help
        line; this catches the reverse, a help line left behind after its
        target is removed or renamed, which would send a contributor to a
        missing target. Every help target line names a `.PHONY` target.
        """
        phony = set(self._public_targets())
        for target in self._help_targets():
            with self.subTest(target=target):
                self.assertIn(
                    target,
                    phony,
                    f"help lists target {target!r}, which is not a .PHONY target",
                )

    def test_every_help_variable_is_used(self):
        r"""The help index must not name a variable the Makefile lacks.

        `test_lists_every_tunable_variable` catches a `?=` variable added
        without a help line; this catches the reverse, a help line left
        behind after its variable is removed or renamed, which would send a
        contributor to a variable that no longer tunes anything.
        """
        used = self._used_variables()
        self.assertTrue(used, "Makefile has no variables to check")
        for name in self._help_variables():
            with self.subTest(variable=name):
                self.assertIn(
                    name,
                    used,
                    f"help lists variable {name!r}, which the Makefile never uses",
                )

    def test_lists_every_tunable_variable(self):
        r"""Every `?=` variable appears in the help index, empty default or not.

        `test_names_every_tunable_variable_default` skips a `?=` variable with
        an empty default (`CHECK_TESTS`), so without this a help line removed
        for one would go unnoticed.
        """
        listed = set(self._help_variables())
        names = [name for name, _ in self._question_variables()]
        self.assertTrue(names, "Makefile has no `?=` variables to check")
        for name in names:
            with self.subTest(variable=name):
                self.assertIn(
                    name, listed, f"help does not list variable {name!r}"
                )

    def test_readme_names_every_public_target(self):
        r"""README is the entry point, so it must name every public target.

        `make help` is only discoverable if a contributor already knows it
        exists, so the README has to mention each target; a target added to
        the Makefile without a README line otherwise stays invisible. The
        `(?![-\w])` guard keeps a shorter target from matching as a prefix of
        a longer one (`check` inside `check-references`).
        """
        text = _read_repo_file("README.md")
        for target in self._public_targets():
            with self.subTest(target=target):
                self.assertRegex(
                    text,
                    rf"make {re.escape(target)}(?![-\w])",
                    f"README does not name target {target!r}",
                )

    def test_names_every_tunable_variable_default(self):
        """Each `?=` variable's help line names the Makefile's own default.

        The help text states a default per variable, and a default changed in
        the Makefile but not the help (or the reverse) would mislead a
        contributor who reads the index. The expected value comes from the
        Makefile, so the two are compared instead of pinning a third copy.
        """
        lines = self._output().splitlines()
        defaults = self._tunable_defaults()
        self.assertTrue(defaults, "Makefile has no `?=` variables to check")
        for name, default in defaults.items():
            with self.subTest(variable=name):
                named = [
                    line
                    for line in lines
                    if line.strip().startswith(f"{name}=")
                ]
                self.assertTrue(named, f"help does not list variable {name!r}")
                self.assertTrue(
                    any(f"(default {default})" in line for line in named),
                    f"help does not name the {name} default {default!r}",
                )


if __name__ == "__main__":
    unittest.main()
