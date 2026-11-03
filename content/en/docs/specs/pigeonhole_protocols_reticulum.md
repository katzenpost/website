---
title: ""
linkTitle: "Pigeonhole protocols over Reticulum"
description: ""
author: "David Stainton"
url: ""
date: ""
draft: "false"
slug: "pigeonhole-protocols-reticulum"
layout: ""
type: ""
weight: "999"
version: ""
---

**Abstract**

A client on a Reticulum mesh reads and writes Pigeonhole boxes through one replica it can
reach. This document is what such a client does: how it finds a replica, what it sends and
receives, and how the boxes it handles are made. Every protocol built on boxes, the group chat
among them, sits on what is here. The replicas' own protocol, placement and bridges to a
Katzenpost mixnet are in [Pigeonhole over Reticulum](/docs/specs/reticulum/); the box itself is
BACAP, in the [Echomix paper](https://arxiv.org/abs/2501.02933); the result codes are the
[Pigeonhole specification](/docs/specs/pigeonhole/)'s.


## Replicas

A replica announces a Reticulum destination with application name `pigeonhole` and aspect
`replica`: a single destination whose announce carries one byte of application data, 0, or 1
when the replica is also a bridge to a mixnet. A client collects these announces. For each
destination it keeps the first identity it hears and ignores a later announce of the same
destination under another identity.

A client needs one replica, its entry replica: any announced replica it has a path to, by
preference the one with the fewest hops. It writes to that replica and reads from it, and the
replica does the rest. It stores and forwards what is written, finds what is read wherever on
the mesh it is held, and asks a bridge for a box the mesh does not have. A client does no
placement, and it needs a second replica only when it loses its path to the first.


## Requests

Every query travels as a request on a Link to the replica's destination, to one of two request
paths, `write` or `read`. The query is the request's data and the reply is the response. The
first byte of a query says which it is, and a replica refuses a query that disagrees with the
path it arrived on. A third path, `peek`, is how replicas read from each other; a client does not
use it.

A client keeps one Link per replica and reuses it, sends one request at a time on it, and opens
it again when it closes. A request larger than the Link's MTU travels as a Resource, as any
Reticulum request does. A request that is not answered is not repeated at once: the client asks
again later, as it does for a box that is not yet written. The reference client allows 20
seconds to establish a Link and 60 for a request.


## Boxes

A box is a Box ID, a signature and a ciphertext, and a replica stores it because it verifies,
not because of who brought it. The Box ID is 32 bytes, an Ed25519 public key. The signature is
64 bytes, over the ciphertext, and verifies under the Box ID. How a client gets from a
capability to those three is BACAP, under the context string `pigeonhole context`.

A position in a stream is a MessageBoxIndex of 104 bytes: an 8 byte counter, a 32 byte
blinding factor, a 32 byte encryption key and a 32 byte KDF state. A read capability is the
stream's root public key, 32 bytes, followed by a position: 136 bytes. A write capability is the
root private key, 64 bytes as seed then public key, followed by a position: 168 bytes. The
position a capability carries is its first box, and each next position is derived from the one
before it with the KDF, so whoever holds a capability can compute every later Box ID of the
stream.

For the context string, the position's blinding factor and encryption key are each passed
through the KDF with the string as salt. The Box ID is the root public key blinded by the derived
factor. The ciphertext is AES-GCM-SIV under the derived key, with the first 12 bytes of the Box
ID as nonce and the whole Box ID as associated data. The signature is made with the root private
key blinded by the same factor.

The plaintext is padded before it is encrypted: a 4 byte length, the data, then zeros, to the
box size plus 4 bytes. Every ciphertext is therefore the box size plus 20 bytes, and a replica
refuses one of any other length. The box size is one number for a mesh. Where a bridge joins the
mesh to a mixnet it equals the mixnet's plaintext payload length, since the same box must be
storable on both. A client is told the box size with the mesh it joins.


## Writing, reading and deleting

A client writes a box to its entry replica and is done when the reply says SUCCESS or
ALREADY_EXISTS. Both mean the replica holds a box under that Box ID. A replica stores a Box ID
once: a second write of the same bytes is SUCCESS, a write of different bytes is ALREADY_EXISTS
and changes nothing. A writer refused that way knows the position is taken and goes on to the
next.

A client reads a box by its Box ID. SUCCESS carries the signature and ciphertext, which the
client verifies and opens. NOT_FOUND means not yet: the box a mesh client waits for, the next in
a stream it follows, usually does not exist yet, and the client polls with a backoff. The
reference client starts at 2 seconds and doubles to a minute. Whether the replica found the box
in its own store, on another replica or on the mixnet through a bridge, the client cannot tell
and does not need to.

A tombstone is a write with an empty ciphertext. It replaces the box under that Box ID, a box
never replaces a tombstone, and a read of it answers TOMBSTONE and nothing else. A client that
has seen a tombstone treats the box as deleted from then on, and may answer its own later reads
of that Box ID without asking, since another replica may hold the box until the tombstone
reaches it.


## Epochs

The mesh carries no epoch. A protocol that keeps time in replica epochs, as the group chat does
for retention and backfill, computes the Katzenpost replica epoch itself: seven days each,
counted from 1496275200 in Unix time. Replicas keep boxes for the current and the previous
epoch, and a bridged box falls in the same epoch on both networks.


## Open and closed meshes

On an open mesh the Link is the only encryption around a query, and anyone may announce a
replica. On a closed mesh the same query and reply bytes travel inside the Noise session that
[Pigeonhole over Reticulum](/docs/specs/reticulum/) specifies, to a replica whose key is on the
list the client was given with the mesh. Nothing else in this document changes between the two.


## Encoding

All integers are big endian.

### Queries

A read is 33 bytes:

* one byte, 0,
* the 32 byte Box ID.

A read with anything after the Box ID is refused.

A write is 97 bytes and the ciphertext:

* one byte, 1,
* the 32 byte Box ID,
* the 64 byte signature,
* the ciphertext, to the end of the message. There is no length field.

A tombstone is a write with an empty ciphertext: 97 bytes.

### Replies

* one byte, the result code,
* for SUCCESS to a read that found a box, the 64 byte signature and the ciphertext.

A reply to a write is the one byte. A reply to a read of an unwritten box, or of a tombstone, is
the one byte.

The codes are the Pigeonhole replica's: 0 SUCCESS, 1 NOT_FOUND, 2 INVALID_BOX_ID,
3 INVALID_SIGNATURE, 4 DATABASE_FAILURE, 5 INVALID_PAYLOAD, 6 STORAGE_FULL, 7 INTERNAL_ERROR,
8 INVALID_EPOCH, 9 REPLICATION_FAILED, 10 ALREADY_EXISTS, 11 TOMBSTONE.

### Padding

The plaintext of a box is:

* a 4 byte length,
* the data,
* zeros, to the box size plus 4 bytes.

The ciphertext is that plaintext encrypted, with a 16 byte tag: the box size plus 20 bytes.

### Announce

The application data of a replica's announce is one byte: 0, or 1 for a bridge. On a closed
mesh the replica's hybrid key follows it, as Pigeonhole over Reticulum specifies.

### Vectors

`testdata/bridge_socket_vectors.json` in `pigeonhole_rns` holds query and reply bytes (`queries`,
`replies`), queries a replica refuses (`malformed`) and boxes with what a replica answers each
(`boxes`). The frames in it, a 4 byte length before each message, are the socket between a
bridge's two halves and are not sent by a client.
