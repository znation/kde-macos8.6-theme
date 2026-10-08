"""Shared `kpackagetool6` validity check for the two theme packages.

The look-and-feel and desktop-theme suites both ask `kpackagetool6` to install
their package into a fresh temporary data directory and assert that the
package's `metadata.json` lands under its id. The two invocations differ only
in the `kpackagetool6` package type and the source/id of the package, so each
suite subclasses `KPackageInstallCase`, sets `KPACKAGETOOL_TYPE`,
`PACKAGE_DIR` and `PACKAGE_ID`, and inherits the check once.
"""

import os
import tempfile

from theme_install import run


class KPackageInstallCase:
    """Mixin: `kpackagetool6 -i` accepts and installs one package.

    Subclasses set `KPACKAGETOOL_TYPE` (`Plasma/LookAndFeel` or `Plasma/Theme`),
    `PACKAGE_DIR` (the source package directory) and `PACKAGE_ID` (the id the
    installed package lands under). It is a plain mixin, not a `TestCase`, so
    importing it does not collect the unconfigured base.
    """

    KPACKAGETOOL_TYPE = None
    PACKAGE_DIR = None
    PACKAGE_ID = None

    def test_kpackagetool6_installs_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(
                [
                    "kpackagetool6",
                    "-t",
                    self.KPACKAGETOOL_TYPE,
                    "-p",
                    tmp,
                    "-i",
                    self.PACKAGE_DIR,
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                os.path.isfile(
                    os.path.join(tmp, self.PACKAGE_ID, "metadata.json")
                )
            )
