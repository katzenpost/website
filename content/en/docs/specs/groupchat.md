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

**Sent-box records.** Making use of an acknowledgement depends on a second,
distinct kind of retention — not the replicas' own storage retention
(Pigeonhole storage is ephemeral, above), which no client controls, but the
stream owner's own client retaining, for every box it has written to its own
stream, a record of that box's `MessageBoxIndex`, its position in write
order, and — until every current group member has acknowledged it — its
plaintext.

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
- **Backfill.** A stream owner keeps every box it still holds a record of
  (Sent-box records, above) refreshed against garbage collection, for two
  different reasons that happen to produce the same rewrite. A box no
  active member has yet fully acknowledged is rewritten with its original
  plaintext, in case garbage collection beat a slow member to it. A box
  everyone has already acknowledged is instead rewritten as a tombstone —
  not because the content is still needed, but because a position left to
  quietly expire would later look, to a stalled reader, indistinguishable
  from one never written at all (see "Optimistic resync" below). Either
  rewrite is a harmless no-op against a box that survived and a restoration
  against one garbage-collected, because Pigeonhole writes are
  content-idempotent (see "Append-only and immutable" in "Understanding
  Pigeonhole") and BACAP's per-box encryption is deterministic (§4 of the
  Echomix paper). The trigger is always the periodic refresh described in
  "Optimistic resync" below; receiving an acknowledgement never itself
  causes a rewrite.
- **Rate-limiting the rewrite.** A rewrite is only useful once per replica
  epoch, since a box cannot be garbage-collected — and so cannot need
  restoring — more often than that. Implementations SHOULD NOT rewrite the
  same box more than once within a given replica epoch, however often the
  periodic refresh considers it, bounding the mixnet traffic backfill costs
  to a small, fixed multiple of the stream's own size.

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

The periodic refresh that makes backfill (above) possible is also the
stream owner's half of resynchronising two members each stalled behind a
gap in the other's stream; the reader's half is a stall detector and a
scan. Together they need nothing beyond what is already used elsewhere in
this specification and in "Understanding Pigeonhole".

<div class="orderedlist">

1.  **Stream owner: periodic refresh.** Well within a replica epoch, a
    stream owner re-examines every box in Sent-box records (above) and,
    subject to the once-per-epoch limit above, rewrites whichever are due —
    real content or a tombstone, exactly as Backfill (above) determines —
    independent of whether, or how promptly, anyone has acknowledged
    anything. Every position in the stream stays populated, however long
    any reader has been stalled.

2.  **Reader: stall detection and scan.** A reader unable to advance past
    the same expected next box for longer than a bound (comfortably under a
    replica epoch, so the refresh above has had a chance to run) stops
    waiting there and looks both ways. It rechecks a short trailing window
    of positions it has already passed, using index values retained from
    when it read them — a BACAP index is a KDF ratchet state, so it can
    only be advanced, never recovered backward (§4 of the Echomix paper),
    which is why revisiting one requires having kept it; this catches, for
    instance, a box a replica had not finished replicating on an earlier
    attempt. It also scans forward past the stalled position: deriving each
    next index from the last needs no network round trip and no knowledge
    of what, if anything, was written there, so the reader can keep
    deriving positions and asking, for each, without waiting out the
    ordinary retry a genuinely-not-yet-written box invites, whether it holds
    data, a tombstone, or nothing:

    <div class="itemizedlist">

    - Data is a genuine message the reader had not yet received; it is
      processed as any other message would be, and the scan continues past
      it.
    - A tombstone confirms something was once written there — real content
      everyone already has, or a placeholder the refresh above maintains —
      and the scan continues past it.
    - `BoxIDNotFound` is the true current end of the stream: adopt this
      position as the new expected next box, clear the stall, and resume
      ordinary reading.

    </div>

</div>

Two members each stalled behind the other therefore resynchronise without
either side ever needing to send a fresh acknowledgement: each one's own
stream stays populated by its own refresh, and each one's own stall
eventually triggers its own scan past the other's gap. As long as each side
comes back online at least once per replica epoch, recovery always
eventually completes: the refresh never lets a position go a full epoch
unrefreshed, so garbage collection never gets ahead of it. The Sent-box
retention window (Sent-box records, above; comfortably longer than a
replica epoch) is not a limit on this — it exists only so that a member who
has stopped coming back at all, ever, is eventually forgotten rather than
held onto forever.

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
