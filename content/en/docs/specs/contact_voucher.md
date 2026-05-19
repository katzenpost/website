---
title: "Contact voucher design"
linkTitle: "Contact voucher design"
description: ""
author: ""
url: ""
date: "2026-05-13T18:07:12.574908781-07:00"
draft: "false"
slug: "contact_voucher"
layout: ""
type: ""
weight: "1"
version: ""
---

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="voucher"></span>

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">Threebit</span> <span class="surname">Hacker</span>

</div>

<div class="author">

### <span class="firstname">Leif</span> <span class="surname">Ryge</span>

</div>

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

In order to join or initiate a conversation, participants need to exchange cryptographic
key
material. To address this problem, we created a slightly unusual design: <span class="emphasis">*contact
vouchers*</span>.

In many systems, invites to conversations flow from an existing member of the conversation
to the user being invited. In our contact voucher protocol, this flow is reversed:
Bob, who
wishes to join a conversation, hands a contact voucher (out-of-band) to existing member
Alice,
who then inducts Bob into the group.

This design mitigates two potential problems with the conventional way of doing things:

<div class="orderedlist">

1.  A third party who observes the contact voucher does not get to read either participant's
    actual messages. However,

    <div class="itemizedlist">

    - A <span class="strong">**passive**</span> adversary learns that the voucher was
      spent, but does not get to observe further interactions.

    - An <span class="strong">**active**</span> adversary can create a new fake group
      to induct the member into, but does not learn anything about the existing group.

    </div>

    In the future, to prevent this one-way impersonation, we could require that Alice
    and
    Bob both bring something on paper to their meeting.

    <div class="itemizedlist">

    - Bob brings the contact voucher.

    - Alice brings a fingerprint for the `VoucherReplyPublicKey` (thwarting the
      active attacker).

    </div>

2.  Only one thing that needs to delivered out-of-band to achieve a two-pass protocol
    (instead of a three-pass protocol):

    <div class="itemizedlist">

    - One of the parties needs to bring key material to a meeting in order to establish
      contact.

    </div>

</div>

The following diagram illustrates the contact voucher authentication handshake.

<div class="mediaobject">

```mermaid
sequenceDiagram
    actor Bob
    participant VoucherSeq@{ "type" : "database" }
    actor Alice
    Bob-->>+Bob: Generates VoucherKeypair. <br>Generates BACAP write/read cap.<br>VoucherPayload := read cap || VoucherPublicKey<br>Voucher := Hash(VoucherPayload)
    Bob->>+VoucherSeq: Publish: VoucherPayload
    Bob-->>Alice: [Sent OOB] Voucher


    Alice-->>+Alice: Derive VoucherSeq read/write caps from Voucher.<br>Read the first box in VoucherSeq
    VoucherSeq->>+Alice: VoucherPayload
 
    Alice-->>+Alice: VoucherReply := Encrypt(WhoReply + VoucherSalt)<br> to VoucherPublicKey<br><br>Derive Bob's ReadCap from<br>VoucherPayload + VoucherSalt
    par_over All-Or-Nothing using COPY service
    Alice->>+VoucherSeq: VoucherReply
    Alice->>+Alice's Group: WhoReply<br>(incl. Bob's new ReadCap)
    Alice->>+VoucherSeq: Tombstone VoucherPayload<br>to prevent Voucher reuse
    end

    Bob-->>+Bob: Poll the second VoucherSeq box until Alice replies
    VoucherSeq->>+Bob: VoucherReply
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="d58e83"></span>Self-authenticating BACAP payload

</div>

</div>

</div>

The first message sent, the `VoucherPayload`, is authenticated in the following
manner:

<div class="itemizedlist">

- The `VoucherPayload` is computed (first).

- A cryptographic hash of the `VoucherPayload` is computed. This hash
  <span class="strong">**is**</span> the `Voucher`.

- The `Voucher` is then used to derive a BACAP read/write capability set.

- The `VoucherPayload` is uploaded to the sequence described by the
  capability (at index 0).

- Anyone who intercepts the `Voucher` can read from <span class="strong">**and**</span> write to the message sequence.

- But: Since the `Voucher` is a hash over the `VoucherPayload`,
  writing the sequence with anything but the `VoucherPayload` will be detectable
  by the recipient.

- This means that the contents <span class="emphasis">*cannot*</span> be undetectably modified by
  the interceptor.

</div>

</div>

</div>
