# Render container for the Katzenpost website.
# The host needs make, podman and git. Nothing else.
#
# hugo-extended arrives through npm, because package.json pins it and the
# site's SCSS pipeline needs the extended build. Go is here for the Hugo
# module that pulls docsy. Node runs postcss. Python runs the text checks.

FROM docker.io/library/golang:1.23-bookworm AS go

FROM docker.io/library/node:22-bookworm

COPY --from=go /usr/local/go /usr/local/go

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates git python3 \
 && rm -rf /var/lib/apt/lists/*

ENV PATH=/usr/local/go/bin:/site/node_modules/.bin:$PATH \
    GOPATH=/cache/go \
    GOCACHE=/cache/gocache \
    GOFLAGS=-mod=mod \
    HUGO_CACHEDIR=/cache/hugo \
    npm_config_cache=/cache/npm \
    HOME=/tmp \
    DOCSY_MKDIR_HUGO_MOD_SKIP=1
# The site uses Hugo modules, so docsy's npm postinstall has no reason to
# create empty stub directories beside the checkout. Skipping it also keeps
# the container from writing outside the bind mount.

RUN git config --system --add safe.directory /site

WORKDIR /site
