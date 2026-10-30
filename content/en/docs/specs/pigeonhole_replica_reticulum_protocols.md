---
title: ""
linkTitle: "Pigeonhole over Reticulum"
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

**Abstract**

Pigeonhole storage replicas on a Reticulum mesh give Reticulum users a durable, asynchronous
group chat with post quantum confidentiality, and let them share groups with users of a
Katzenpost mixnet. The mesh side spends as few bytes as it can. The mixnet side keeps its
metadata privacy. Neither needs the other to work, and no one has to agree on anything before
running a replica.

This document assumes the [Echomix paper](https://arxiv.org/abs/2501.02933) and the
[Pigeonhole specification](/docs/specs/pigeonhole/).


## What crosses over

A box is a Box ID, a ciphertext and a signature. The Box ID is the public key that verifies
the signature, the ciphertext is readable only with the read capability, and consecutive
boxes of one writer are unlinkable to anyone without it. A replica stores a box because it
verifies, not because of who brought it. Both networks store this same object at the same
size, so a box written on one can be carried to the other by anyone who can read it, and it
arrives as authentic as it left.

Everything above the box is shared: BACAP, the box size, the group chat message format.
Everything below it differs, and this document describes the mesh half.


## Priorities

The mesh carries bytes over LoRa and similar links, so the design pays public key
cryptography once per session rather than once per query, carries no padding, and hides
nothing from replicas that the mixnet design hides from couriers. The mixnet makes the
opposite trade in its own specification.

BACAP is already quantum annoying: without the blinding factor an adversary cannot read a box
or link two of them, quantum computer or not, and the paper states the one thing a quantum
adversary can do, which is forge a write into a box whose ID it has seen. What BACAP does not
cover is the traffic that carries it. Box IDs and read patterns in transit, and knowing that
the replica answering is the one you meant, are protected here by one more layer: a Noise
session over a hybrid NIKE, X25519 combined with CTIDH1024. Confidentiality must hold against
an adversary who records traffic now and has a quantum computer later; authentication must
hold against one who has it now. Both do, and the next section says why without any post
quantum signature.


## Membership

A replica is a node that announces a Reticulum destination under the Pigeonhole application
name. There is no list to join. The announce carries the replica's long term hybrid NIKE
public key, and that key is the replica's identity: boxes are placed by hashing it, and
sessions authenticate against it. The Reticulum identity that signs the announce is only a
location, saying where that key can currently be reached. Nothing below rests on it.

This is what bootstraps post quantum authentication on a classically signed mesh. Noise
authenticates by Diffie-Hellman, not by signature: a replica proves it holds the private half
of the announced key, and the key is hybrid. An adversary who breaks the Ed25519 on an
announce can forge one for a replica's address, but can only put its own key in it. Then it
has announced a new replica at a stolen address, which anyone may do classically, and a client
that connects authenticates it as itself, never as the replica it meant.

Each node remembers the key it first saw for a destination and ignores an announce that
changes it, as Reticulum itself refuses a changed public key for a known destination hash. A
replica that wants a new key announces it as a new replica. The old key leaves path tables as
its announces stop, and the boxes it owned move to the new order through the handoff below.
Noise ephemerals give every session forward secrecy, so a key can live for years.

Because anyone may be a replica, a single operator announcing many keys holds a larger share
of the box order. That costs the mesh bandwidth, since boxes are forwarded to those keys, and
nothing else: every replica that handles a box keeps it, and a reader is never limited to the
owners. A community that wants a closed set of replicas uses Reticulum's own boundaries, an
interface passphrase or a Network Identity on the interfaces that carry the mesh.


## Sessions

All Pigeonhole traffic runs inside a Noise session over a Reticulum Link, with the hybrid
NIKE as the Diffie-Hellman function, ChaCha20-Poly1305 and BLAKE2s. Reticulum's own link
encryption carries it but is not relied on.

A client speaks `Noise_NK` to a replica:

```
NK:
  <- s
  ...
  -> e, es
  <- e, ee
```

The replica's static is known from its announce. The client has no identity to prove, since
the capability inside its query is the authorisation, and NK keeps it anonymous, as a
Reticulum link initiator is. The handshake is one round trip, and the client puts its first
query in the first message, so a query and its reply together cost one round trip. That first
payload is encrypted to the replica's static alone, so it is replayable and would be exposed
by a later compromise of that static. A replayed write is idempotent, a replayed read yields
a reply only the original client can decrypt, and the only thing in the payload is a Box ID
and a box, which the replica sees in any case. A client that nevertheless wants forward
secrecy for its first query sends it after the second message, for one more round trip.
Everything after the handshake has forward secrecy.

Replicas speak `Noise_KK` to each other. Both statics are known from announces, so the
handshake transmits only ephemerals and completes in one round trip. These sessions are long
lived and reopened when a link is lost.

A Noise message that fits a link packet travels as one; a larger one travels as a Reticulum
Resource.


## Placement

Rendezvous hashing orders the replicas for every box: each replica's score is the hash of its
identity key and the Box ID, lowest first. The first two replicas in a box's order are its
owners. Box IDs are uniformly random, so every replica owns an equal share, and anyone who
holds a Box ID can compute its owners from the announces it has heard, without asking.

Placement is what lets the mesh grow. With two copies per box however many replicas there
are, capacity grows with the number of replicas, and a reader asks two of them instead of all
of them. Without it every replica would come to hold every box, as propagation nodes do.

Two nodes may have heard different announces, and a partition hides replicas from both. So
every node applies the order to the replicas it knows and can reach, and the protocol is
written so that differing views converge instead of conflicting. Sharding is the result when
every replica is reachable; store and forward is what happens in between.

### Writing

A client sends a write to the reachable replica with the fewest hops in its path table, its
entry replica. The entry replica stores the box and acknowledges. The client is done.

The entry replica then forwards the box to the first two reachable replicas in the box's
order. When those are the owners, the box is where every reader looks first. When an owner is
unreachable or unknown, a stand-in holds the box in its place and forwards it to the owner
once it can reach one. Placement depends only on the Box ID and the replicas a node knows, so
when a partition heals or an announce arrives, every held box moves to the right owners.

A replica stores a box it already holds once, so forwarding needs no coordination. A
replica that is not one of a box's owners keeps its copy until both owners have acknowledged
holding the box, then may drop it. During a partition no acknowledgement comes and nothing is
dropped; once every replica is reachable the extra copies disappear after one handoff and the
mesh holds two copies per box. Stored boxes survive a restart.

### Reading

A client sends a read to its entry replica. The entry replica answers from its own store if
it can. Otherwise it asks the reachable replicas in the box's order, owners first, and
returns the first box it is given. It does not stop at the owners: if they do not have the
box it continues down the order, so a copy held by a stand-in or by another client's entry
replica is found, and an owner that withholds a box only costs the reader queries. If no
reachable replica has it, the reply says so, and the client asks again later.

Within a partition, the replicas a reader can reach are the ones its neighbours wrote to, so
a group keeps chatting among the members it can reach. Boxes written on the other side arrive
when the first stand-in can reach an owner.

### Deleting and forgetting

A tombstone is a write with an empty payload. It replaces the box, is forwarded like one, and
a read of a tombstoned box says so. Replicas keep boxes for the current and previous replica
epoch, one week each, and drop older ones; the group chat protocol's acknowledgements and
backfill cover readers who were away longer.

A reader that has seen a box's tombstone treats the box as deleted thereafter, since
another replica may still hold the box until the tombstone reaches it.


## Group chat on the mesh

The group chat protocol depends only on reading and writing boxes. On the mixnet it writes
several boxes through a temporary stream and a copy command so that a courier sees one
action; the mesh has no courier to hide from, so a mesh client writes the same boxes directly.
Readers on either network see identical streams.

A member who is on both networks carries boxes between them: it reads the streams of the
members it can see on one side and writes those boxes, unchanged, on the other. Nothing else
is needed for a group to span the two.


## Encoding

A replica's announce carries, as application data, its 192 byte hybrid NIKE public key:
the 32 byte X25519 key followed by the 160 byte CTIDH1024 key.

A query is a Noise message payload:

* one byte, zero for a read and one for a write,
* the 32 byte Box ID,
* for a write, the 64 byte signature and the ciphertext, whose length is fixed by the box
  size; a tombstone has a zero length ciphertext.

A reply is:

* one byte result: found, not found, tombstone, stored, or an error code from the Pigeonhole
  specification,
* for a found box, the 64 byte signature and the ciphertext.

Replicas exchange boxes with the same write message and reply.

All integers are big endian.
