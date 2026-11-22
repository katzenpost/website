---
title: ""
linkTitle: "Pigeonhole replicas over Reticulum"
description: ""
author: "David Stainton"
url: ""
date: ""
draft: "false"
slug: "reticulum"
layout: ""
type: ""
weight: "999"
version: ""
---

## Pigeonhole replicas over Reticulum

**Abstract**

Pigeonhole replicas on a Reticulum mesh give Reticulum users asynchronous group communication
with post quantum confidentiality, and let them share groups with users of a Katzenpost
mixnet. The mesh side spends as few bytes as it can. The mixnet side keeps its metadata
privacy. Neither needs the other to work.

This document assumes the [Echomix paper](https://arxiv.org/abs/2501.02933) and the
[Pigeonhole specification](/docs/specs/pigeonhole/). The client's side is
[Pigeonhole protocols over Reticulum](/docs/specs/pigeonhole-protocols-reticulum/). The
reference implementation is [pigeonhole_rns](https://github.com/katzenpost/pigeonhole_rns),
a Python replica on RNS and a Rust replica on Reticulum-rs.


## What crosses over

A box is a Box ID, a ciphertext and a signature. The Box ID is the public key that verifies
the signature, the ciphertext is readable only with the read capability, and consecutive
boxes of one writer are unlinkable to anyone without it. A replica keeps a box because it
verifies, not because of who brought it. Both networks carry this same object, so a box
written on one can be carried to the other by anyone who can read it, and it arrives as
authentic as it left.

Everything above the box is shared: BACAP, the box sizes, the group chat message format.
Everything below it differs, and this document describes the mesh half.


## Priorities

The mesh carries bytes over LoRa and similar links, so the design pays public key
cryptography as rarely as it can, carries no padding beyond the box, and hides nothing from
replicas that the mixnet hides from couriers. The mixnet makes the opposite trade in its own
specification.

BACAP is already quantum annoying: without the blinding factor an adversary cannot read a box
or link two of them, quantum computer or not. The one thing a quantum adversary can do is
forge a write into a box whose ID it has seen. That holds on both networks. What BACAP does
not cover is the traffic that carries it: which Box IDs are written and read, and when.


## Open mode

A mesh runs in open mode. A replica is any node that announces a Reticulum destination under
application name `pigeonhole`, aspect `replica`. There is no list to join. The replica's
Reticulum identity is its identity, and the Link a client opens to it is authenticated by it.

Queries travel on that Link as they are. Reticulum's link encryption gives them X25519 forward
secrecy and Ed25519 authentication of the replica, both classical. There is no post quantum
authentication of replicas. No session layer is added, because anyone may announce a replica,
and a replica sees the Box IDs and read times of the boxes it handles, as a replica does on
the mixnet. What remains post quantum is what BACAP protects: contents and linkage.

Every replica holds every box. There is no placement on the mesh; sharding happens only on the
Katzenpost side of a bridge, as the mixnet places boxes.


## Replication

A replica that newly holds a box, written by a client, forwarded by another replica, pulled
from a mixnet or fetched for a reader, forwards it to every replica it has heard except the
one it came from. It retries each with backoff until that replica acknowledges with SUCCESS or
ALREADY_EXISTS, and stops for one that answers INVALID_SIGNATURE, INVALID_BOX_ID or
INVALID_PAYLOAD. A box it already held is not passed on again, so a forward is never
forwarded twice. Forwards to different replicas run at once.

Replicas identify themselves on the Links they open to each other, so a receiver knows a
forward's sender and does not send the box back. A write from an unidentified Link is a
client's.

When a replica first hears another, and again after it found it unreachable or either
restarted, the two sync. The initiator walks the Box ID space in pages of up to 128 Box IDs,
each with a tombstone flag. The responder answers each page with its own page over the same
range, cut short when full, and each side enqueues for the other the boxes it lacks. A
tombstone is sent where the other holds the box it replaces. An unidentified initiator gets
the answer but no boxes.

### Reading

A client sends a read to one replica, its entry replica. The entry replica answers from its own
store. Otherwise it asks every reachable replica with `peek`, in the box's order, which answers
from that replica's store only, a bridge also asking its mixnet. The first box or tombstone found is
returned, kept and forwarded like a write, so the next reader finds it on the mesh. If none has
it and the entry replica is itself a bridge, it asks its mixnet. Otherwise the reply is
NOT_FOUND, and the client asks again later or subscribes to the box.

A box's order ranks replicas by SHA-256 of the replica's identity hash and the Box ID, lowest
first; anyone who has heard the same replicas computes the same order.

### Deleting

A tombstone is a write with an empty ciphertext. It replaces the box and is forwarded and
synced like one; a box never replaces a tombstone. A read of a tombstoned box answers
TOMBSTONE. A reader that has seen a box's tombstone treats the box as deleted thereafter, since
another replica may hold the box until the tombstone reaches it.


## Epochs and garbage collection

Boxes are kept by replica epoch, as on Katzenpost replicas. An epoch is 1200 seconds, a replica
epoch is 504 epochs, one week, both counted from 2017-06-01 00:00 UTC (Unix 1496275200):

```
replica epoch = ⌊(now − 1496275200) / 604800⌋
```

A box is stamped with the replica epoch it arrived in and kept for that epoch and the next, so
one to two weeks. Collection runs at start and at every replica epoch boundary. Both periods
are settings; a bridge keeps the defaults, since the bridge socket carries no timing and
Katzenpost's replica epoch is a week. The group chat protocol's acknowledgements and backfill
cover readers who were away longer.


## Disk limits

A replica keeps every box while there is room. Two limits bound the room: a cap on the box
database and its write-ahead log (none by default), and a minimum of free space on its
filesystem (500 MiB by default, as Katzenpost's `MinFreeStorageMiB`). A new box that would
cross either first evicts the oldest boxes, by replica epoch and then arrival, tombstones only
after every box, until a sixteenth of the limit is spare. Only when nothing is left to evict
is the write answered STORAGE_FULL. Evicted pages are returned to the filesystem, so the limits
measure real disk use.


## Box sizes

A replica takes boxes of several sizes at once, since meshes and mixnets joined through
bridges need not share one. A box's size is its plaintext size; the ciphertext is the
plaintext with a 4 byte length before it, zero padded, plus a 16 byte AEAD tag.

| profile  | plaintext | ciphertext | write query |
|----------|-----------|------------|-------------|
| `mesh`   | 256       | 276        | 373         |
| `mixnet` | 1549      | 1569       | 1666        |

`mixnet` is the Katzenpost box, fixed by the Sphinx geometry. `mesh` is the largest multiple of
16 whose write, and a replica's forward of it, fit one Link packet at Reticulum's 500 byte MTU in
either query mode: the 431 byte Link MDU, less request mode's 31 byte msgpack framing (more than
Channel mode's 11), less the forward's 113 byte head, less the 20 bytes of box overhead, is 267,
rounded down to 256. It is the size clients on Reticulum write.

A replica always takes `mesh` and `mixnet` and up to 8 more sizes its operator lists, none over
1549. It refuses a box of any other ciphertext size with INVALID_PAYLOAD, and a replica
forwarding such a box drops it. A tombstone is always taken. An operator may instead take any
size, which on a bridge leaves the check to the Katzenpost replica.


## Bridges

A bridge joins a mesh to a Katzenpost mixnet so that a group can have members on both without
either side doing anything. It is a mesh replica like any other, holding every box and
syncing, beside a Katzenpost replica that is a member of the mixnet's PKI. The two share a host
and talk over a unix socket on the Katzenpost replica. What the bridge brings in enters under
that already vetted replica's name; this is why the crossing happens between replicas and not
through a new door into the mixnet.

A bridge announces the mixnet it serves as an id: the first 16 bytes of SHA-256 of a name its
operator gives, such as the mixnet's PKI identity, the same on every bridge to that mixnet.

**Out of the mesh.** A bridge writes each box it holds into its mixnet, where the Katzenpost
replica treats it as a replication write and dispatches it to the box's shards. Bridges
serving the same mixnet first ask each other, with `pushed`, whether one has written the box:
the first in the box's order among them writes, and the others wait up to three retries for
it and then write themselves. A duplicate write is harmless. A bridge may instead write only
the boxes clients write to it, while still pulling for reads.

**Into the mesh.** Nothing on the mixnet announces a write, so the mixnet cannot push. A read
that misses on the mesh reaches the bridges, which ask their Katzenpost replicas; the bridge
that finds the box keeps it, with its mixnet as the box's origin, and it replicates from
there. The read is the watch list: no one tells a bridge what to look for.

A box carries its origin through replication, as a `forward` prefixed with the mixnet id, so no
bridge writes a box back into the mixnet it came from, while bridges to other mixnets do. One
mesh can join several mixnets without loops. A tombstone written directly on a mixnet does not
cross to the mesh, since the bridge socket returns a tombstone without its signature; one
written on the mesh reaches every mixnet.

A box from the mixnet appears on the mesh only because a mesh node holding its read capability
asked for it by ID, which is a group member; the consent is the membership. A mesh box written
into the mixnet shows mixnet replicas nothing the mesh did not already show every mesh
replica. What a bridge costs is paid by its operator: a mixnet round trip the first time a
mixnet box is read on the mesh, and a replication write into the mixnet for every box the mesh
writes.

A bridge carries boxes of every size it takes unchanged.


## Query modes

A query reaches a replica over a Link to its destination in one of two modes. Both carry the
same query and reply bytes, and one destination serves both.

1. **Request mode.** Each query is a Link request to a path; one larger than the Link MDU
   travels as a Resource.
2. **Channel mode.** Each query and reply is a run of Channel messages on the Link, for
   Reticulum stacks with Links and Channel but no Link requests or Resources. The message's
   first byte picks the handler.

| path          | Channel op | between             |
|---------------|------------|---------------------|
| `read`        | 0          | client and replica  |
| `write`       | 1          | client and replica  |
| `peek`        | 2          | replicas            |
| `sync`        | 3          | replicas            |
| `forward`     | 4          | replicas            |
| `pushed`      | 5          | bridges             |
| `subscribe`   | 6          | client and replica  |
| `unsubscribe` | 7          | client and replica  |

For ops 0 and 1 the op is the query's own first byte. For the others the op byte is followed by
that path's request bytes and answered with its response bytes.

Replicas ask each other in Channel mode first, when the other announces that it serves the
replica paths there (or Channel mode at all, for a write), and fall back to a Link request when
it does not or the Channel query fails. A replica announcing that it serves no Link requests,
such as the Rust replica, is asked only in Channel mode. The Python replica serves both modes.

A replica handles Channel queries on 2 workers per Link, with up to 16 more queued per Link and
at most 32 at once across the replica. A query arriving to a full queue is dropped; the asker
times out and asks again.


## Push

A client can subscribe on its Link to the Box IDs it waits for, and the replica pushes each box
down that Link when it newly holds it: written by a client, arriving by forward or sync, or
pulled from a mixnet. A client that never subscribes polls.

A Link waits for at most 256 Box IDs. A subscription lasts the granted time, at most an hour;
the client renews it by subscribing again. A Box ID already held is pushed at once. A push
consumes the subscription, since a box is written once; the client then subscribes to the
stream's next Box ID. Closing the Link drops every subscription.

Pushes go only over Channel, also to a Link that subscribed with a Link request. They are best
effort: a push sent as the Link closes is lost, and one is dropped when 256 wait to be sent on
its Link, so a client that reconnects reads what it waits for once and subscribes again.


## Group chat on the mesh

The group chat protocol depends only on reading and writing boxes. On the mixnet it writes
several boxes through a temporary stream and a copy command so that a courier sees one action;
the mesh has no courier to hide from, so a mesh client writes the same boxes directly. Readers
on either network see identical streams, and a group whose members are on both talks through a
bridge without knowing it.


## Encoding

All integers are big endian.

### Announce

The application data of a replica's announce is one byte of flags:

| bit | set when the replica                          |
|-----|-----------------------------------------------|
| 0   | is a bridge                                   |
| 1   | serves Channel mode                           |
| 2   | serves the replica paths in Channel mode too  |
| 3   | serves no Link requests                       |
| 4   | serves push                                   |

A bridge follows the byte with its 16 byte mixnet id. A bridge announcing none serves the
mixnet of the empty name. The Rust replica announces bits 1, 2, 3 and 4.

### Queries and replies

A read query is one byte 0 and the 32 byte Box ID. A write query is one byte 1, the 32 byte Box
ID, the 64 byte signature and the ciphertext to the end of the message; a tombstone has an
empty ciphertext. A reply is one result byte, a Pigeonhole replica code, and for a box found
the 64 byte signature and the ciphertext. The codes and their meaning for a client are in
[Pigeonhole protocols over Reticulum](/docs/specs/pigeonhole-protocols-reticulum/).

### Replica paths

* `peek`: a read query, answered with a reply.
* `forward`: the 16 byte mixnet id of the box's origin, then a write query; answered with a
  reply. The origin is kept only from an identified replica.
* `sync`: a 32 byte lower bound, exclusive, a 32 byte upper bound, inclusive, then up to 128
  entries of a 32 byte Box ID and one byte, 1 for a tombstone, in Box ID order. The answer is
  the 32 byte Box ID where its page ends and up to 128 entries of the same form. A malformed
  page is answered with nothing.
* `pushed`: a 32 byte Box ID and one byte, 1 for a tombstone; answered with one byte, 1 when
  this bridge has written that box or tombstone into its mixnet or pulled it from there.

### Subscribe and unsubscribe

Subscribe, after the op byte in Channel mode or as the `subscribe` request:

```
ttl u16 seconds | box id 32 | box id 32 | ...
```

The answer is `0 | taken u16 | ttl u16`. The first `taken` IDs are subscribed; the rest are
refused because the Link already waits for 256. An ID the Link already waits for is renewed
and counts as taken. The granted `ttl` is the asked one capped at 3600, 0 asking for 3600. A
malformed subscribe is answered with the one byte 5, INVALID_PAYLOAD.

Unsubscribe, after op 7 or as the `unsubscribe` request, is a run of 32 byte Box IDs, dropping
those from the Link, or every one when none is named. The answer is the one byte 0.

### Channel frames

A Channel mode query or reply is one or more Channel messages of MSGTYPE `0x5048`:

```
request id u16 | piece index u8 | piece count u8 | piece
```

A query or reply is cut into 1 to 255 pieces of at most the Channel MDU less 4 bytes, the
Channel MDU being the Link MDU less Channel's 6 byte envelope: 421 bytes on a 500 byte MTU
link. A reply carries its query's request id. A receiver drops a request whose pieces disagree
on the count, or that is incomplete after 60 seconds.

A push is a run of Channel messages of MSGTYPE `0x5049`, framed the same way under request ids
the replica counts per Link. Its bytes are:

```
box id 32 | reply
```

the reply as for a read: 0 with the signature and ciphertext, or 11, TOMBSTONE.

### Bridge socket

The two halves of a bridge exchange the same write and read queries and replies over their unix
socket, each message behind a 4 byte length. The mesh replica sends writes to put boxes into
the mixnet and reads to pull them out. `testdata/bridge_socket_vectors.json` in
`pigeonhole_rns`, read by the tests of both implementations, pins the format and what a
replica answers each box.


## Pending

Not merged at the time of writing: Katzenpost replicas holding box sizes besides their
geometry's (katzenpost#1265), so that a bridged mixnet also takes the `mesh` size.
