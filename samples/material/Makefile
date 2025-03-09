at ?= @
makefile_dir := $(realpath $(patsubst %/,%,$(dir $(firstword $(MAKEFILE_LIST)))))

.PHONY: help
help:
	@echo "Usage:"
	@echo "  build      : build a PDF"
	@echo "  clean      : delete the site directory"
	@echo "  distclean  : return to factory settings"
	@echo "  help       : show this message"

.PHONY: clean
clean:
	$(at)find $(makefile_dir) -type d -name "site" -exec rm -rf {} +

.PHONY: distclean
distclean: clean

mkdocs ?= $(abspath $(makefile_dir)/../../.venv/bin/mkdocs)

samples ?= $(notdir $(shell find $(makefile_dir) -mindepth 1 -maxdepth 1 -type d ! -path "*/\.*"))

.PHONY: build
build:
	$(at)if [ ! -f "$(mkdocs)" ]; then \
		echo "$(mkdocs) is not available"; \
		exit 2; \
	fi;
	$(at)find "$(makefile_dir)" -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 -I {} sh -c " \
		cd {} && "$(mkdocs)" build; \
	"
