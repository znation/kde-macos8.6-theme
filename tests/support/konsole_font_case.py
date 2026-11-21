"""Shared test base for the Konsole font and refusal suites.

This module name does not match ``test*.py``, so test discovery never collects it.
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
from support.theme_install import write_file
from tools import apply_konsole_font
from tools.apply_theme import FIXED_VALUE as FONT

class KonsoleError(Exception):
    """The refusal class the tests pass to the helper, as apply_theme does."""

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


class StubKonsoleToolsTestCase(unittest.TestCase):
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
        write_file(self.konsolerc, text)

    def write_profile(self, directory, name, text):
        target = directory / "konsole" / name
        write_file(target, text)
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
