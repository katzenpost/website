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

  - the index of the next box to read, kept separately from the readcap

  - a nickname

  </div>

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
members, each with the index to start reading at.

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
          for all existing members, each with the index to start reading at.

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

Pigeonhole boxes are garbage-collected after one to two weeks (see
"Ephemeral" in <a href="/docs/pigeonhole_explained" class="link" target="_top">Understanding
Pigeonhole</a>). After that, only the author has the content. Acknowledgements
tell the author what to restore.

Any group message may carry acknowledgements. None is sent on its own.
`GroupChatMessage` gains one field:

``` programlisting
type GroupChatMessage struct {
    Version int

    TextPayload *TextPayload
    Introduction *Introduction
    FileUpload *FileUpload
    Who *Who
    ReplyWho *ReplyWho

    Acks []byte
    Numbers []byte
    IntroducedAt []byte
}
```

This new `Acks` field is a mapping from roster indexes (see Rosters below) to BACAP
`MessageBoxIndex` values. Its encoding is described in
<a href="#acks_wire_format" class="link">Acks wire format</a>.
Acks is nil when we don't have anything to acknowledge. `Numbers` and
`IntroducedAt` keep rosters in step; they are described under Rosters below.

`TextPayload` and `FileUpload` are content. `Introduction`, `Numbers` and
`IntroducedAt` are control. A message carries either content or control,
never both. The retention policy deletes content only (see
<a href="#disappearing_messages" class="link">Disappearing messages</a>), so
a message that changes a roster stays readable for as long as its Sent-box
record lasts.

Throughout this specification we use roster indexes as the channel
identities. Alice keeps a list of the channels she has numbered and refers
to each by its place in that list, counting from 0: 0 is Alice herself, 1
is the next member she numbered, and so on. One byte names a member, which
keeps acknowledgements small.

<div class="itemizedlist">

- Each value in the key-value mapping is the 104-byte `MessageBoxIndex` of the furthest box newly
  read on that member's stream. BACAP reading is sequential, so this
  acknowledges every earlier box too.
- The acknowledging member is whoever's stream carried the message.
- A stream owner checks each claimed index against its Sent-box records and
  ignores one matching nothing it wrote.

</div>

**Rosters.** Members are named by one-byte roster indexes, not public keys,
to save bytes on constrained transports such as LoRa.

<div class="itemizedlist">

- **Roster.** Each member keeps an ordered list of the members it has
  numbered, itself included. A member's roster index is its position in
  that list. Entries are never moved or reused, so a roster holds at most
  256 members ever. Every member keeps a copy of every other member's
  roster. A member's identity is its read-cap public key.
- **Starting.** A lone founder's roster holds only itself. Co-founders
  each start with all founders in ascending order of read-cap public key. A
  new member starts with a copy of its introducer's roster as of the
  `Introduction` announcing it.
- **Numbering.** A member numbers another by appending it to its roster,
  taking its next unused index, and announcing the assignment in the
  `Numbers` field of a control message. Each entry states the index
  assigned and the `Introduction` that introduced the member: its
  introducer's roster index and the `Introduction`'s position on the
  introducer's stream. An introducer numbers the new member in the message
  carrying its `Introduction`. Every other member numbers a new member
  after reading its `Introduction`, and MUST do so before acknowledging the
  new member's stream. Entries are in ascending order of index.
- **Watching.** A reader learns each sender's roster from that sender's
  `Numbers`. Until the reader has read the `Introduction` an entry names,
  the member at that index is unresolved.
- **Introduced at.** A new member learns where its `Introduction` landed
  by reading its introducer's stream, and its next message after that is a
  control message carrying `IntroducedAt`: its introducer's roster index
  and the position of the `Introduction` it joined through. A member can be
  introduced more than once, so readers take the new member's starting
  roster from the `Introduction` that `IntroducedAt` names. Until they have
  read it, the new member's roster is unknown and its acknowledgements are
  skipped.
- **Repeats.** A member already in a roster is never added again.
- **Reply to a new member.** The reply is built before the new member's
  read cap or its `Introduction`'s position is known, so it names the new
  member only by the index it will take. The reply carrying the group's read caps, each
  with its start index (`ReplyWho`, or `WhoReply` in the contact voucher
  protocol), lists them in
  the introducer's roster order, so position equals roster index. A
  removed member's slot is sent empty. The reply also carries every
  member's roster, as the introducer has followed it, sent once:

  ``` programlisting
  // Rosters holds each member's roster, in introducer roster order.
  // Each byte is the introducer's roster index for that entry.
  Rosters [][]byte
  ```

- **Reading.** Resolve each index against the sender's roster. Skip values
  at unresolved indexes. Roster indexes MUST NOT be compared across
  senders.
- **Skipped boxes.** A reader that skips a box may miss a `Numbers`
  entry. Every entry states its index, so later entries still land in
  place, and the missed index stays unresolved.
- **Removal.** A member may silently stop reading a stream. It keeps the
  roster entry, MUST NOT acknowledge that index again, and MUST NOT reuse
  it. It no longer waits for the removed member's acknowledgements before
  discarding plaintext. The removed member keeps its read caps.

</div>

**Sent-box records.** A stream owner records, for each box it wrote, its
`MessageBoxIndex`, its position, and its plaintext until every member has
acknowledged it or its retention policy deletes the plaintext (see
<a href="#disappearing_messages" class="link">Disappearing messages</a>).

<div class="itemizedlist">

- **Retention.** Once every other active member has acknowledged a box,
  its plaintext MAY be discarded, but its position is kept. Records MUST be
  discarded after a bounded window exceeding one replica epoch, so absent
  members cannot force retention forever.
- **Backfill.** The owner periodically rewrites every recorded box:
  boxes whose plaintext it still has with that plaintext, and the rest as
  tombstones, so the position still reads as written. Rewrites are
  idempotent since Pigeonhole writes are content-idempotent and BACAP
  encryption is deterministic. Acknowledgements never trigger a rewrite.
- **Rate limit.** Implementations SHOULD NOT rewrite a box more than once
  per replica epoch.

</div>

**Joining.** A new member receives its introducer's view of the group as of
the `Introduction`: a read cap and a start index for every member's stream
in the introducer's roster, and the rosters the introducer knew about (see
Reply to a new member). Read caps are sent unchanged; the index travels
beside them and is advanced separately.

<div class="itemizedlist">

- **Catching up.** Before an invitation begins, the introducer reads every
  stream to its end, scanning any it is stuck on (see
  <a href="#rewrite_and_scan" class="link">Rewrite and scan</a>).
- **Start positions.** Each start index is the box after where the
  introducer had read that stream when the invitation began, and the
  introducer's own is the `Introduction`.
- **Holding back.** From the start of an invitation until the
  all-or-nothing commit that writes the `Introduction`, the introducer
  sends no acknowledgements and numbers no one. Its published
  acknowledgements then stop short of every start index, and its roster
  stays as the reply describes it.
- **Retention.** A member that reads an `Introduction` keeps every box of
  its own stream that the introducer had not acknowledged at that point,
  until the new member acknowledges it or the member's retention policy
  deletes it.
- **No race.** Members read the introducer's stream in order, so each sees
  the `Introduction` before any acknowledgement that would let it discard
  a box the new member was given.
- **History.** Older history is sent from the introducer's own copy, never
  by starting a stream earlier.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="acks_wire_format"></span>Acks wire format

</div>

</div>

</div>

We encode the `Acks` mapping by hand as a byte slice rather than as a CBOR map. The
motivation is to let this protocol run over constrained pipes, such as
LoRa radio links, where every byte counts.

Let `n` be the number of entries. Every value is a
104-byte `MessageBoxIndex`, so the values cost `104n` bytes in any
encoding. Only the cost of naming the keys varies.

<div class="itemizedlist">

- **Simplest.** A list of (roster index, value) pairs. The keys cost one
  byte each, `n` bytes in total.
- **Bitmap.** A bitmap with one bit per roster index, followed by the
  values in ascending roster index order. Let `b` be the bytes a bitmap
  needs to reach the highest acknowledged index; `b` is at most 32. The
  keys cost `b` bytes. This beats the list when many members are
  acknowledged at once.
- **Most compact.** Use whichever of the two key encodings is shorter:
  `min(n, b)` bytes. No length prefix or type tag is needed, because both
  can be inferred from the field length (see Parsing). This is the
  encoding `Acks` uses.

</div>

For example, if the highest acknowledged index is 19, the bitmap is 3
bytes. Acknowledging 3 members then costs 3 key bytes either way;
acknowledging 10 costs 10 as a list but only 3 as a bitmap.

The most compact encoding is defined as follows.

<div class="itemizedlist">

- **Layout.** `Acks` is the keys followed by the values in ascending
  roster index order. If `n <= b`, the keys are a list of `n` index bytes
  in ascending order. Otherwise they are a `b`-byte bitmap where index `i`
  is bit `i mod 8`, counting from the most significant bit, of byte
  `i div 8`.
- **Parsing.** Divide the field length by 104: the quotient is `n` and the
  remainder is the key length. A remainder equal to `n` means a list;
  smaller means a bitmap. This works because keys are at most 32 bytes,
  shorter than one value. A parser MUST ignore the whole field if the
  remainder exceeds `n`, a list is not strictly ascending, a bitmap's last
  byte is zero, a bitmap does not have exactly `n` bits set, or a bitmap
  exceeds 32 bytes.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="numbers_wire_format"></span>Numbers and IntroducedAt wire format

</div>

</div>

</div>

`Numbers` and `IntroducedAt` are encoded by hand for the same constrained
pipes as `Acks`.

<div class="itemizedlist">

- **Numbers.** A sequence of 10-byte entries in ascending order of index.
  Each entry is the roster index assigned (1 byte), the introducer's
  roster index in the sender's roster (1 byte), and the position of the
  `Introduction` on the introducer's stream, the 8-byte little-endian
  counter of its `MessageBoxIndex`. In a message carrying an
  `Introduction`, the entry for the member it introduces has position 0,
  meaning that `Introduction`: its own position is not known when it is
  encoded, and stream counters start at a random point, so no real box is
  at 0. A parser MUST ignore the whole field if its length is not a
  multiple of 10 or its indexes are not strictly ascending.
- **IntroducedAt.** One entry without its first byte: 9 bytes.

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="rewrite_and_scan"></span>Rewrite and scan

</div>

</div>

</div>

A reader cannot tell a quiet stream from one stuck behind a
garbage-collected box by reading it: both return `BoxIDNotFound`.
Acknowledgements tell them apart. If any member has acknowledged a stream
beyond a reader's position, there is more to read and the reader is stuck.

<div class="orderedlist">

1.  **Periodic rewrite.** Well within each replica epoch, the stream owner
    rewrites due boxes (see Backfill), keeping every position populated.

2.  **Kept indexes.** A reader keeps the `MessageBoxIndex` of each position
    it passed without data, a tombstone or a skipped box, for a short
    window behind its position. BACAP indexes cannot be derived backward,
    so an index is kept as it is passed.

3.  **Scan.** The reader rechecks its kept indexes and ingests any box now
    readable. If a member has acknowledged the stream beyond the reader's
    position, the reader jumps to the furthest acknowledged box, deriving
    and keeping the indexes of the boxes it skips. It then probes forward
    without waiting between positions: data is ingested, a tombstone is
    skipped, and the first `BoxIDNotFound` becomes the new expected
    position, ending the scan.

4.  **When to scan.** An implementation MAY scan automatically when another
    member has acknowledged the stream beyond the reader's position.
    Otherwise it MUST NOT scan automatically. It MAY show how long the
    stream has been quiet, and the user requests a scan, one stream at a
    time.

</div>

Two members stuck behind gaps in each other's streams resynchronise once
both scan, provided they do so within the owner's Sent-box retention window.
A reader stuck behind boxes that are gone for good resumes at the furthest
acknowledged box and loses the boxes it skipped.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="disappearing_messages"></span>Disappearing messages

</div>

</div>

</div>

Disappearing messages is the feature that causes a user's client to remove messages from the client's state database
based on a user specified message retention policy. For example, a client's message retention policy could keep
decrypted plaintext messages from other members for X number of days. Likewise policy could retain sent message
plaintext for Y number of days.

The retention policy applies to content only. Control messages are kept for
as long as their Sent-box records last, so a message that disappears never
takes a roster change with it.

Once a client makes a message "disappear" as per this feature, then after that point in time
the client can never retransmit that box. Backfill rewrites it as a tombstone instead.
The tombstone in place of the box is still very useful for resyncing.
A member that reaches a tombstone at a position it has not yet read can also tell from it
that it didn't read your message in time before your client's retention policy purged the plaintext data.

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

OPEN PROBLEM: Our BACAP API defines a ReadCap type as containing
the master public key AND the start index. Therefore whenever we send a readcap over the wire
we are needlessly sending a start index even when we don't need it anymore. We should
probably fix this, especially given that our goal is to be as bandwidth efficient as possible.

FUTURE WORK: Forward secrecy. We can add two extensions that allow transmitting public
keys + stuff encrypted under those public keys. We can also refer to the Reunion protocol
which is a <span class="emphasis">*n*</span>-way PAKE with strong anonymity properties. Reunion is
described in <a href="https://research.tue.nl/en/publications/communication-in-a-world-of-pervasive-surveillance-sources-and-me" class="link" target="_top">Communication in a world of pervasive surveillance: Sources and methods: Counter-strategies
against pervasive surveillance architecture</a>. Currently, <a href="https://codeberg.org/rendezvous/reunion/" class="link" target="_top">Python</a> and <a href="https://github.com/katzenpost/reunion/" class="link" target="_top">Go</a> implementations of Reunion are
available.

</div>

</div>
