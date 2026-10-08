PYTHON ?= python3
XDG_DATA_HOME ?= $(HOME)/.local/share

COLOR_SCHEME := theme/color-schemes/MacOS8.6.colors
INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/color-schemes

.PHONY: check install

check:
	$(PYTHON) -m unittest discover -s tests -v

install:
	install -Dm644 $(COLOR_SCHEME) $(INSTALL_DIR)/MacOS8.6.colors
