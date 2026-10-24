"""Shared assertions for a completed child process's exit status.

Many suites run `make install`/`uninstall`, a Plasma CLI or a tool script and
then assert the child exited cleanly (or not) before reading its output. This
names that expectation once::

    assert_succeeded(self, result)   # result.returncode == 0
    assert_failed(self, result)      # result.returncode != 0
    assert_exit_2_without_traceback(self, result)  # refusal, not a crash

*result* is a ``subprocess.CompletedProcess`` with decoded-text
``stdout``/``stderr``: the suites get one from ``theme_install.run_captured``,
``process_runner.run`` or ``subprocess.run(..., text=True)``. Both helpers
attach the child's stdout and stderr to a failure message, so a failing test
shows the diagnostic the child printed rather than only one stream.
``CliTestCase._assert_success`` delegates here; the install/make suites, which
do not subclass ``CliTestCase``, call these functions directly.
"""


def assert_succeeded(case, result):
    """Assert *result* exited 0, attaching its output to a failure."""
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)


def assert_failed(case, result):
    """Assert *result* exited non-zero, attaching its output to a failure."""
    case.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


def assert_exit_2_without_traceback(case, result):
    """Assert *result* is a refusal: exit 2 with no escaped traceback.

    A tool reports refused input with its own diagnostic and status 2; a
    ``Traceback`` on stderr means an unexpected exception escaped instead.
    The local-hook suite uses this for its install and uninstall refusal
    paths, which each append the diagnostic or path they expect.
    """
    assert_failed(case, result)
    case.assertEqual(result.returncode, 2, result.stderr)
    case.assertNotIn("Traceback", result.stderr)
