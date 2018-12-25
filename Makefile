PREFIX?=$(DESTDIR)/usr/local
BINDIR?=$(PREFIX)/bin
.PHONY: install
all:
	true
install:
	install -D bin/m $(BINDIR)/m

