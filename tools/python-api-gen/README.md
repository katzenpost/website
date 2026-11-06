# Python Thin Client API Page Generator

Generates `content/en/docs/misc/python_thin_client_api.md` from the
docstrings of the pinned `katzenpost_thinclient` release, using the
native Python documentation tool `pydoc-markdown`.

This is deliberately separate from `thin-client-api-gen`. That tool
produces the curated *cross-language* reference (Go, Rust, Python) via
its own AST extractors. This tool produces only the standalone Python
API page and defers entirely to Python's own tooling for it.

## How it works

1. `pinned-versions.env` pins the `thin_client` tag and checkout path
   (`?=`, so environment / `make VAR=value` overrides win).
2. `generate.py` exports that tag's `katzenpost_thinclient` subtree
   with `git archive`. The working checkout is never touched, so this
   runs regardless of which branch the checkout sits on.
3. `pydoc-markdown.yml` (the real, wired configuration) is rendered
   over the export. `@SRC@` is substituted with the export path.
4. The Docsy front matter and intro from `preamble.md` are prepended
   and the page is written into `content/`. The existing Hugo Pages
   workflow then publishes it to `https://katzenpost.network/`.

## Usage

```sh
make build                          # generate the page (pinned tag)
make build THINCLIENT_TAG=0.0.16    # override the pinned tag
make check-tag                      # verify the tag resolves
make venv-refresh                   # rebuild the venv
make clean                          # remove build/ and .venv/
```

## Prerequisites

* Python 3.9+ with `venv`. `pydoc-markdown` and `PyYAML` are installed
  into a local `.venv/` by the `Makefile`; the system Python is not
  touched.
* A local `thin_client` git checkout containing the pinned tag (any
  branch; the tag merely has to resolve).

## Files

```
.
├── Makefile
├── pinned-versions.env   # pinned tag + checkout path
├── requirements.txt      # pydoc-markdown, PyYAML
├── pydoc-markdown.yml    # native pydoc-markdown config (@SRC@ templated)
├── preamble.md           # Docsy front matter + intro (@THINCLIENT_TAG@ templated)
├── generate.py           # export, render, stitch, write
└── README.md
```
