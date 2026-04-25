---
title:
linkTitle: "Thin Client API Reference"
description: "Complete API reference for the Katzenpost thin client libraries (Go, Rust, Python)"
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
slug: "/thin_client_api_reference/"
---

# Thin Client API Reference

This is the complete API reference for the Katzenpost thin client. The
thin client is an interface to the kpclientd daemon, which handles all
cryptographic and network operations. The thin client communicates
with the daemon over a local socket using CBOR-encoded messages.

**This document is generated.** The canonical source is
`website/tools/thin-client-api-gen/`; edit binding docstrings (in the
source trees) or `groups.yaml` / `overlay/*.md` (in the generator) — do
not edit this file directly, as local changes will be overwritten by
the next generation pass.

There are three implementations: a Go reference (`katzenpost/client/thin`), a
Rust binding (`thin_client/src`), and a Python binding
(`thin_client/katzenpost_thinclient`).

For pinned versions of the full stack — including `kpclientd`, `katzenqt`, and
the server-side components — see [Build from source](/docs/build_from_source/).

For conceptual background on Pigeonhole, see [Understanding Pigeonhole](/docs/pigeonhole_explained/).
For task-oriented usage guides, see [Thin Client How-to Guide](/docs/thin_client_howto/).

---
