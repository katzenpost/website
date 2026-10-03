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

Pigeonhole storage is ephemeral: a box survives roughly one to two weeks
before replicas garbage-collect it (see "Ephemeral" in
<a href="/docs/pigeonhole_explained" class="link" target="_top">Understanding
Pigeonhole</a>). A reader can always skip a position it cannot fill and
check further ahead: deriving the next position needs no knowledge of
what, if anything, is at the current one (see "Rewrite and scan" below).
But that cannot recover what was actually written there: once
garbage-collected, a box's content survives only in its author's memory of
writing it. Reading past a gap is not the same as closing it; nothing so
far in this specification restores lost content.

<div class="itemizedlist">

- **Opportunistic acknowledgement.** Any message a member sends to the group
  (`TextPayload`, `FileUpload`, `Introduction`, a `Who` / `ReplyWho`
  exchange) may also carry an acknowledgement of the furthest box it has
  newly read on another member's stream since it last acknowledged one.
  Acknowledgements are never sent on their own: a member with nothing else
  to say has nothing to acknowledge either.

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

    // Acks maps a channel prefix (the shortest prefix of an acknowledged
    // member's read-cap public key that this sender can tell apart from
    // every other member it holds; see "Channel prefixes") to the BACAP
    // MessageBoxIndex of the furthest box this sender has newly read on
    // that member's stream since it last acknowledged one. The key is
    // encoded as a CBOR byte string, not a text string.
    Acks map[string][]byte
}
```

<div class="itemizedlist">

- Each key is a **channel prefix**: the shortest prefix of the
  acknowledged member's read-cap public key that is a prefix of no other
  read cap the sender holds, never shorter than one byte (see "Channel
  prefixes" below). The public key it abbreviates is the part of a cap
  that stays stable across every index-mutation variant (original,
  salt-mutated, future-only), unlike the cap's own index suffix, and it
  remains the member's identity; the prefix only names that member within
  the one message carrying it. A stream owner recognises its own
  acknowledgement by one test: is some key a prefix of its own public key.
- Each value is the raw `MessageBoxIndex` (the 104-byte BACAP position
  value used elsewhere to address a box; §4 of the Echomix paper), nothing
  else, naming the furthest box newly read on that member's stream.
- The *acknowledging* member's identity (as against the acknowledged one,
  above) still comes from which member's own stream carried the message:
  with no broadcast channel in this design, a message already arrives
  attributed to its sender, whatever channel prefixes its `Acks` keys name.
- A channel prefix is not secret (every member already holds every other
  member's read cap, to read their stream), so a stream owner still checks
  a claimed index against its own Sent-box records (below): one matching
  nothing it actually wrote is ignored, stale, forged, or misattributed
  (see "Channel prefixes") alike.
- Because BACAP reading is sequential, acknowledging a stream's Nth box
  implies every earlier one has already been read; a conforming
  implementation therefore need only include, per stream, the single
  highest index newly read since its last acknowledgement.

</div>

**Channel prefixes.** A key abbreviates a member's read-cap public key
rather than carrying it whole because a message may acknowledge every
member the sender has read, and this protocol is meant eventually to
cross transports (LoRa, for one) where every byte of a group message
counts. A prefix is chosen by the sender alone, against the sender's own
current view of the group, with no agreement among members and nothing
announced in advance.

<div class="itemizedlist">

- **Choosing.** For each member it acknowledges, the sender takes the
  shortest prefix of that member's read-cap public key that is a prefix
  of no other read cap it holds, and never less than one byte. Public
  keys being uniformly random, this is one byte for nearly every member
  of a group under about thirty and two bytes beyond: among `n` members
  about `n²/512` pairs share a first byte. Prefixes are recomputed for
  every message, so when the sender learns of a member whose key shares
  a prefix with one it already acknowledges, both lengthen on their own
  and readers need no notice of it.
- **Claiming.** A stream owner claims an entry if, and only if, its key
  is a prefix of the owner's own read-cap public key. That is the whole
  rule. An owner MUST NOT reject an entry for being shorter than the
  owner itself would have chosen: doing so would refuse genuine
  acknowledgements from every sender that has not yet learned of some
  colliding member, to prevent a rarer misattribution instead.
- **Resolving.** A prefix is not an identifier and MUST NOT be stored or
  compared as one. A reader resolves each key afresh against the members
  it holds at the time, and the same member may be named by prefixes of
  different lengths in successive messages from one sender.
- **Misattribution.** Because members' views of the group are only
  eventually consistent, an entry can be claimed by the wrong member:
  exactly when the acknowledged member and some other member share a
  prefix and the sender does not yet know that other member. The window
  closes as soon as the sender learns of them. Within it the claimed
  index names a box on the acknowledged member's stream, so it matches
  nothing the wrong claimant ever wrote and the Sent-box check above
  discards it. Any future shortening of the value weakens that check in
  proportion.
- **Divergence.** A key that matches no member the reader holds, one
  that matches more than one, or one longer than the reader would itself
  have chosen each tells the reader that the sender's view of the group
  differs from its own: the sender holds a member the reader lacks,
  lacks one the reader holds, or holds a colliding member the reader
  lacks, respectively. The protocol does not act on this; an
  implementation MAY surface it.
- **Grinding.** Read-cap public keys are self-chosen, so a member can
  pick one sharing a long prefix with another member's. That costs
  everyone a longer prefix for those two members and nothing else:
  claiming stays by prefix of one's own key, and the Sent-box check
  stands.

</div>

**Sent-box records.** Making use of an acknowledgement depends on a second,
distinct kind of retention: not the replicas' storage retention
(Pigeonhole storage is ephemeral, above), which no client controls, but the
stream owner's own client keeping, for every box it has written, a record
of its `MessageBoxIndex`, its write-order position, and, until every
current member has acknowledged it, its plaintext.

<div class="itemizedlist">

- **Retention.** Once every other active member has acknowledged a box, or
  a later one, its plaintext is no longer needed for delivery: an
  implementation MAY discard it, while still remembering the box's
  position so it stays occupied (see "Rewrite and scan" below). A record
  MUST eventually be discarded outright, regardless of acknowledgement,
  after a bounded window comfortably exceeding one replica epoch, so a
  member who never acknowledges (an old client, or one gone for good)
  cannot force every other member to retain records forever.
- **Backfill.** A stream owner keeps every box in its Sent-box records
  rewritten against garbage collection, for two reasons that produce the
  same rewrite. A box no active member has fully acknowledged is rewritten
  with its original plaintext, in case garbage collection beat a slow
  member to it. A box everyone has acknowledged is instead rewritten as a
  tombstone: not because it's still needed, but because a position left
  to expire would later look, to a reader, indistinguishable from one
  never written (see "Rewrite and scan" below). Either rewrite is
  harmless: a no-op if the box survived, a restoration if it didn't,
  because Pigeonhole writes are content-idempotent ("Append-only and
  immutable" in "Understanding Pigeonhole") and BACAP's per-box encryption
  is deterministic (§4, Echomix). The trigger is always the periodic
  rewrite described in "Rewrite and scan"; an acknowledgement never itself
  causes a rewrite.
- **Rate-limiting the rewrite.** A rewrite is only useful once per replica
  epoch, since a box can't be garbage-collected (and so can't need
  restoring) more often than that. Implementations SHOULD NOT rewrite the
  same box more than once per epoch, however often the periodic rewrite
  considers it, bounding backfill's mixnet traffic to a small, fixed
  multiple of the stream's own size.

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

The periodic rewrite that makes backfill possible is also the stream
owner's half of resynchronising two members each stuck behind a gap in the
other's stream. The reader's half is a scan. Unlike the periodic rewrite,
though, the client cannot safely decide on its own when to run it.

Nothing observable from a reader's side distinguishes a stream that has
simply gone quiet (completely ordinary, and can last indefinitely) from
one stuck behind a position that was written and then garbage-collected:
both look identical, forever, as the same repeated `BoxIDNotFound`, which
means only "nothing has ever been written here," not whether that's
because nothing has been written *yet* or because it once was and is now
gone. No threshold turns that ambiguity into reliable detection: a short
one scans streams that were never stuck, a long one is merely slow to
react to a real gap, and neither ever tells the reader which case it's in.
An implementation MAY show the user how long a stream has gone quiet, but
MUST NOT use that to trigger a scan itself: the decision is the user's,
made with context (how well they know the other member, other contact,
plain suspicion) that no protocol-level signal has. Concretely, a
conforming client exposes a scan as something the user asks for, one
stream at a time, not as a background behaviour.

<div class="orderedlist">

1.  **Stream owner: periodic rewrite.** Well within a replica epoch, a
    stream owner re-examines every box in its Sent-box records and,
    subject to the once-per-epoch limit above, rewrites whichever are due
    (content or tombstone, as Backfill determines) regardless of
    acknowledgements or scan requests. Every position stays populated,
    however long since a reader last looked.

2.  **Reader: scan, on request.** Once the user asks their client to scan
    a stream, it looks both ways from the stuck position. It rechecks a
    short trailing window it has already passed, using index values kept
    from when it read them: a BACAP index only advances, never recovers
    backward (§4 of the Echomix paper), so revisiting one needs its value
    kept. This catches, say, a box a replica hadn't finished replicating.
    It also scans forward: deriving each next index needs no network round
    trip and no knowledge of what's there, so the client keeps deriving
    and asking, for each, without waiting out the ordinary not-yet-written
    retry, whether it holds data, a tombstone, or nothing:

    <div class="itemizedlist">

    - Data is a genuine, unreceived message: process it normally and
      continue past it.
    - A tombstone confirms something was once written there (real content
      everyone already has, or a placeholder the periodic rewrite
      maintains), and the scan continues past it.
    - `BoxIDNotFound` is the true current end of the stream: adopt this
      position as the new expected next box and resume ordinary reading.

    </div>

</div>

Item 2 is a small state machine with exactly two states:

``` programlisting
Reading --the user requests a scan--> Scanning --BoxIDNotFound (the true frontier)--> Reading

(Reading self-loops on Data, Tombstone, and BoxIDNotFound: ordinary
reading, unchanged. Scanning self-loops on Data and Tombstone, each
just advancing the probe.)
```

| State    | On                                          | Next state | Effect                                                       |
|----------|----------------------------------------------|------------|----------------------------------------------------------------|
| Reading  | Data or Tombstone at the expected position    | Reading    | advance the expected position by one (ingest a `Data` message) |
| Reading  | `BoxIDNotFound` at the expected position      | Reading    | none: ordinary reading, unchanged                               |
| Reading  | the user requests a scan                      | Scanning   | reprobe the short trailing window behind; probe forward         |
| Scanning | Data at a probed position                     | Scanning   | ingest it; probe the next position forward                      |
| Scanning | Tombstone at a probed position                | Scanning   | probe the next position forward                                 |
| Scanning | `BoxIDNotFound` at a probed position           | Reading    | adopt this position as the expected next box                    |
| Scanning | the user requests a scan again                | Scanning   | none: already scanning                                          |

The backward reprobe on entering Scanning is a one-time side check, not a
state of its own: whatever it turns up is ingested like ordinary reading,
and doesn't affect which transition fires.

Two members each stuck behind a gap in the other's stream resynchronise
once each has asked their own client to scan: each one's stream stays
populated by its own periodic rewrite, so there is always something for a
scan to find. This is not automatic (recovery happens on request, not on
its own or promptly), and it depends on asking before the stream owner's
Sent-box retention window (above; comfortably longer than a replica epoch)
lets the position go: that window bounds not how long a scan may take, but
how long after the fact anything can still be found.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="disappearing_messages"></span>Disappearing messages

</div>

</div>

</div>

Backfill and the periodic rewrite, above, keep a stream owner's messages
available longer than Pigeonhole storage would otherwise guarantee.
Disappearing messages points the same mechanism the other way: a stream owner may
shorten a message's life instead, tombstoning it before replica garbage
collection would have removed it regardless. This trades the availability
the mechanisms above preserve for an earlier, deliberate end.

This is a purely local, unilateral choice: like read progress elsewhere in
this specification, it governs only a member's own outbound stream, and is
never negotiated with, or binding on, anyone else.

Two policies are defined; an implementation offering this feature MUST
support both, since they serve different intents and neither substitutes
for the other:

<div class="itemizedlist">

- **Ack-gated.** A box is tombstoned, and no longer even kept as a
  placeholder (above), once it or a later box on the same stream has been
  acknowledged by every other active member (exactly the condition under
  which Backfill's retention would otherwise just discard the plaintext).
  This never destroys a box some active member hasn't yet acknowledged; a
  slow or unreachable member only delays deletion, never prevents it.
- **Age-fraction.** A box is tombstoned once a sender-chosen fraction `f`
  of the replica epoch has elapsed since it was written, regardless of
  acknowledgement. This can destroy a message no other member has yet
  read: a deliberate consequence of choosing this policy, not an
  oversight.

</div>

`f` MUST be constrained to `0 <= f < 1`. This is not a matter of taste: a
box written at replica-epoch time `t` cannot be garbage-collected before
slightly more than one full epoch has elapsed after `t`, however early or
late within its own epoch `t` fell (see "Ephemeral" in "Understanding
Pigeonhole"). Any `f < 1` therefore always tombstones before garbage
collection could have removed the box regardless; `f >= 1` offers no such
guarantee and can lose that race, defeating the point of choosing this
policy over just waiting for storage to expire.

Which message types a disappearing-message policy applies to (ordinary
chat content, as against membership or protocol messages such as
`Introduction` or `ReplyWho`, whose loss could affect other members' view
of the group) is left to implementations for now, rather than fixed here.

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
