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

## Niche Use Cases

We can Pigeonhole protocol to compose decentralized apps which do not require permanent data storage
and which can tolerate some latency. Obvious exmaples include:

- one on one chat
- group chat

However, we might have to encourage users to think of these more as "message boards or forums" to dispense
with the notion that messages will arrive in real-time.

Less obvious examples include any application that can be modeled as replicated state machines driven by append-only events.
Each participant publishes events on their own stream, and every client reconstructs the same state by applying those events.

Formally:

```
state = fold(events)
```


This works especially well when:

- events are small
- ordering only needs to be consistent per author
- conflicts can be resolved deterministically
- temporary divergence is acceptable


Future work falls roughly into two categories:

- integrations with existing systems
- new protocols and applications


As for integrations, we have two of them planned for the future:

- Prometheus: The ability to upload metrics to a Prometheus aggregator anonymously over the mixnet.
- NNCP: The ability to use existing NNTP infrastructure to transfer and receive files anonymously.


And then there are new protocols and applications which will use our
broadcast API for use cases other than "group chat":

- A Doodle-like protocol which allows participants to vote on
  candidate meeting dates and times. The poll creator proposes a set
  of time slots, and group members publish ballots indicating their
  availability for each slot. Votes are transparent to all group
  members and may be updated by publishing a new ballot. Clients
  derive the current poll state by folding all poll events observed
  across the group’s streams.

- War room / situation room: This application provides a
  decentralized coordination space for managing incidents or urgent
  operational problems within a group. When an incident occurs, a
  participant creates an incident object, and group members publish
  updates, tasks, and status messages to their own streams. Clients
  reconstruct the current incident state by folding all
  incident-related events, producing a shared view of the timeline,
  active tasks, and overall status. Participants may independently add
  observations, claim or update tasks, and report progress as the
  situation evolves, while a final resolution message marks the end of
  the incident. Because all events are append-only and replicated
  across participants, the system provides a durable but temporary
  record of the coordination process, which naturally expires once the
  incident has been resolved.

