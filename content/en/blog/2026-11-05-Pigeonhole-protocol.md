---
title: "Introduction to Pigeonhole Protocol"
date: "2026-11-05"
description: "Pigeonhole as a network-independent abstraction: what it is, what it guarantees, what we build on it, and the mixnet and Reticulum mesh it runs on, with measured box timings."
author: "David Stainton"
tags: ["research", "mixnet", "reticulum", "apps", "pigeonhole", "protocol"]
version: ""
draft: false
---

Pigeonhole is a protocol for asynchronous, unlinkable communication. Without a read
capability, no one can tell which messages belong together, and sender and reader need not
be online at the same time. That second property is the only reason Pigeonhole stores
anything. Our paper,
[Echomix: a Strong Anonymity System with Messaging](https://arxiv.org/abs/2501.02933), and
[Understanding Pigeonhole](/docs/pigeonhole_explained/) have the details. This post treats
Pigeonhole as an abstraction that does not depend on the network beneath it: what it is,
what it guarantees, what we build with it, and the two networks it now runs on.

## What Pigeonhole is

A Pigeonhole channel is a sequence of *boxes*: fixed-size ciphertexts, each signed and named
by a Box ID. Two capabilities govern it. The write capability writes boxes and derives the
read capability; the read capability finds, verifies and decrypts them. A channel has one
writer and any number of readers, and two one-way channels make a two-way one.

Boxes are immutable, with one exception: tombstones. The holder of the write capability can
replace a box with a tombstone, an empty ciphertext with a valid signature over it, which
deletes the box. That is a feature.

Box indexes come from a KDF ratchet, which moves forward but not backward. A read capability
that starts at index *n* reaches box *n* and every box after it, never one before. You can
therefore share a channel from now on without sharing its history.

Storage replicas verify, store and forward boxes; they cannot read them. They keep the
current and the previous replica epoch, a week each, so a box lives one to two weeks before
it is garbage-collected. Anything that must last, such as a ticket tracker, a calendar or
revision control, belongs elsewhere.

## What it guarantees, and against whom

- **Confidential**: only holders of the read capability can decrypt a box.
- **Authentic**: a box that verifies was written by the holder of the write capability. That
  is a key, not a person: whoever holds the write capability is the author.
- **Unlinkable**: without the read capability, no one, the replicas included, can tell which
  boxes belong to one channel.

Who learns *which node* wrote or read a box depends on the network. On the mixnet, no one
does: not the replica, not the courier that relays the query, not a global observer of the
network. On an open mesh, the replica a node talks to sees which boxes it writes and fetches,
and when; anyone may run a replica, and a network observer sees which node talks to which
replica.

BACAP, the scheme beneath the boxes, keeps contents and linkage safe even from a quantum
adversary, but its signatures are Ed25519, so such an adversary could forge a write into a
box whose ID it has seen. A channel has no post-compromise security of its own: a leaked
capability works until the participants move to a fresh channel.

## What we build with it

**Chat.** For one-on-one chat, Alice and Bob each write a channel and give the other its read
capability. In group chat every member writes their own channel and reads everyone else's;
messages are ordered per author, with no global order. Our group chat protocol is katzenqt1,
in [pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols), and these
clients speak it, so they all share groups:

- [katzenqt](https://github.com/katzenpost/katzenqt): Qt desktop client
- [hushphone](https://github.com/katzenpost/hushphone): Rust and Slint, push-to-talk voice messages, Linux and Android, over the mixnet or a Reticulum mesh
- [jam](https://github.com/katzenpost/jam): Lean terminal client
- [frank_chat](https://github.com/katzenpost/frank_chat): Lean 4 client with security oriented dependent types
- [katzenrns](https://github.com/katzenpost/katzenrns): Python client for a Reticulum mesh
- [pigeonhole_reticulous](https://github.com/katzenpost/pigeonhole_reticulous): group chat on the LilyGO T-Deck Plus, over a Reticulum mesh

**Replicated state machines.** Any application that is a fold over append-only events fits:
each participant publishes events on their own channel, and every client computes
`state = fold(events)`. Voting, ephemeral shared documents, sensor aggregation and incident
logs all qualify, provided events are small, order matters only per author, and the data may
expire. A single-writer channel gives each event exactly one author, which is the actor
uniqueness that Conflict-free Replicated Data Types (CRDTs) assume, so CRDT state converges
whatever the order of arrival. A late joiner who cannot replay expired events takes a
snapshot of an existing member's state over a one-shot channel and merges it; CRDT merges are
idempotent, so overlap is harmless. Tallying votes looks like this (illustrative only: the
Rust prototype on the [`crdts`](https://crates.io/crates/crdts) crate has been removed from
thin_client):

```rust
let mut tally: Map<SlotId, MVReg<Vote, Actor>, Actor> = Map::new();
for event in group.receive_from_all_timeout(poll_deadline).await? {
    tally.apply(event.op); // same result in any order
}
```

## Where it runs

Pigeonhole meets the network at the box: write a box, read a box, by Box ID. The Katzenpost
mixnet and [Reticulum](https://reticulum.network) are two bindings of that one interface.
Everything above it, BACAP and katzenqt1 included, is shared, so every Pigeonhole
application runs on either. On the mesh, the replica is
[replica_rns](https://github.com/katzenpost/pigeonhole_rns), and the
[specification](/docs/specs/pigeonhole-protocols-reticulum/) has the details.

| | Katzenpost mixnet (namenlos) | Reticulum, open mesh |
|---|---|---|
| who may run a node | those the directory authorities admit | anyone |
| directory | one PKI document per epoch, voted by six authorities | none; replicas announce |
| connectivity | the internet | LoRa, serial, TCP, with or without the internet |
| who sees which node reads which box | no one | the replica it talks to |
| post-quantum | hybrid links, directory signatures and query envelopes; Sphinx packets use X25519 | no; Reticulum's links are classical |
| replica storage | sharded, two replicas per box | every replica stores every box\* |

\* Full replication is in [pigeonhole_rns PR #6](https://github.com/katzenpost/pigeonhole_rns/pull/6),
now in review; sharding is kept for the future closed mesh of the
[replica specification](/docs/specs/reticulum/).

We timed bare box operations, with no chat client in the way: write three boxes to a fresh
channel one after another, read them back at once (the first read), then read them again.
Figures are cumulative seconds, the median of five runs on 5 November 2026, with the range in
brackets.

| seconds | namenlos mixnet | Reticulum, local replica | Reticulum, namenlos bridge |
|---|---|---|---|
| write 1 box | 25 (24–30) | 0.05 (0.05–0.05) | 0.20 (0.20–0.20) |
| write 2 boxes | 51 (47–61) | 0.10 (0.10–0.10) | 0.35 (0.35–0.40) |
| write 3 boxes | 73 (67–80) | 0.15 (0.15–0.16) | 0.55 (0.50–0.60) |
| first read of 1 box | 24 (15–26) | 0.05 (0.05–0.05) | 0.15 (0.15–0.20) |
| read 1 box | 28 (21–31) | 0.05 (0.05–0.06) | 0.15 (0.15–0.20) |
| read 2 boxes | 46 (40–61) | 0.10 (0.10–0.11) | 0.30 (0.30–0.35) |
| read 3 boxes | 67 (65–90) | 0.15 (0.15–0.16) | 0.45 (0.45–0.50) |

The mixnet client was the Python thin client on its own `kpclientd`, with the default ARQ:
each operation is two round trips over five-hop Sphinx routes
([the Pigeonhole ARQ](/docs/pigeonhole_explained/#the-pigeonhole-arq)), and a read retries
until the box is there. The mesh client was `pigeonhole_rns`, over TCP to a replica on the
same machine and to the namenlos bridge replica, 145 ms away. The mesh figures exclude the 5
to 6 seconds Reticulum took to set up the Link, and are rounded up to the client's 50 ms
polling interval.

A replica can also be a bridge to a Katzenpost storage replica, so mesh users and mixnet users
share groups. We have tested exactly that: katzenrns users on a mesh chatting with hushphone
users on namenlos through the namenlos bridge. Since a box is the same object on every
network, a mesh with bridges to several mixnets joins those mixnets together; the bridge rules
for that are landing now.

## What comes next

- **Prometheus**: uploading metrics to a Prometheus aggregator anonymously over the mixnet.
- **NNCP**: sending and receiving files anonymously through existing NNCP infrastructure.
- **Tally**: transparent voting on the broadcast API. Members publish ballots visible to the
  group and may change them; since each channel has one writer, no one else can. A CRDT
  register keeps concurrent ballots side by side rather than dropping one, and katzenqt1
  already reserves message types for it. A meeting scheduler follows: the options are time
  slots, the ballots availability.

## Conclusion

The abstraction is the point. Pigeonhole is defined at the box, so networks plug in
underneath it, and every application above, from chat to Tally, works on each of them.

That makes the Katzenpost mixnet more powerful with Reticulum than without it. The mixnet
keeps what only it gives: metadata privacy against a global observer and hybrid post-quantum
links. Bridged to meshes, it gains reach, to places with radio and no internet, and speed,
a fifth of a second per box instead of twenty-five seconds, for the members who can accept a
mesh's weaker metadata privacy. And a mesh can join several mixnets together, so that the
users of each share groups.
