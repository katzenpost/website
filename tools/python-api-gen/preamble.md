---
title:
linkTitle: "Python Thin Client API"
description: "Generated API reference for the Katzenpost Python thin client (katzenpost_thinclient)"
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
slug: "/python_thin_client_api/"
url: "docs/python_thin_client_api/"
---

# Python Thin Client API

This is the API reference for the `katzenpost_thinclient` Python
package, the Python binding of the Katzenpost thin client. The thin
client is an interface to the `kpclientd` daemon, which performs all
cryptographic and network operations; the binding itself does no
cryptography.

**This page is generated** by `website/tools/python-api-gen/` from the
docstrings of the pinned `katzenpost_thinclient` release, using the
native Python documentation tool [`pydoc-markdown`](https://niklasrosenstein.github.io/pydoc-markdown/).
Do not edit it directly: changes belong in the binding docstrings (in
the `thin_client` repository) and will be overwritten by the next
generation pass.

This page documents the **@THINCLIENT_TAG@** release of the Python
binding ([source](https://github.com/katzenpost/thin_client/tree/@THINCLIENT_TAG@/katzenpost_thinclient),
[PyPI](https://pypi.org/project/katzenpost_thinclient/)). Symbols are
re-exported from `katzenpost_thinclient`, so application code may
import them directly, for example `from katzenpost_thinclient import
ThinClient, Config`.

For the curated cross-language reference covering the Go, Rust, and
Python bindings side by side, see the
[Thin Client API Reference](/docs/thin_client_api_reference/). For
conceptual background see [Understanding Pigeonhole](/docs/pigeonhole_explained/),
and for task-oriented guidance see the
[Thin Client How-to Guide](/docs/thin_client_howto/).

---
