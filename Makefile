# Render the site in a container. The host needs make, podman and git.

ENGINE   ?= podman
IMAGE    ?= katzenpost-website-render:local
PORT     ?= 1313
BIND     ?= 127.0.0.1
PREVIEW_URL  ?= http://$(BIND):$(PORT)/
POLL     ?= 700ms
SITE     := $(CURDIR)
OUT      ?= $(SITE)/public
BASEURL  ?= https://katzenpost.network/
PAGE     ?= content/en/docs/specs/dirauth.md

# A named volume keeps node_modules, the Go module cache and the Hugo module
# cache between runs, so only the first render pays for them.
CACHE    := katzenpost-website-cache
NAME     ?= katzenpost-website-serve

# keep-id maps the calling user into the container, so files written into the
# bind mount stay owned by the caller under rootless podman.
RUNFLAGS := -v $(SITE):/site:z -v $(CACHE):/cache -w /site
GIT_COMMON_DIR := $(shell if test -f .git; then git rev-parse --path-format=absolute --git-common-dir; fi)
ifneq ($(GIT_COMMON_DIR),)
RUNFLAGS += -v '$(GIT_COMMON_DIR):$(GIT_COMMON_DIR):ro'
endif
ifeq ($(ENGINE),podman)
RUNFLAGS += --userns=keep-id
endif
RUN       = $(ENGINE) run --rm $(RUNFLAGS)

.PHONY: help image deps render serve serve-bg stop diagrams text check shell clean distclean

help:
	@printf 'make %-10s %s\n' \
	  image    'build the render image' \
	  deps     'install the pinned node packages into the cache volume' \
	  render   'build the site into $$OUT (default ./public)' \
	  serve    'watch and serve the site on $(PREVIEW_URL)' \
	  serve-bg 'the same, detached' \
	  stop     'stop a detached server' \
	  diagrams 'parse every mermaid block in $$PAGE' \
	  text     'ASCII and semicolon checks on $$PAGE' \
	  check    'diagrams, text, then a production render' \
	  shell    'an interactive shell in the image' \
	  clean    'remove the build output' \
	  distclean 'also remove the cache volume and the image'

image:
	$(ENGINE) build -t $(IMAGE) -f Containerfile .

# npm ci installs the pinned hugo-extended and the postcss pipeline. Hugo
# fetches the modules go.mod pins on its own during the build, so nothing
# here runs `hugo mod get`, which would upgrade them and edit go.mod.
deps: image
	$(RUN) $(IMAGE) npm ci --no-audit --no-fund

render: deps
	$(RUN) $(IMAGE) hugo --gc --minify --baseURL '$(BASEURL)' --destination '$(patsubst $(SITE)/%,/site/%,$(OUT))'
	@echo "rendered into $(OUT)"

serve: deps
	@echo "$(PREVIEW_URL)docs/specs/dirauth/"
	$(ENGINE) run --rm $(RUNFLAGS) -p '$(BIND):$(PORT):$(PORT)' -it $(IMAGE) \
	  hugo server --bind 0.0.0.0 --port $(PORT) --baseURL '$(PREVIEW_URL)' --disableFastRender --cleanDestinationDir --poll $(POLL)

serve-bg: deps
	-$(ENGINE) rm -f $(NAME) >/dev/null 2>&1 || true
	$(ENGINE) run -d --name $(NAME) $(RUNFLAGS) -p '$(BIND):$(PORT):$(PORT)' $(IMAGE) \
	  hugo server --bind 0.0.0.0 --port $(PORT) --baseURL '$(PREVIEW_URL)' --disableFastRender --cleanDestinationDir --poll $(POLL)
	@echo "$(PREVIEW_URL)docs/specs/dirauth/"

stop:
	-$(ENGINE) rm -f $(NAME)

diagrams: image
	$(RUN) $(IMAGE) sh -euc '\
	  cd /cache && mkdir -p mmv && cd mmv && \
	  printf "%s" "{\"name\":\"mmv\",\"private\":true,\"type\":\"module\",\"dependencies\":{\"mermaid\":\"12.2.0\",\"jsdom\":\"25.0.1\"}}" > package.json && \
	  npm install --silent --no-audit --no-fund && \
	  cp /site/tools/check-mermaid.mjs . && \
	  node ./check-mermaid.mjs /site/$(PAGE)'

text: image
	$(RUN) $(IMAGE) sh -euc '\
	  n=$$(LC_ALL=C grep -c "[^ -~]" $(PAGE) || true); \
	  echo "non-ASCII bytes: $$n"; [ "$$n" = "0" ]; \
	  python3 /site/tools/prose-only.py $(PAGE) /tmp/prose.md; \
	  s=$$(grep -c ";" /tmp/prose.md || true); \
	  echo "semicolons in prose: $$s"; [ "$$s" = "0" ]'

check: diagrams text render

shell: image
	$(ENGINE) run --rm $(RUNFLAGS) -it $(IMAGE) bash

clean:
	rm -rf $(OUT) resources/_gen

distclean: clean
	-$(ENGINE) volume rm $(CACHE)
	-$(ENGINE) rmi $(IMAGE)
