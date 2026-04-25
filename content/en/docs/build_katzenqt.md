---
title:
linkTitle: "Build and run katzenqt from source"
description: "How to build and run katzenqt, the Qt group chat client, from source on Debian or Ubuntu"
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
slug: "/build_katzenqt/"
body_class: "td-style-dashes"
---

# Build and run katzenqt from source

`katzenqt` is the Qt group chat client. It is a decentralised
application that runs over the Katzenpost mix network and the
Pigeonhole storage services. The design is set out in the
[Echomix paper](https://arxiv.org/abs/2501.02933).

> **Warning.** `katzenqt` is in active development and has not yet
> been tagged for general release. It is not appropriate to rely on
> the software for anonymity, security, or privacy at this stage.
> Pre-built packages will be linked from the [docs landing](/docs/)
> once a release is cut.

## Prerequisites

These instructions assume an up-to-date Debian or Ubuntu Linux system
with the following packages installed:

```shell
sudo apt install -y git make libxcb-cursor0 libegl1
```

The `Makefile` does the rest: it provisions a Python virtual
environment via [`uv`](https://github.com/astral-sh/uv), builds
`kpclientd`, installs it as a systemd user service, and launches the
GUI.

## Quick start

```shell
git clone https://github.com/katzenpost/katzenqt
cd katzenqt
make deps
make run
```

If `make run` opens the `katzenqt` window, you are ready.

## Step by step (if the quick start fails)

If the two-command form does not yield a running interface, the
following sequence runs each phase of the setup independently and is
useful for diagnosing where things have gone awry:

```shell
make system-setup       # apt-installs the system dependencies
make setup-uv           # bootstraps the uv-managed venv
make setup              # installs Python dependencies into the venv
make test               # runs the test suite
make kpclientd          # builds the kpclientd binary
make install-kpclient   # installs kpclientd into ~/.local/bin
make kpclientd.service  # installs the systemd user unit
make status             # verifies the install
```

A successful `make status` produces something like the following:

```
backend: uv
venv: .venv
kpclientd(bin): /home/<user>/.local/bin/kpclientd
kpclientd(service): active
kpclientd(path): found
```

Once that is the case, `make run` should bring up the application.

## Persistent state

`katzenqt` keeps all of its persistent data (keys, conversation logs,
BACAP capabilities, message indices) in a single SQLite file at
`~/.local/share/katzenqt/katzen.sqlite3`. The environment variable
`KQT_STATE` overrides the file name, which is useful when running two
instances on the same machine (one talking to the other):

```shell
KQT_STATE=alice make run    # uses ~/.local/share/katzenqt/alice.sqlite3
```

## Current caveats

- `katzenqt` is currently developed against a debug branch of the
  `katzenpost` repository (`tb/debug2025-09-21`) rather than the
  pinned release tag listed on [Build from source](/docs/build_from_source/).
  This will be reconciled when a `katzenqt` tag is cut.
- A tag has not yet been published.

## See also

- [Build from source](/docs/build_from_source/): pinned versions of
  the rest of the Katzenpost stack.
- [Understanding Pigeonhole](/docs/pigeonhole_explained/): the
  storage primitive that `katzenqt` uses.
- The [katzenqt repository](https://github.com/katzenpost/katzenqt):
  for issues, pull requests, and the latest `README.md` / `HACKING.md`.
