# Katzenpost Website

Source for [katzenpost.network](https://katzenpost.network): the
documentation, specifications and blog of the
[Katzenpost](https://github.com/katzenpost) mixnet. This README is for
people who edit those pages. The software itself lives in the other
repositories of the organisation.

The site is built with [Hugo](https://gohugo.io/) and the
[Docsy](https://www.docsy.dev/) theme.

## Local preview

Prerequisites: Node.js (>= 22) and a Go toolchain (Hugo fetches the
Docsy theme as a Hugo module on first build).

```bash
npm ci
npx hugo server
```

Then browse <http://localhost:1313/>. Add `--bind 0.0.0.0` when
browsing from a different machine. `npx hugo` writes a full build to
`public/`.

`npm ci` installs the pinned `hugo-extended` (0.139) and the PostCSS
toolchain into `node_modules`, so no system Hugo is needed; a build
without it fails with "You need to install PostCSS". Do not use
`npm run serve` or `npm run build`: those scripts are inherited from
upstream Docsy and reference a `userguide` directory this repository
does not have.

CI renders every pull request in the container defined by
`Dockerfile` (see `.github/workflows/docs-render.yml`). To reproduce
it with podman or docker:

```bash
podman build -t katzenpost-website-render:local .
podman run --rm -v "$PWD:/site" -w /site katzenpost-website-render:local \
  sh -euc 'npm ci --no-audit --no-fund && hugo --gc --minify'
```

## Map

- `content/en/docs/specs/`: protocol specifications
- `content/en/docs/admin_guide/`: the mix network operator guide
- `content/en/docs/misc/`: how-tos, the threat model and the thin client API references
- `content/en/blog/`: blog posts
- `source/`: LaTeX and DocBook sources for some of the published documents
- `layouts/`, `assets/`, `static/`: templates, styles and static files
- `tools/thin-client-api-gen/`, `tools/python-api-gen/`: API reference generators

## Generated pages

Two pages are machine-generated and must not be edited directly:
`content/en/docs/misc/thin_client_api_reference.md` (from
[`tools/thin-client-api-gen/`](tools/thin-client-api-gen/README.md))
and `content/en/docs/misc/python_thin_client_api.md` (from
[`tools/python-api-gen/`](tools/python-api-gen/README.md)). Edit the
binding docstrings, `groups.yaml` or the `overlay/` fragments instead,
then regenerate as each generator's README describes.

## Contributing

Open a pull request against `main`; the render check must pass.
This repository has no licence file yet.
