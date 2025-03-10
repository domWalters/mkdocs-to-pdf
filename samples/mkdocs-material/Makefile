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
	$(at)if [ -f $(makefile_dir)/gen/patched ]; then \
	    patch -R $(makefile_dir)/mkdocs-material/mkdocs.yml < $(makefile_dir)/mkdocs-yml.patch; \
	    rm -rf $(makefile_dir)/gen; \
	fi

mkdocs ?= $(abspath $(makefile_dir)/../../.venv/bin/mkdocs)

$(makefile_dir)/gen/patched:
	$(at)mkdir -p $(makefile_dir)/gen
	$(at)patch $(makefile_dir)/mkdocs-material/mkdocs.yml < $(makefile_dir)/mkdocs-yml.patch
	$(at)touch $@

.PHONY: build
build: $(makefile_dir)/gen/patched
	$(at)if [ ! -f $(mkdocs) ]; then \
		echo "$(mkdocs) is not available"; \
		exit 2; \
	fi;
	$(at)cd $(makefile_dir)/mkdocs-material && $(mkdocs) build
