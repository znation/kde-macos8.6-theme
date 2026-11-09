"""The Makefile's control-byte list is evaluated once per make run.

The parse-time value guards refuse a DESTDIR / XDG_DATA_HOME / FLOCK_TIMEOUT
value carrying a C0 or DEL byte. The list of bytes they search for is a
constant built by one awk program: make spawns awk for it through
``$(shell ...)`` once, remembers the result, and every later guard evaluation
reuses it. A recursive evaluation would instead re-run that shell spawn for
each guarded value, paying one process spawn per guard call on every make
invocation; this test pins the one-spawn shape by counting awk invocations
through a PATH shadow that records each run.

``test_make_refusals`` pins the refusals these guards report; this module
only pins the spawn count.
"""

from __future__ import annotations

import shutil
import unittest

from support import theme_install
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir

# The real awk the shadow delegates to, resolved before PATH changes.
_REAL_AWK = shutil.which("awk")


@unittest.skipUnless(_REAL_AWK, "needs awk on PATH to resolve the real tool")
class TestControlCharsListIsEvaluatedOnce(unittest.TestCase):
    """One make run evaluates the guard's byte list one time.

    The list is a constant, so the shadow's log must carry one line: a
    recursive evaluation would instead re-spawn awk for every guarded value
    during the parse-time guard run of ``make -n install``, which evaluates
    the guards but runs no recipe.
    """

    def test_make_spawns_awk_once_for_the_guard_byte_list(self) -> None:
        destdir = make_tmp_dir(self)
        log = destdir / "awk.log"
        env = theme_install.shadow_command_env(
            str(destdir),
            "awk",
            "#!/bin/sh\n"
            'printf "x\\n" >> "%s"\n'
            'exec "%s" "$@"\n' % (log, _REAL_AWK),
        )
        result = theme_install.run_make(
            ["-n", "install", f"DESTDIR={destdir}"], env=env
        )
        assert_succeeded(self, result)
        self.assertEqual(log.read_text().count("\n"), 1)


if __name__ == "__main__":
    unittest.main()
