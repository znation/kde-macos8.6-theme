"""Tests for tools/apply_konsole_font.py.

The helper runs `kreadconfig6` and `kwriteconfig6` against stub scripts on a
narrowed `PATH`: the reader answers from a fixture INI file, and the writer
edits its target file with KConfig's replace-or-append semantics, so the
text each apply leaves behind can be asserted line for line. The helper is
called directly with a scratch XDG home -- its caller and its place in the
apply sequence are `tests/test_apply_theme.py`'s subject -- and the refusal
cases assert the raised diagnostic and that nothing was written.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import apply_konsole_font
from tools.apply_theme import FIXED_VALUE as FONT


class KonsoleError(Exception):
    """The refusal class the tests pass to the helper, as apply_theme does."""


# The shell, keyboard and interaction keys an unrelated profile edit must
# keep: a profile font write that touched them would rewrite the user's
# terminal setup, not just its face.
FOREIGN_PROFILE = """\
[General]
Name=Mine
Parent=FALLBACK/
Command=/bin/bash
KeyTab=default.keys

[Appearance]
Font=Liberation Mono,10,-1,5,400,0,0,0,0,0

[InteractionOptions]
TrimLeftSpaces=false
"""


class StubKonsoleTools(unittest.TestCase):
    """Base running the helper against stub `kreadconfig6`/`kwriteconfig6`.

    `PATH` is narrowed to the stub directory, so a host Konsole tool cannot
    answer instead. The stubs are python scripts: the reader prints the last
    value a group/key holds (KConfig's own last-wins rule), the writer
    replaces that key inside its group or appends it, so repeated applies
    exercise real replace semantics rather than a recording no-op.
    """

    WRITER = """\
#!/usr/bin/env python3
import sys
args = sys.argv[1:]

def arg(flag, offset=1):
    return args[args.index(flag) + offset]

path = arg("--file")
group = arg("--group")
key = arg("--key")
value = arg("--key", 2)
try:
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
except FileNotFoundError:
    lines = []
start = None
for index, line in enumerate(lines):
    if line.strip() == "[" + group + "]":
        start = index
        break
if start is None:
    lines.extend(["", "[" + group + "]", key + "=" + value])
else:
    end = len(lines)
    for index in range(start + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            end = index
            break
    hit = None
    for index in range(start + 1, end):
        if lines[index].split("=", 1)[0].strip() == key:
            hit = index
    if hit is None:
        lines.insert(end, key + "=" + value)
    else:
        lines[hit] = key + "=" + value
with open(path, "w", encoding="utf-8") as handle:
    handle.write("\\n".join(lines) + "\\n")
"""

    READER = """\
#!/usr/bin/env python3
import sys
args = sys.argv[1:]

def arg(flag, offset=1):
    return args[args.index(flag) + offset]

path = arg("--file")
group = arg("--group")
key = arg("--key")
value = arg("--default") if "--default" in args else ""
try:
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
except FileNotFoundError:
    lines = []
current = None
for line in lines:
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        current = stripped[1:-1]
    elif current == group and "=" in stripped:
        name, _, raw = stripped.partition("=")
        if name.strip() == key:
            value = raw.strip()
print(value)
"""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="apply-konsole-font-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        self.data = self.root / "data"
        self.data.mkdir()
        self.system = self.root / "system"
        self.konsolerc = self.home / ".config" / "konsolerc"
        self.profile_dir = self.data / "konsole"
        self.writer = self.bin / "kwriteconfig6"
        self._write_stub(self.writer, self.WRITER)
        self._write_stub(self.bin / "kreadconfig6", self.READER)

    def _write_stub(self, path, body):
        # The stub PATH holds no interpreter directory, so the python
        # stubs are pinned to the running interpreter's own absolute path
        # instead of an `env` lookup the narrowed PATH cannot answer.
        body = body.replace("#!/usr/bin/env python3", f"#!{sys.executable}", 1)
        path.write_text(body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def env(self):
        return {
            "PATH": str(self.bin),
            "HOME": str(self.home),
            "XDG_DATA_HOME": str(self.data),
            "XDG_DATA_DIRS": str(self.system),
        }

    def env_without_homes(self):
        return {"PATH": str(self.bin), "XDG_DATA_HOME": str(self.data)}

    def write_konsolerc(self, text):
        self.konsolerc.parent.mkdir(parents=True, exist_ok=True)
        self.konsolerc.write_text(text, encoding="utf-8")

    def write_profile(self, directory, name, text):
        target = directory / "konsole" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def read(self, path):
        return path.read_text(encoding="utf-8")

    def apply_font(self, font=FONT, env=None):
        """Run the helper, returning (status, stderr) with stderr captured."""
        scratch = self.root / "scratch"
        scratch.mkdir(exist_ok=True)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = apply_konsole_font.apply(
                scratch,
                dict(self.env() if env is None else env),
                self.data,
                font,
                KonsoleError,
                60.0,
            )
        return status, stderr.getvalue()

    def without_font_lines(self, text):
        """Drop every Font entry, so a font-only rewrite compares clean."""
        return [
            line for line in text.splitlines() if not line.startswith("Font=")
        ]

    def fail_stub(self, name, status):
        """Make *name* exit with *status* after printing a marker to stderr."""
        self._write_stub(
            self.bin / name,
            f"#!/bin/sh\necho exploded >&2\nexit {status}\n",
        )


class TestUserDefault(StubKonsoleTools):
    def setUp(self):
        super().setUp()
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        self.profile = self.write_profile(self.data, "Mine.profile", FOREIGN_PROFILE)

    def test_a_user_default_profile_gets_the_font(self):
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        text = self.read(self.profile)
        self.assertIn(f"Font={FONT}\n", text)
        self.assertNotIn("Liberation Mono", text)

    def test_only_the_font_entry_changes(self):
        # Every other key -- the profile name, its shell command, its key
        # tab (Konsole's keyboard mapping) and its interaction options --
        # must survive a font apply untouched, in place.
        before = self.without_font_lines(self.read(self.profile))
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(
            before, self.without_font_lines(self.read(self.profile))
        )

    def test_konsolerc_is_untouched(self):
        before = self.read(self.konsolerc)
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(before, self.read(self.konsolerc))

    def test_a_repeat_apply_leaves_the_profile_the_same(self):
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        once = self.read(self.profile)
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(once, self.read(self.profile))


class TestSystemDefault(StubKonsoleTools):
    def setUp(self):
        super().setUp()
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        self.system_profile = self.write_profile(
            self.system, "Mine.profile", FOREIGN_PROFILE
        )
        self.local_profile = self.profile_dir / "Mine.profile"

    def test_a_system_default_profile_is_copied_then_edited(self):
        before = self.system_profile.read_bytes()
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(before, self.system_profile.read_bytes())
        self.assertEqual(
            self.without_font_lines(FOREIGN_PROFILE),
            self.without_font_lines(self.read(self.local_profile)),
        )
        self.assertIn(f"Font={FONT}\n", self.read(self.local_profile))

    def test_a_data_home_profile_shadows_the_same_named_system_one(self):
        # Konsole reads konsole/ under the data home first, so an existing
        # local profile is the one new sessions load: it is edited in place
        # and no copy may overwrite the user's edits with the system text.
        marker = FOREIGN_PROFILE.replace(
            "[Appearance]", "[General]\nExtra=user edit\n\n[Appearance]", 1
        )
        self.write_profile(self.data, "Mine.profile", marker)
        before = self.system_profile.read_bytes()
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(before, self.system_profile.read_bytes())
        text = self.read(self.local_profile)
        self.assertIn("Extra=user edit\n", text)
        self.assertIn(f"Font={FONT}\n", text)

    def test_a_repeat_apply_keeps_the_earlier_copy(self):
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        copied = self.local_profile.read_bytes()
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(copied, self.local_profile.read_bytes())
        self.assertNotEqual(
            self.system_profile.read_bytes(), self.local_profile.read_bytes()
        )

    def test_other_profiles_are_untouched(self):
        other = self.write_profile(
            self.data, "Other.profile", FOREIGN_PROFILE
        )
        before = other.read_bytes()
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(before, other.read_bytes())


class TestFallback(StubKonsoleTools):
    def test_an_unset_default_creates_and_selects_the_platinum_profile(self):
        self.write_konsolerc("[General]\nColorScheme=BreezeLight\n")
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        profile = self.profile_dir / "Platinum.profile"
        text = self.read(profile)
        self.assertIn("Name=Platinum\n", text)
        self.assertIn("Parent=FALLBACK/\n", text)
        self.assertIn(f"Font={FONT}\n", text)
        self.assertEqual(
            "[General]\nColorScheme=BreezeLight\n\n"
            "[Desktop Entry]\nDefaultProfile=Platinum.profile\n",
            self.read(self.konsolerc),
        )

    def test_a_repeat_apply_rewrites_the_same_keys(self):
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        konsolerc = self.read(self.konsolerc)
        profile = self.read(self.profile_dir / "Platinum.profile")
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(konsolerc, self.read(self.konsolerc))
        self.assertEqual(profile, self.read(self.profile_dir / "Platinum.profile"))
        for key in ("Name", "Parent", "Font"):
            with self.subTest(key=key):
                self.assertEqual(
                    1,
                    sum(
                        1
                        for line in profile.splitlines()
                        if line.startswith(key + "=")
                    ),
                    profile,
                )

    def test_an_explicit_platinum_default_only_writes_the_font(self):
        # Once the fallback profile exists and is selected, the next apply
        # takes the named-profile path: konsolerc keeps naming the profile
        # and only the font entry is rewritten.
        self.apply_font()
        profile = self.profile_dir / "Platinum.profile"
        konsolerc = self.read(self.konsolerc)
        status, stderr = self.apply_font()
        self.assertEqual(None, status, stderr)
        self.assertEqual(konsolerc, self.read(self.konsolerc))
        self.assertIn(f"Font={FONT}\n", self.read(profile))


class TestRefusals(StubKonsoleTools):
    def assert_refused(self, message_part, profile="Mine.profile"):
        """The helper raises, prints nothing, and writes nothing."""
        self.write_konsolerc(f"[Desktop Entry]\nDefaultProfile={profile}\n")
        before = self.read(self.konsolerc)
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font()
        self.assertIn(message_part, str(raised.exception))
        self.assertEqual(before, self.read(self.konsolerc))
        self.assertFalse(self.profile_dir.exists())

    def test_an_absolute_profile_name_is_refused(self):
        self.assert_refused("must be a plain file name", profile="/etc/Own.profile")

    def test_a_traversal_profile_name_is_refused(self):
        self.assert_refused("must be a plain file name", profile="../Own.profile")

    def test_a_separated_profile_name_is_refused(self):
        self.assert_refused("must be a plain file name", profile="sub/Own.profile")

    def test_the_dot_names_are_refused(self):
        for name in (".", ".."):
            with self.subTest(name=name):
                self.assert_refused("must be a plain file name", profile=name)

    def test_an_unresolvable_profile_name_is_refused(self):
        self.assert_refused(
            "does not exist in konsole/", profile="Gone.profile"
        )

    def test_a_symlinked_profile_is_refused(self):
        target = self.root / "real.profile"
        target.write_text("[Appearance]\nFont=Liberation Mono\n", encoding="utf-8")
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        self.profile_dir.mkdir(parents=True)
        self.profile = self.profile_dir / "Mine.profile"
        self.profile.symlink_to(target)
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font()
        self.assertIn("symbolic link", str(raised.exception))
        self.assertEqual(
            "[Appearance]\nFont=Liberation Mono\n", self.read(target)
        )

    def test_a_symlinked_copy_destination_is_refused(self):
        self.write_profile(self.system, "Mine.profile", FOREIGN_PROFILE)
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        target = self.root / "real.profile"
        target.write_text("[General]\nName=Real\n", encoding="utf-8")
        self.profile_dir.mkdir(parents=True)
        (self.profile_dir / "Mine.profile").symlink_to(target)
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font()
        self.assertIn("symbolic link", str(raised.exception))
        self.assertEqual("[General]\nName=Real\n", self.read(target))

    def test_an_unresolvable_config_home_is_refused(self):
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font(env=self.env_without_homes())
        self.assertIn("XDG_CONFIG_HOME", str(raised.exception))
        self.assertIn("HOME", str(raised.exception))


class TestCommandFailures(StubKonsoleTools):
    def setUp(self):
        super().setUp()
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        self.profile = self.write_profile(self.data, "Mine.profile", FOREIGN_PROFILE)

    def test_a_failing_read_exits_1_with_the_tail(self):
        self.fail_stub("kreadconfig6", 4)
        status, stderr = self.apply_font()
        self.assertEqual(1, status)
        self.assertIn("kreadconfig6 exited 4", stderr)
        self.assertIn("exploded", stderr)

    def test_a_failing_font_write_exits_1_and_writes_nothing(self):
        self.fail_stub("kwriteconfig6", 6)
        before = self.profile.read_bytes()
        status, stderr = self.apply_font()
        self.assertEqual(1, status)
        self.assertIn("kwriteconfig6 exited 6", stderr)
        self.assertEqual(before, self.profile.read_bytes())

    def test_an_unrunnable_writer_exits_2_without_a_traceback(self):
        self.writer.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        self.writer.chmod(self.writer.stat().st_mode | stat.S_IXUSR)
        status, stderr = self.apply_font()
        self.assertEqual(2, status)
        self.assertIn("cannot run kwriteconfig6", stderr)
        self.assertIn("apply_theme: error:", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_a_failing_fallback_write_stops_before_the_selection(self):
        # The fallback branch writes the profile before it selects it, so a
        # failed profile write must leave konsolerc without a selection.
        self.write_stub_body(
            "kwriteconfig6",
            'case "$*" in *--key\\ Name*) echo profile write failed >&2\n'
            "exit 7;; esac\nexit 0",
        )
        self.write_konsolerc("[General]\nColorScheme=BreezeLight\n")
        before = self.read(self.konsolerc)
        status, stderr = self.apply_font()
        self.assertEqual(1, status)
        self.assertIn("kwriteconfig6 exited 7", stderr)
        self.assertEqual(before, self.read(self.konsolerc))

    def write_stub_body(self, name, body):
        self._write_stub(self.bin / name, f"#!/bin/sh\n{body}\n")


if __name__ == "__main__":
    unittest.main()
