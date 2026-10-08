PYTHON ?= python3
XDG_DATA_HOME ?= $(HOME)/.local/share

COLOR_SCHEME := theme/color-schemes/MacOS8.colors
INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/color-schemes

LNF_ID := org.macos8.desktop
LNF_PACKAGE := theme/look-and-feel/$(LNF_ID)
LNF_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/look-and-feel

.PHONY: check check-references install

check:
	$(PYTHON) -m unittest discover -s tests -v

# Opt-in: the repository check needs materialized Git LFS images, so it stays
# out of `check`. The deterministic self-test runs first and fails fast.
check-references:
	$(PYTHON) tools/check_references.py --self-test
	$(PYTHON) tools/check_references.py

install:
	install -Dm644 $(COLOR_SCHEME) $(INSTALL_DIR)/MacOS8.colors
	install -d $(LNF_INSTALL_DIR)
# Replace the package rather than merging: `cp -r` would leave files that were
# deleted from $(LNF_PACKAGE) behind, so a reinstall could keep loading stale QML.
	rm -rf $(LNF_INSTALL_DIR)/$(LNF_ID)
	cp -r $(LNF_PACKAGE) $(LNF_INSTALL_DIR)/
