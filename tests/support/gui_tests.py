"""Guard GTK probes that present windows on the host display."""

import os
import unittest


def require_gui_opt_in():
    if os.environ.get("PLATINUM_RUN_GUI_TESTS") != "1":
        raise unittest.SkipTest(
            "set PLATINUM_RUN_GUI_TESTS=1 to run visible GTK probes"
        )
