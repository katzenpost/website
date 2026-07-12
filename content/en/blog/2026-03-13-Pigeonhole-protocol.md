---
title: 'Introduction to Pigeonhole Protocol'
description: ""
date: 2026-03-13
language: "English"
author: "David Stainton"
tags: ["research", "mixnet", "apps", "pigeonhole", "protocol"]
draft: false
---

## Abstract

Today I want to elaborate on what exactly is the Pigeonhole protocol which
is described in our paper:

**Echomix: a Strong Anonymity System with Messaging**
https://arxiv.org/abs/2501.02933

Please see our paper for the gory details. This blog post attempts to describe
what Pigeonhole protocol is at a high level and to explore our niche use cases.

Our mixnet based Pigeonhole protocol provides us with cryptographic communication channels which are:

- unidirectional
- single writer, multi reader
- immutable
- append-only
- durable
- replicated
- ephemeral

I should mention, that of course, these channels provide:

- confidentiality
- authenticity

But they must be chained in order to provide post compromise security.
These one-way channels can be composed to form two-way channels.

The data is only retained by the storage replica servers for a maximum
of two weeks. After two weeks the data is garbage collected.

Technically these channels are not append-only because you could
calculate a message index that is further ahead than the next message
and write to it.  Pigeonhole channels are composed of elements called
boxes which are fixed sized ciphertexts.  A channel write must have
the cryptographic write capability in order to write to the channel.
Likewise a channel reader must have the cryptographic read capability
in order to read from the channel.  However we also violate our
immutable rule to allow holder of a write capability to write
tombstones to the channel in order to remove individual box
ciphertexts within the channel.


## Inappropriate Use Cases

- If you need real-time updates then this protocol might not work out so well for your
use case given that our mixnet adds some latency. Although Pigeonhole protocol could
in theory be used without a mixnet, we do not elaborate on that here.

- Use cases requiring the stored data to be permanent are also not
appropriate here since the data within Pigeonhole channels is
ephemeral and only lives a couple of Pigeonhole epochs; for example,
two weeks. Inappropriate use case examples include: a trouble ticketing system, events
calendar, content management system, revision control system.


## One On One Chat

Alice creates a channel and gives Bob the cryptographic read capability.
Bob creates a channel and gives Alice the cryptographic read capability.

Now, when Alice wishes to write Bob a message, she writes to her own channel and Bob reads it.
Likewise, when Bob wants to send Alice a message he writes to his own channel and Alice reads it.

## Group Chat

We can compose a high level API that provides a broadcast channel amongst a group.
We do this simply by providing every member with their own channel which they use
for writing. The other group members have the read cap for everyone else's channel.

This means there is no global ordering for messages within the "broadcast channel".
But there is per-author message ordering.

## The Replicated State Machine Pattern

Beyond chat, Pigeonhole is a natural fit for any application that can be modeled as a replicated
state machine driven by append-only events. Each participant publishes events on their own stream,
and every client reconstructs the same state by applying those events.

Formally:

```
state = fold(events)
```

This pattern fits a surprisingly wide range of applications beyond chat: anonymous voting systems,
ephemeral collaborative documents, sensor metric aggregation, and shared incident logs. What they
have in common is that they need convergent state across participants without a central coordinator,
and they can tolerate the data expiring after a couple of weeks.

This works especially well when:

- events are small
- ordering only needs to be consistent per author
- conflicts can be resolved deterministically
- temporary divergence is acceptable

The key insight is that Pigeonhole's single-writer stream guarantee maps naturally onto the actor
model used by Conflict-free Replicated Data Types (CRDTs). A CRDT is a data structure that can
be updated independently by multiple participants and always converges to the same state when
those updates are merged — no coordination required. Because each Pigeonhole participant can only
write to their own channel, every event is cryptographically attributed to a unique author, which
is exactly the actor uniqueness assumption CRDTs rely on.

We use the [`crdts`](https://crates.io/crates/crdts) Rust crate, which provides a family of
well-tested, serializable CRDT types. A concrete example: folding a group's vote events into a
tally looks like this:

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

Any two participants who have seen the same set of events will compute identical state, even if
they received those events in different orders or at different times.

The full implementation of `GroupChannel` and `EventChannel` that makes this possible is available
in the [katzenpost/thin_client](https://github.com/katzenpost/thin_client) repository.

### Handling Late-Joining Members

One challenge worth noting: because Pigeonhole retains data for at most two weeks, a member who
joins a long-running group mid-way through cannot always replay all events from the beginning.

We solve this with a snapshot handoff. Any existing member can serialize their current CRDT state
and deliver it to the newcomer over a dedicated one-shot Pigeonhole channel. The newcomer merges
the snapshot as a baseline, then applies only the new events they observe going forward. Because
CRDT merges are idempotent, any events the newcomer subsequently receives that were already
included in the snapshot are safely ignored.

```rust
// Late joiner receives a snapshot from an existing member,
// then continues with live ops from the group streams.
state.merge(snapshot);

loop {
    let event = group.receive_any().await?;
    state.apply(event.op); // duplicate ops are safe — idempotent
}
```

The two-week Pigeonhole epoch boundary is the natural cadence for proactive snapshots: as the
oldest bucket approaches expiry, an online member can offer a fresh snapshot to any peer at risk
of falling behind.


Future work falls roughly into two categories:

- integrations with existing systems
- new protocols and applications


As for integrations, we have two of them planned for the future:

- Prometheus: The ability to upload metrics to a Prometheus aggregator anonymously over the mixnet.
- NNCP: The ability to use existing NNTP infrastructure to transfer and receive files anonymously.


And then there are new protocols and applications which will use our
broadcast API for use cases other than "group chat":

## Tally

Tally is a general purpose transparent voting protocol. The poll creator proposes a set of
candidates or options, and group members publish ballots indicating their choices. Votes are
transparent to all group members and may be updated by publishing a new ballot.

Because each participant's stream is single-writer, their vote is cryptographically theirs —
no one else can update it. Clients derive the current poll state by folding all vote events
observed across the group's streams. Two participants who have seen the same votes will always
compute the same tally, even if those votes arrived in different orders.

Votes can change: publishing a new ballot simply overwrites the previous one. The CRDT's
last-observed-value semantics handle concurrent updates gracefully, preserving all concurrent
versions for the UI to surface rather than silently dropping one.

One application we plan to build on top of Tally is a meeting time scheduler: the poll creator
proposes a set of time slots, and group members publish their availability for each one.
Clients derive the current schedule by folding all availability events across the group's streams.

## SituationRoom

The SituationRoom protocol provides a decentralized coordination space for managing incidents or
urgent operational problems within a group. When an incident occurs, a participant creates an
incident object, and group members publish updates, tasks, and status messages to their own
streams. Clients reconstruct the current incident state by folding all incident-related events,
producing a shared view of the timeline, active tasks, and overall status.

Participants may independently add observations, claim or update tasks, and report progress as
the situation evolves. A final resolution message marks the end of the incident. Because
resolution events go into a grow-only set, an incident cannot be accidentally un-resolved by
a concurrent update — once sealed, it stays sealed.

Because all events are append-only and replicated across participants, the system provides a
durable but temporary record of the coordination process. The record naturally expires once the
Pigeonhole retention window closes, which is appropriate for incident response — post-mortems
belong in a permanent system, not here.

## Conclusion

Pigeonhole is not just a messaging protocol. It is a substrate for a new class of
decentralized applications that work under realistic adversarial conditions — applications
that do not require permanent storage, can tolerate network latency, and need strong metadata
privacy against global adversaries.

The design principle is simple but powerful: give every participant a cryptographically
owned, single-writer stream, and let clients reconstruct shared state by folding events
across those streams. Combined with CRDTs, this produces applications where convergence
is guaranteed, conflicts resolve deterministically, and no central coordinator is ever needed.
Tally and SituationRoom are two early examples of what becomes possible with this approach.
