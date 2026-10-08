PYTHON ?= python3
XDG_DATA_HOME ?= $(HOME)/.local/share

COLOR_SCHEME := theme/color-schemes/MacOS8.6.colors
INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/color-schemes

.PHONY: check check-references install

check:
	$(PYTHON) -m unittest discover -s tests -v

# Opt-in: the repository check needs materialized Git LFS images, so it stays
# out of `check`. The deterministic self-test runs first and fails fast.
check-references:
	$(PYTHON) tools/check_references.py --self-test
	$(PYTHON) tools/check_references.py

install:
	install -Dm644 $(COLOR_SCHEME) $(INSTALL_DIR)/MacOS8.6.colors
