---
title: 'Introduction to Pigeonhole Protocol'
description: ""
date: 2026-03-13
language: "English"
author: "David Stainton"
tags: ["research", "mixnet", "reticulum", "apps", "pigeonhole", "protocol"]
draft: false
---

Pigeonhole is the storage protocol described in our paper,
[Echomix: a Strong Anonymity System with Messaging](https://arxiv.org/abs/2501.02933).
The paper has the details. This post says what Pigeonhole is, what it is good for, and,
now that it runs over Reticulum mesh networks as well as the Katzenpost mixnet, what each
of the two networks gives and what it costs.

## Channels made of boxes

A Pigeonhole channel is a sequence of *boxes*: fixed-size ciphertexts kept by storage
replicas. Whoever holds a channel's write capability can write boxes to it; whoever holds
its read capability can find and read them. No one else can do either. Boxes are encrypted
and signed, so a channel is confidential and authentic.

Channels are:

- **unidirectional**: one writer, any number of readers;
- **replicated** across storage replicas;
- **ephemeral**: replicas discard boxes after at most two weeks.

They are append-only and immutable, with two qualifications. A writer may compute an index
further ahead and write there, skipping boxes; and a writer may overwrite a box with a
tombstone to delete it. Post-compromise security is not built in; it comes from chaining
channels. Two one-way channels make a two-way one.

## What it is not for

Pigeonhole does not keep data. Anything that must outlive two weeks, such as a ticket
tracker, an events calendar, a content management system or revision control, belongs
elsewhere. Nor does it suit real-time traffic over the mixnet, where a box takes about
twenty-five seconds to write. Over a Reticulum mesh it is much faster; the numbers are below.

## Chat

For one-on-one chat, Alice gives Bob the read capability of a channel she writes, and Bob
gives Alice the read capability of his. Each writes to their own channel and reads the
other's.

Group chat generalises this. Every member writes to their own channel and holds the read
capabilities of everyone else's. Messages are ordered per author; there is no global order.

Our group chat protocol is katzenqt1, in
[pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols). Several clients
speak it, so they all share groups:

- [katzenqt](https://github.com/katzenpost/katzenqt): Qt desktop client
- [hushphone](https://github.com/katzenpost/hushphone): Rust and Slint, push-to-talk voice messages, Linux and Android, over the mixnet or a Reticulum mesh
- [jam](https://github.com/katzenpost/jam): Lean terminal client
- [frank_chat](https://github.com/katzenpost/frank_chat): Lean 4 client with security oriented dependent types
- [katzenrns](https://github.com/katzenpost/katzenrns): Python client for a Reticulum mesh
- [pigeonhole_reticulous](https://github.com/katzenpost/pigeonhole_reticulous): group chat on the LilyGO T-Deck Plus, over a Reticulum mesh

## Pigeonhole over Reticulum

Pigeonhole also runs over [Reticulum](https://reticulum.network) mesh networks. There the
storage replica is [replica_rns](https://github.com/katzenpost/pigeonhole_rns), a Reticulum
node that stores BACAP boxes and places each one on two of the replicas it hears. A mesh
needs at least one replica. A replica can also be a bridge to a Katzenpost storage replica,
joining the mesh to the mixnet.

The integration happens at the BACAP box. The Reticulum transport knows nothing of chat; it
moves boxes. Every protocol built on Pigeonhole therefore works over Reticulum unchanged, an
application can switch between the two transports, and through a bridge, mesh users and
mixnet users share the same groups. We have tested exactly that: katzenrns users on a mesh
chatting with hushphone users on the namenlos mixnet through the namenlos bridge. We suspect
a mesh can also join two mixnets, and are testing it now.

## How fast is it?

We timed bare box operations, with no chat client in the way: write three boxes to a fresh
channel one after another, read them back at once (the first read), then read them again.
Figures are cumulative seconds, the median of five runs on 5 November 2026, with the range
in brackets.

| seconds | namenlos mixnet | Reticulum, local replica | Reticulum, namenlos bridge |
|---|---|---|---|
| write 1 box | 25 (24–30) | 0.05 (0.05–0.05) | 0.20 (0.20–0.20) |
| write 2 boxes | 51 (47–61) | 0.10 (0.10–0.10) | 0.35 (0.35–0.40) |
| write 3 boxes | 73 (67–80) | 0.15 (0.15–0.16) | 0.55 (0.50–0.60) |
| first read of 1 box | 24 (15–26) | 0.05 (0.05–0.05) | 0.15 (0.15–0.20) |
| read 1 box | 28 (21–31) | 0.05 (0.05–0.06) | 0.15 (0.15–0.20) |
| read 2 boxes | 46 (40–61) | 0.10 (0.10–0.11) | 0.30 (0.30–0.35) |
| read 3 boxes | 67 (65–90) | 0.15 (0.15–0.16) | 0.45 (0.45–0.50) |

The mixnet client was the Python thin client on its own `kpclientd`. The mesh client was
`pigeonhole_rns`, over TCP to a replica on the same machine and over the internet to the
namenlos bridge replica (145 ms ping away); opening the Reticulum Link first took 5 and 6
seconds and is not counted. That client polls for replies every 50 ms, so the mesh figures
are rounded up to steps of 50 ms. Every mixnet operation is two round trips over five-hop
Sphinx routes: the courier acknowledges the query, then the client fetches the replica's answer
with a fresh SURB. On the mesh, an operation is one request on an open Link.

## Beyond chat: replicated state machines

Pigeonhole suits any application that can be modelled as a replicated state machine driven
by append-only events. Each participant publishes events on their own channel, and every
client rebuilds the same state by applying them:

```
state = fold(events)
```

Anonymous voting, ephemeral shared documents, sensor metric aggregation and shared incident
logs all fit. They need state that converges across participants without a coordinator, and
they can live with data that expires. The pattern works best when events are small, ordering
matters only per author, conflicts resolve deterministically, and brief divergence is
acceptable.

Pigeonhole's single-writer channel maps onto the actor model of Conflict-free Replicated Data
Types (CRDTs). A CRDT can be updated independently by many participants and always converges
when the updates are merged, with no coordination. Since each participant can write only to
their own channel, every event is cryptographically attributed to one author: exactly the
actor uniqueness CRDTs assume.

Our first prototype was in Rust, on the [`crdts`](https://crates.io/crates/crdts) crate.
Folding a group's votes into a tally looked like this:

```rust
// Each member's vote event is a CRDT op.
// The actor ID is derived from their Pigeonhole read capability.
let mut tally: Map<SlotId, MVReg<Vote, Actor>, Actor> = Map::new();

// Collect votes from all members, waiting up to the poll deadline.
let events = group.receive_from_all_timeout(poll_deadline).await?;
for event in events {
    tally.apply(event.op);
}
render(&tally); // same result regardless of arrival order
```

Two participants who have seen the same events compute the same state, whatever the order
or time of arrival.

### Late joiners

Since boxes last at most two weeks, a member who joins a long-running group cannot always
replay its history. An existing member instead serialises their CRDT state and hands it to
the newcomer over a one-shot Pigeonhole channel. The newcomer merges it as a baseline and
applies new events from then on; because merges are idempotent, events already in the
snapshot are harmless.

```rust
// Late joiner receives a snapshot from an existing member,
// then continues with live ops from the group streams.
state.merge(snapshot);

loop {
    let event = group.receive_any().await?;
    state.apply(event.op); // duplicate ops are safe — idempotent
}
```

The two-week expiry sets the cadence: as the oldest boxes near it, an online member can
offer a fresh snapshot to anyone at risk of falling behind.

## What comes next

Two integrations with existing systems:

- **Prometheus**: uploading metrics to a Prometheus aggregator anonymously over the mixnet.
- **NNCP**: sending and receiving files anonymously through existing NNCP infrastructure.

And new protocols on the broadcast API, the first of which is **Tally**, a transparent voting
protocol. A poll's creator proposes options; members publish ballots, visible to the whole
group. A ballot can be changed by publishing a new one, and since each channel has a single
writer, no one else can change it. Clients fold the ballots into the current tally, and a
CRDT register keeps concurrent updates side by side for the interface to show, rather than
silently dropping one. katzenqt1 already reserves message types for it. A meeting scheduler
follows naturally: the options are time slots, and the ballots are availability.

## Conclusion

Pigeonhole is less a messaging protocol than a substrate. Give every participant a
cryptographically owned, single-writer channel, let clients fold events across those
channels, and you get applications that converge without a coordinator, provided they can
let their data expire.

The substrate now runs on two networks, and neither is simply better.

A Reticulum mesh offers more ways to connect: LoRa radio, serial lines, TCP, with or
without the internet. It is unregulated and free: anyone may run a node or a replica, and
there is no global directory and no one to ask. It is fast, a twentieth of a second per box
on a local link and a fifth of a second across the internet. But it hides little metadata:
an observer of the mesh sees which node talks to which replica, and when. An open mesh's
cryptography is classical. The closed mesh of our specification adds post-quantum Noise
sessions, but only by vetting its replicas, as the mixnet does.

The mixnet is the opposite on each count. It is strict and closed: a node joins only when the
directory authorities admit it, and every client follows one PKI document, voted on and published each epoch by a
small set of directory authorities, six on namenlos. The authorities are independent, but
beside the mesh the design is plainly centralised. In return the mixnet hides who talks to
whom, even from a global observer, and uses hybrid post-quantum cryptography for its links,
its directory signatures and the envelopes that carry Pigeonhole queries. The price is time:
about twenty-five seconds per box.

Because the two meet at the BACAP box, an application need not choose once. The same group
can have members on each side of a bridge, each choosing the network that suits them.
