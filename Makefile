PREFIX?=$(DESTDIR)/usr/local
BINDIR?=$(PREFIX)/bin
.PHONY: install
install:
	install -D bin/m $(BINDIR)/m

