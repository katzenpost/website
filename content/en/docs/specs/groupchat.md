---
title: ""
linkTitle: "Group chat"
description: ""
author: ""
url: ""
date: "2026-06-02T10:58:11.422588516-07:00"
draft: "false"
slug: "groupchat"
layout: ""
type: ""
weight: "20"
version: "0"
---

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="group_chat"></span>Group chat specification

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">Threebit</span> <span class="surname">Hacker</span>

</div>

<div class="author">

### <span class="firstname">David</span> <span class="surname">Stainton</span>

</div>

</div>

</div>

<div>

<div class="abstract">

**Abstract**

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="d58e43"></span>Prerequisites

</div>

</div>

</div>

This design specification is dependent on the BACAP and Pigeonhole protocol designs
from
our paper <a href="https://arxiv.org/abs/2501.02933" class="link" target="_top">Echomix: A Strong Anonymity
System with Messaging</a>, which describes

<div class="itemizedlist">

- the BACAP (blinded and capability) in §4 and

- the Pigeonhole protocol in §5.

</div>

The <a href="https://github.com/katzenpost/hpqc/blob/main/bacap/bacap.go" class="link" target="_top">source
code</a> and <a href="https://github.com/katzenpost/hpqc/blob/main/bacap/bacap.go" class="link" target="_top">API docs</a> for
BACAP are available on pkg.go.dev.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="d58e63"></span>Introduction

</div>

</div>

</div>

The Pigeonhole protocol establishes anonymous cryptographic communication channels
which
have a <span class="emphasis">*readcap*</span> (read capability) and a <span class="emphasis">*writecap*</span>
(write capability). For example, if Alice and Bob want to communicate, they can each
create
their own Pigeonhole/BACAP channels and exchange readcaps on those channels. Now when
Bob
writes to his channel, Alice can read those messages because she has Bob's readcap.
Likewise,
when Alice writes to her channel, Bob can read those messages because he has Alice's
readcap.
This is the most basic construction using BACAP and Pigeonhole.

Here we extend this basic design to work as a minimal group-chat protocol, without
key
rotation.

BACAP primitives give us two message types:

<div class="itemizedlist">

- `SingleMessage`

- `AllOrNothingMessage` (used for big messages: upload <span class="emphasis">*n*</span>
  chunks to a temporary stream and then put a pointer to that in your own stream as
  a single
  message.)

</div>

The group state consists of:

<div class="itemizedlist">

- a `MembershipCap` for each member, containing:

  <div class="itemizedlist">

  - a BACAP readcap

  - a nickname

  </div>

- a `MembershipHash` (a hash over all of the MembershipCaps)

</div>

The group chat is completely decentralized. Each member must keep track of every other
member.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="d58e101"></span>Group chat message types

</div>

</div>

</div>

All messages are `SingleMessage` if they fit in one BACAP slot, or an
`AllOrNothingMessage` if they are too big.

<div class="itemizedlist">

- `Text` type payloads are normal chat text messages.

</div>

``` programlisting
// TextPayload encapsulates a normal text message.
type TextPayload struct {
    // Payload contains a normal UTF-8 text message to be displayed inline.
    Payload []byte
}
```

<div class="itemizedlist">

- `Introduction` type messages introduce new group members.

</div>

``` programlisting
// Introduction introduces a new member to the group.
type Introduction struct {
    // DisplayName is the party's name to be displayed in chat clients.
    DisplayName string
    
    // UniversalReadCap is the BACAP UniversalReadCap
    // which lets you read all messages posted by this user.
    UniversalReadCap *bacap.UniversalReadCap
}
```

<div class="itemizedlist">

- `FileUpload` type

</div>

A `FileUpload` can be used for various purposes such as uploading an image to
be displayed inline by the chat client. Likewise, a sound bite could be made visible
in the
chat along with a play-button. Beyond that, we can support arbitrary file attachments.

``` programlisting
// FileUpload encapsulates several file types
// which result in different client behaviors.
type FileUpload struct {
    // Payload contains the file payload.
    Payload []byte
    
    // FileType is the identifier for each file type.
    // Valid file types are:
    // "image"
    // "sound"
    // "arbitrary"
    FileType string
}
```

<div class="itemizedlist">

- `Who` type

</div>

The `Who` message type is used to query who is currently in the group.

``` programlisting
// Who is used to query the group chat to find out the member read capabilities.
type Who struct {}
```

<div class="itemizedlist">

- `ReplyWho` type

</div>

The `ReplyWho` message answers the Who query with an
`AllOrNothingMessage` BACAP stream containing readcaps for all group chat
members.

``` programlisting
type ReplyWho struct {
    Payload *bacap.BacapStream
}
```

<div class="itemizedlist">

- `GroupChatMessage` type

</div>

The `GroupChatMessage` message encapsulates all of the above-mentioned message
types and is serialized with CBOR.

``` programlisting
// GroupChatMessage encapsulates all chat message types.
type GroupChatMessage struct {
    // Version is used to ensure we can change this message type in the future.
    Version int

    // MembershipHash is the hash of the user's PleaseAdd message.
    MembershipHash *[32]byte
    
    TextPayload *TextPayload
    Introduction *Introduction
    FileUpload *FileUpload
    Who *Who
    ReplyWho *ReplyWho
}
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="d58e170"></span>Protocol flow

</div>

</div>

</div>

The protocol flow for making a new group from scratch (using whatever authentication
protocol) is essentially for everybody to exchange `PleaseAdd` messages.

``` programlisting
// PleaseAdd is a message used by a client to try and gain access to a chat group.
type PleaseAdd struct {
    // DisplayName is the party's name to be displayed in chat clients.
    DisplayName string
    
    // UniversalReadCap is the BACAP UniversalReadCap
    // which lets you read all messages posted by this user.
    UniversalReadCap *bacap.UniversalReadCap
}

type SignedPleaseAdd struct {
    // PleaseAdd contains the CBOR serialized PleaseAdd struct.
    PleaseAdd []byte
    
    // Signature contains the cryptographic signature over the PleaseAdd field.
    Signature []byte
}
```

For introduction to an existing group over an existing channel between an introducer
member and new member, an `Invitation` message is used.

``` programlisting
type Invitation struct {
    GroupName string
}
```

The `Invitation` protocol flow works as follows.

<div class="orderedlist">

1.  There exists a group called YoloGroup. A member of the group invites a potential new
    member with an `Invitation` message.

2.  If the invited party wants to join, then they reply with a
    `SignedPleaseAdd` message meaning "I want to join your group." This
    provides the invited party's BACAP universal readcap, their display name, and a
    cryptographic signature produced by their BACAP writecap.

3.  The introducer receives the `SignedPleaseAdd` message.

    <div class="orderedlist">

    1.  If the introducer does not like the DisplayName, they reply to the invited party
        with a `PleaseReviseDisplayName` message that contains the original
        `SignedPleaseAdd`. Then they wait for a new
        `SignedPleaseAdd`.

    2.  If the introducer approves of the `DisplayName`, then:

        <div class="itemizedlist">

        - Because existing members need the new member's readcap, the introducer
          publishes the `SignedPleaseAdd` to their own BACAP stream for the
          rest of the group to read.

        - Because the new member needs existing members' readcaps, the introducer
          replies to the new member with `ReplyWho` message containing readcaps
          for all existing members.

          <span class="bold">**IMPORTANT:**</span> The content of both replies must
          be sent in the same `AllOrNothingMessage`, despite the
          `SignedPleaseAdd` being written to the introducer's own BACAP
          stream for the group and the `ReplyWho` being written to the BACAP
          stream the introducer is using to communicate with the new member.

          <span class="bold">**NOTE:**</span> We could send all of this information
          as part of the initial `Invitation`, but that would allow silent
          members to read other members' streams without them knowing it, which is an
          anti-goal.

        </div>

    </div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="opportunistic_acks"></span>Opportunistic acknowledgements and backfill

</div>

</div>

</div>

Pigeonhole storage is ephemeral: a box survives for roughly one to two weeks
before the replicas garbage-collect it (see "Ephemeral" in
<a href="/docs/pigeonhole_explained" class="link" target="_top">Understanding
Pigeonhole</a>). A reader is, of course, always free to advance past a
position it cannot yet fill and check further ahead instead of waiting there
indefinitely — deriving the position that follows one needs no knowledge of
what, if anything, was written at it (see "Optimistic resync" below). But
doing so cannot recover what was actually written at the position it
skipped: once a box has been garbage-collected, its content survives nowhere
but in its author's own memory of having written it. Reading past a gap is
therefore not the same as closing it. Nothing described so far in this
specification restores a box's content once it is gone.

<div class="itemizedlist">

- **Opportunistic acknowledgement.** Whenever a member sends any message to
  the group, for any of the reasons already described (`TextPayload`,
  `FileUpload`, `Introduction`, a `Who` / `ReplyWho` exchange), it may also
  carry, in the same message, an acknowledgement of the furthest box it has
  newly read on any other member's stream since it last acknowledged one.
  Acknowledgements are never sent as messages of their own: a member that has
  nothing else to say to the group has nothing to acknowledge either, and
  simply says nothing.

</div>

`GroupChatMessage` gains a field to carry them:

``` programlisting
// GroupChatMessage encapsulates all chat message types.
type GroupChatMessage struct {
    Version int
    MembershipHash *[32]byte

    TextPayload *TextPayload
    Introduction *Introduction
    FileUpload *FileUpload
    Who *Who
    ReplyWho *ReplyWho

    // Acks lists the BACAP MessageBoxIndex of the furthest box this
    // sender has newly read on each other member's stream since it
    // last acknowledged one. See "Opportunistic acknowledgements and
    // backfill".
    Acks [][]byte
}
```

<div class="itemizedlist">

- Each entry is a bare `MessageBoxIndex` (the 104-byte BACAP position value
  used elsewhere to address a box; see BACAP in §4 of the Echomix paper) —
  nothing else. No further label is carried, deliberately:

  <div class="itemizedlist">

  - The identity of the acknowledging member follows from which member's own
    stream the acknowledging message was itself read from. There is no
    broadcast channel in this design; every message already arrives
    attributed to its sender by the stream it was read on.
  - The identity of the acknowledged stream follows from the value itself.
    A `MessageBoxIndex` addresses one and only one position on one specific
    stream's BACAP ratchet, so a recipient recognises an entry as being
    "about me" simply by finding it, byte for byte, among the boxes it has
    itself written. An entry matching nothing a recipient has written is,
    from that recipient's point of view, addressed to some other member,
    and is otherwise ignored.

  </div>

- Because BACAP reading is sequential, acknowledging a stream's Nth box
  implies every earlier box on that stream has already been read too; a
  conforming implementation therefore need include, per acknowledged stream,
  only the single highest index newly read since its last acknowledgement.

</div>

**Sent-box records.** To make use of an acknowledgement, a stream owner is
expected to keep, for every box it has written to its own stream, a record of
that box's `MessageBoxIndex`, its position in write order, and — until every
current group member has acknowledged it — its plaintext.

<div class="itemizedlist">

- **Retention.** Once every other currently active group member has
  acknowledged a box, or a later one, its plaintext is no longer needed for
  delivery, since every current recipient already has it: an implementation
  MAY discard the plaintext at that point while still remembering the box's
  position, so that position can continue to be kept occupied (see
  "Optimistic resync" below). A record MUST eventually be discarded outright,
  regardless of acknowledgement, after a bounded retention window comfortably
  exceeding one replica epoch, so that a member who never acknowledges (an
  old client, or one that has permanently left) cannot oblige every other
  member to retain records indefinitely.
- **Backfill.** On recognising an acknowledgement of one of its own boxes, a
  stream owner rewrites — at the same index, with the same plaintext —
  every later box it still holds a record for. Pigeonhole writes are
  content-idempotent (rewriting a box that still holds the same content is
  accepted, not rejected; see "Append-only and immutable" in "Understanding
  Pigeonhole"), and BACAP's per-box encryption is deterministic (§4 of the
  Echomix paper), so rewriting a surviving box is a harmless no-op, while
  rewriting a box the replicas have garbage-collected restores it. This is
  the mechanism by which a stream, whose storage is otherwise ephemeral, is
  kept available for as long as the group continues to acknowledge it.
- **Rate-limiting the rewrite.** A rewrite is only useful once per replica
  epoch, since a box cannot be garbage-collected — and so cannot need
  restoring — more often than that. Implementations SHOULD NOT rewrite the
  same box more than once within a given replica epoch, however many
  acknowledgements name it, bounding the mixnet traffic a chatty or replayed
  acknowledgement can cause to a small, fixed multiple of the stream's own
  size, once per epoch, independent of how many acknowledgements arrive.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="optimistic_resync"></span>Optimistic resync

</div>

</div>

</div>

Backfill, above, is reactive: it triggers only on receiving an
acknowledgement naming a box. Two members each stalled behind a gap in the
other's stream can never trigger it for one another, since neither can read
far enough on the other's stream to produce a fresh acknowledgement in the
first place. Optimistic resync removes that dependency, on both ends, using
nothing beyond what is already used elsewhere in this specification and in
"Understanding Pigeonhole".

<div class="orderedlist">

1.  **Stream owner: periodic, unconditional refresh.** Independent of
    whether any acknowledgement has ever been received, a stream owner
    periodically — well within a replica epoch — rewrites every box it still
    holds a record of (Sent-box records, above), subject to the same
    once-per-epoch limit backfill already observes. A box whose plaintext
    has already been discarded (every acknowledging member's floor has
    passed it) is instead rewritten as a tombstone — an empty, signed
    payload, unconditionally accepted as an overwrite — rather than with its
    original content, since nobody who still needs it remains to be served;
    this keeps the position occupied without indefinitely retaining
    plaintext nobody needs. Either way, every position in the stream owner's
    stream stays populated rather than falling silently absent, however long
    any given reader has been stalled and whatever it has or has not
    acknowledged.

2.  **Reader: stall detection and forward scan.** A reader unable to advance
    past the same expected next box for longer than a bound (comfortably
    under a replica epoch, so the owner's refresh above has had a chance to
    run at least once) stops waiting on that one position and instead scans
    forward: it advances its own expected position past the stalled one —
    BACAP index derivation needs no network round trip and no knowledge of
    what, if anything, has been written at a position to compute the
    position that follows it (§4 of the Echomix paper) — and asks, for each
    successive position, whether reading it, without waiting out the
    ordinary retry a genuinely-not-yet-written box invites, yields data, a
    tombstone, or `BoxIDNotFound`:

    <div class="itemizedlist">

    - Data is a genuine message the reader had not yet received (perhaps
      very old); it is processed as any other message would be, and the
      scan continues past it.
    - A tombstone confirms something was once written at that position —
      either real content every current member already has, or a
      placeholder the owner's refresh maintains — and the scan continues
      past it, with nothing to process.
    - `BoxIDNotFound` is the true current end of the stream: nothing has
      ever been written there, and the reader resumes ordinary reading from
      that position.

    </div>

</div>

A pair of members each stalled behind the other therefore resynchronise
without either side ever needing to send a fresh acknowledgement: each one's
own stream stays populated by its own periodic refresh, and each one's own
stall eventually triggers its own forward scan past the other's gap.

This does not repair every possible loss: if both members' relevant records
have themselves aged out of retention (Sent-box records, above) before
either side's refresh or scan has run, there is nothing left for either side
to find.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="disappearing_messages"></span>Disappearing messages

</div>

</div>

</div>

Backfill and resync, above, exist to keep a stream owner's own messages
available for longer than Pigeonhole storage would otherwise guarantee.
Disappearing messages is the same mechanism, deliberately pointed the other
way: a stream owner may choose to actively shorten a message's life below
what storage would otherwise allow, tombstoning it before replica garbage
collection would have removed it regardless — trading the availability the
mechanisms above work to preserve for an earlier, deliberate end to a
message's life.

This is a purely local, unilateral choice: like the read progress tracked
elsewhere in this specification, it governs only what a member's own client
does with its own outbound stream, and is never negotiated with, or binding
on, any other member.

Two policies are defined. An implementation offering this feature MUST
support both, since they serve different intents and neither substitutes for
the other:

<div class="itemizedlist">

- **Ack-gated.** A box is tombstoned, and then no longer retained even as a
  placeholder for resync (above), once it, or a later box on the same
  stream, has been acknowledged by every other currently active group
  member — exactly the condition under which backfill's own retention
  (above) would otherwise merely discard the plaintext and keep a
  placeholder. This policy never destroys a box some active member has not
  yet acknowledged; a slow or temporarily unreachable member only delays
  deletion, never prevents it once they return.
- **Age-fraction.** A box is tombstoned once an elapsed fraction `f` of the
  replica epoch has passed since it was written, chosen by the sending
  member, regardless of whether anyone has acknowledged it. Because this
  policy can destroy a message no other member has yet read, that is a
  deliberate consequence of choosing it, not an oversight.

</div>

`f` MUST be constrained to `0 <= f < 1`. This is not a matter of taste: a box
written at replica-epoch time `t` cannot be garbage-collected by the
replicas before slightly more than one full replica epoch has elapsed after
`t`, however early or late within its own epoch `t` fell (see "Ephemeral" in
"Understanding Pigeonhole"). A retention shorter than one full replica epoch
— any `f < 1` — therefore always tombstones before replica garbage
collection could have removed the box regardless; `f >= 1` offers no such
guarantee, and can lose that race, defeating the entire purpose of choosing
this policy over simply waiting for storage to expire on its own.

Which message types a disappearing-message policy applies to — ordinary chat
content, as against membership or protocol messages such as `Introduction`
or `ReplyWho`, whose loss could affect other members' view of the group — is
left to be settled by implementations for now, rather than fixed here.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="d58e246"></span>Addenda

</div>

</div>

</div>

GOOD QUESTION: If we are adding a lot of people at once,do we really need to upload
all of
the members <span class="emphasis">*n*</span> times?

FUTURE WORK: Forward secrecy. We can add two extensions that allow transmitting public
keys + stuff encrypted under those public keys. We can also refer to the Reunion protocol
which is a <span class="emphasis">*n*</span>-way PAKE with strong anonymity properties. Reunion is
described in <a href="https://research.tue.nl/en/publications/communication-in-a-world-of-pervasive-surveillance-sources-and-me" class="link" target="_top">Communication in a world of pervasive surveillance: Sources and methods: Counter-strategies
against pervasive surveillance architecture</a>. Currently, <a href="https://codeberg.org/rendezvous/reunion/" class="link" target="_top">Python</a> and <a href="https://github.com/katzenpost/reunion/" class="link" target="_top">Go</a> implementations of Reunion are
available.

</div>

</div>
