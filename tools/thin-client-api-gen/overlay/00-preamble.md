---
title:
linkTitle: "Thin Client API Reference"
description: "Complete API reference for the Katzenpost thin client libraries (Go, Rust, Python)"
categories: [""]
tags: [""]
author: []
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

There are three implementations:

| Language | Source | Release candidate |
|----------|--------|-------------------|
| Go (reference) | [katzenpost/client/thin](https://github.com/katzenpost/katzenpost/tree/main/client/thin) | `v0.0.73-rc3` |
| Rust | [thin_client/src](https://github.com/katzenpost/thin_client/tree/main/src) | `0.0.12-rc3` |
| Python | [thin_client/katzenpost_thinclient](https://github.com/katzenpost/thin_client/tree/main/katzenpost_thinclient) | `0.0.12-rc3` |

For conceptual background on Pigeonhole, see [Understanding Pigeonhole](/docs/pigeonhole_explained/).
For task-oriented usage guides, see [Thin Client How-to Guide](/docs/thin_client_howto/).

---
