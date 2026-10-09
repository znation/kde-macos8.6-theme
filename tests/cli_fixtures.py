"""Run a tools/ CLI's ``main`` in-process and capture its output.

The tool CLIs parse arguments with argparse, which exits through ``SystemExit``
for ``--help`` (0) and for a usage error (2), while ``main`` returns its status
otherwise. Tests that read only the exit status and printed diagnostics call
``main`` in-process instead of spawning ``python3 tools/<tool>.py``, exercising
the same parsing, output and statuses without paying interpreter startup and
module import per assertion. The script entry point itself stays covered once
per CLI by a ``test_script_entry_point``.
"""

import contextlib
import io
import subprocess


def run_main(main, program, args):
    """Call *main* with *args* and capture stdout/stderr as a CompletedProcess.

    *program* names the tool in the returned process's ``args``, so a failure
    message reads like the ``python3 tools/<program>.py`` invocation. A
    ``SystemExit`` becomes the process return code, as the script wrapper's
    ``sys.exit`` would report it: ``None`` is 0 and a non-int code is 1.
    """
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            returncode = main(list(args))
        except SystemExit as exc:
            returncode = 0 if exc.code is None else exc.code
            if not isinstance(returncode, int):
                returncode = 1
    return subprocess.CompletedProcess(
        [program, *args], returncode, stdout.getvalue(), stderr.getvalue()
    )
