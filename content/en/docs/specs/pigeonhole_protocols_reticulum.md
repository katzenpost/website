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

## Pigeonhole protocols over Reticulum

A client on a Reticulum mesh reads and writes Pigeonhole boxes through one replica. This is
what it sends and receives. Replicas, replication and bridges are in
[Pigeonhole replicas over Reticulum](/docs/specs/reticulum/); BACAP is in the
[Echomix paper](https://arxiv.org/abs/2501.02933); a protocol on top, such as
[katzenqt1 chat](/docs/specs/katzenqt1-reticulum/), adds only what it writes into boxes.


## Replicas

|                           |                                                                        |
|---------------------------|------------------------------------------------------------------------|
| destination               | application name `pigeonhole`, aspect `replica`, single                |
| announce application data | 1 byte of flags, under Encoding; a bridge's 16 byte mixnet id after it |
| identity                  | the first heard for a destination; a later one for it is ignored       |
| entry replica             | any announced replica with a path, the fewest hops by preference       |

A client uses one replica at a time. The mesh runs in open mode: every replica holds every box,
and the replica forwards, syncs and finds boxes, and fetches from the mixnet through a bridge;
the client does none of that. Replicas are authenticated only by Reticulum's classical link
encryption.


## Requests

A query reaches a replica over a Link to its destination, in one of two modes. One Link per
replica, reopened when it closes. Both modes carry the same query and reply bytes.

**Request mode**, every replica not announcing bit 3: the query is a Link request; a request
above the MTU travels as a Resource. Up to 8 queries in flight per Link.

| path    | query       | reply                              |
|---------|-------------|------------------------------------|
| `write` | write query | result code                        |
| `read`  | read query  | result code, and the box when found |

A query whose first byte disagrees with its path is answered INVALID_PAYLOAD. `subscribe` and
`unsubscribe` are under Push; the other paths are replica to replica. Reference timeouts: 20 s
to establish a Link, 60 s per request; an unanswered request is asked again later, not repeated
at once.

**Channel mode**, replicas announcing bit 1: the query goes as Channel messages on the Link,
for Reticulum stacks with Links and Channel but no requests or Resources. A client uses it
only with replicas that announce bit 1, and only it with those announcing bit 3. The
query's first byte picks read, write, subscribe or unsubscribe. A query or reply larger than
one Channel message is cut into pieces, each a frame carrying the query's request id; the reply
comes back with the same request id. A replica drops a request whose pieces do not all arrive
within 60 s. Bytes on the air for one box of 1000 bytes, client sent / received:

| link MTU | query | request mode | channel mode |
|----------|-------|--------------|--------------|
| 500      | write | 1484 / 297   | 1468 / 428   |
| 500      | read  | 329 / 1436   | 480 / 1456   |

Channel mode costs about 100 to 150 bytes more per query, mostly the proof every Channel packet
gets. With the `mesh` box size a write is one packet in either mode.

**Choosing a mode.** The reference clients have a mode setting: request, Channel, or auto, the
default. Auto asks a replica with a Link request first and, when a replica announcing bit 1
does not answer, asks again in Channel mode, and keeps per replica the mode that answered. The
Rust client on Reticulum-rs speaks Channel mode alone. Replicas asking each other go Channel
first, as Pigeonhole replicas over Reticulum describes.


## Push

A client on a replica announcing bit 4 need not poll. After a read answers NOT_FOUND, the
client subscribes to that Box ID on the same Link, in Channel mode, since pushes come only
over Channel. When the replica holds the box it pushes it down the Link, and the client takes
the box from the push with no further query. The client then subscribes to the stream's next
Box ID.

Pushes are best effort, so a stream waiting for a push still reads again every 5 minutes,
which also renews the subscription. A subscription lasts at most an hour, and a Link waits for
at most 256 Box IDs. Against a replica that does not announce push, and on the mixnet, the
client polls with backoff.


## Boxes

BACAP under the context string `pigeonhole context`.

|                                                                              | bytes         |
|------------------------------------------------------------------------------|---------------|
| Box ID: a blinded Ed25519 public key                                         | 32            |
| signature: Ed25519 over the ciphertext, verifying under the Box ID           | 64            |
| MessageBoxIndex: counter 8, blinding factor 32, encryption key 32, KDF state 32 | 104        |
| read capability: root public key, MessageBoxIndex                            | 136           |
| write capability: root private key as seed then public key, MessageBoxIndex  | 168           |
| ciphertext                                                                   | box size + 20 |

For the context string, the index's blinding factor and encryption key each go through
HKDF-BLAKE2b-512 with the string as salt. Box ID = root public key blinded by the derived
factor. Ciphertext = AES-GCM-SIV under the derived key, nonce the first 12 bytes of the Box ID,
the Box ID as associated data. Signature = root private key blinded by the derived factor, over
the ciphertext. A capability's index is its first box; each next index derives from the one
before it.

The box size B is the plaintext a box carries. A replica takes several: always `mesh`, 267
bytes, the largest whose write fits one Reticulum packet at the 500 byte MTU, and `mixnet`, 1549
bytes, the Katzenpost box, and up to 8 more its operator lists. A client pads every box it writes
to one size, the size its group uses, and is told it with the mesh. A replica answers a box of a
size it does not take with INVALID_PAYLOAD.


## Geometry

Every size on the mesh follows from the box size B, the plaintext a box carries.

| quantity                               | bytes   |
|----------------------------------------|---------|
| plaintext a protocol may put in a box  | B       |
| padded plaintext                       | B + 4   |
| ciphertext                             | B + 20  |
| read query                             | 33      |
| write query                            | B + 117 |
| reply to a write, or a miss            | 1       |
| reply with a box                       | B + 85  |
| tombstone write                        | 97      |

With B = 267 that is a 287 byte ciphertext and a 384 byte write query; with B = 1549, 1569 and
1666. The seal scheme the protocols on top use is the hybrid NIKE `CTIDH1024-X25519` and the
signature scheme is Ed25519, as on the mixnet.

## Writing, reading, deleting

| action | send                            | outcome                                                                                                                       |
|--------|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| write  | write query                     | SUCCESS or ALREADY_EXISTS: the replica holds a box under that ID. Same bytes: SUCCESS. Different bytes: ALREADY_EXISTS, nothing changes; use the next index. |
| read   | read query                      | SUCCESS with the box: verify, open. NOT_FOUND: not written yet; poll with backoff, reference 2 s doubling to 60 s. TOMBSTONE: deleted. |
| delete | write query, empty ciphertext   | replaces the box; a box never replaces a tombstone                                                                            |

A client that has seen a tombstone treats that Box ID as deleted from then on; other replicas
may hold the box until the tombstone reaches them.


## Epochs

The mesh carries no epoch. Replica epoch = ⌊(now − 1496275200) / 604800⌋, Unix seconds.
A replica keeps a box for the replica epoch it arrived in and the next, one to two weeks, and
may evict the oldest boxes earlier when its disk is full.


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

### Channel frames

Each Channel message has MSGTYPE `0x5048` and carries one frame:

* a 2 byte request id,
* a 1 byte piece index, from 0,
* a 1 byte piece count, 1 to 255,
* the piece: the next slice of the query or reply.

A frame whose count is 0 or differs from earlier pieces of its request, or whose index is not
below its count, is dropped with its request. Duplicate pieces are ignored.

Piece size is computed from the Link: link MDU = ⌊(MTU − 68) / 16⌋ × 16 − 1, Channel MDU = link
MDU − 6, piece = Channel MDU − 4. At MTU 500 that is 431, 425 and 421 bytes, so a write of one
1000 byte box takes three frames.

### Channel messages

A stack that is not RNS must match RNS's Channel on the wire:

* each message is one Link packet with context `CHANNEL` (0x0E), its payload a 6 byte envelope,
  MSGTYPE, sequence number and length, each 2 bytes, then the message;
* sequence numbers wrap at 65536; messages are delivered in order, and out-of-order ones
  buffered up to 48 ahead; duplicates and ones behind are dropped;
* every Channel packet is acknowledged by the Link's packet proof, and a receiver must prove
  each one, or the sender retries and then closes the Link;
* the sender keeps at most its window of unproven packets in flight: 2 at first, one more per
  delivery, one less per timeout;
* a packet is resent with the same sequence number up to 5 tries, after
  1.5^(tries − 1) × max(2.5 × RTT, 0.025 s) × (packets in flight + 1.5).

### Subscribe and push

Subscribe is the Channel query `6 | ttl u16 seconds | box id 32 | ...`, or the Link request
`subscribe` with the bytes after the 6. The answer is `0 | taken u16 | ttl u16`: the first
`taken` IDs are subscribed, for the granted `ttl`, the asked one capped at 3600, 0 asking for
3600. A malformed subscribe is answered with the one byte 5. Unsubscribe is `7 | box id 32 | ...`,
or the request `unsubscribe`, dropping those IDs, or all when none is named; the answer is the
one byte 0.

A push is a run of Channel messages of MSGTYPE `0x5049`, framed as Channel frames are under
request ids the replica counts, carrying `box id 32 | reply`, the reply as for a read: 0 with the
signature and ciphertext, or 11 for a tombstone.

### Announce

The application data of a replica's announce is one byte of flags: bit 0 a bridge, bit 1 serves
Channel mode, bit 2 serves the replica paths in Channel mode, bit 3 serves no Link requests,
bit 4 serves push. A bridge follows it with its 16 byte mixnet id.

### Vectors

`testdata/bridge_socket_vectors.json` in `pigeonhole_rns` holds query and reply bytes (`queries`,
`replies`), queries a replica refuses (`malformed`) and boxes with what a replica answers each
(`boxes`). The frames in it, a 4 byte length before each message, are the socket between a
bridge's two halves and are not sent by a client.


## Pending

Not merged at the time of writing: box sizes in the pigeonhole_protocols library, so its clients
pad to the `mesh` size and read every allowed size (pigeonhole_protocols#43).
