---
title: ""
linkTitle: "Thin client"
description: ""
author: ""
url: ""
date: "2026-05-21T18:40:45.12443777-07:00"
draft: "false"
slug: "thin_client"
layout: ""
type: ""
weight: "60"
version: ""
---

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="thin_client"></span>Thin client specification

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">David</span> <span class="surname">Stainton</span>

</div>

</div>

</div>

<div>

<div class="abstract">

**Abstract**

This document describes the design of the new Katzenpost mixnet <span class="emphasis">*thin
client*</span>. In particular we discuss its multiplexing and privilege-separation design
elements as well as the protocol used by the thin-client library.

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="thin_client_intro"></span>Introduction

</div>

</div>

</div>

A Katzenpost mixnet client has several responsibilities at a minimum:

<div class="itemizedlist">

- composing Sphinx packets

- decrypting SURB replies

- sending and receiving Noise protocol messages

- keeping up to date with the latest PKI document

</div>

The thin-client library enables applications to talk with the connector daemon and
in that
way interact with the mix network. The library itself does not do any mixnet-related
cryptography since that is already handled by the thin-client daemon. In particular,
the
daemon strips cryptographic signatures from the PKI document before passing data to
clients
using the connector library. Noise- and Sphinx-related cryptography are also handled
by the
daemon.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="library_daemon"></span>Thin-client library and daemon protocol

</div>

</div>

</div>

The thin-client daemon protocol uses a local network socket, either a Unix domain
socket
or TCP.

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="messages"></span>Messages

</div>

</div>

</div>

There are two protocol message types, both CBOR encoded.

<div class="itemizedlist">

- The client sends `Request` messages.

- The daemon sends `Response` messages.

</div>

Messages are length-prefixed CBOR blobs, that is, a blob is prefixed with a big-endian
unsigned four-byte integer (uint32) that encodes the blob length.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="protocol"></span>Protocol description

</div>

</div>

</div>

The protocol has two phases.

<span class="bold">**Phase 1**</span>

Upon connecting to the daemon socket, the thin client waits for two messages.

<div class="itemizedlist">

- <span class="bold">**First message** </span>

  <div class="itemizedlist">

  - The `is_status` field must be set to <span class="strong">**true**</span>

  - The `is_connected` field must indicate whether or not the daemon has
    a mixnet PQ Noise protocol connection to a mixnet gateway node.

  </div>

</div>

<div class="itemizedlist">

- <span class="bold">**Second message**</span>

  <div class="itemizedlist">

  - The message contains the PKI document in its `payload`field. This
    marks the end of the initial connection sequence.

  - The PKI document is stripped of cryptographic signatures as noted above.

  </div>

</div>

<span class="bold">**Phase 2**</span>

<div class="itemizedlist">

- The thin client may send `Request` messages to the daemon, which
  encapsulates the provided payload in a Sphinx packet and sends it to the gateway node.

- The daemon may send `Response` messages to the client at any time during
  this phase. `Response` messages may communicate a connection status change, a
  new PKI document, or a message-sent or message-reply event.

</div>

</div>

</div>

</div>
