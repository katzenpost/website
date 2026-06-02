---
title: ""
linkTitle: "Contact voucher"
description: ""
author: ""
url: ""
date: "2026-06-02T10:58:46.445685453-07:00"
draft: "false"
slug: "contactvoucher"
layout: ""
type: ""
weight: "15"
version: ""
---

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="voucher"></span>Contact voucher specification

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

<div>

<div class="abstract">

**Abstract**

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

In order to join or initiate a conversation securely, participants need to exchange
cryptographic key material. To address this problem, we created a slightly unusual
design:
<span class="emphasis">*contact vouchers*</span>.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="voucher-design"></span>Voucher design

</div>

</div>

</div>

In many systems, an invitation to communicate flows from an existing member of a
conversation to the user being invited. In our contact voucher protocol, this flow
is
reversed: Bob, who wishes to join a conversation, hands a contact voucher (out-of-band)
to
existing member Alice, who then inducts Bob into the group.

This design mitigates two potential problems with the conventional way of doing things:

<div class="orderedlist">

1.  A third party who observes the contact voucher does not get to read either
    participant's actual messages. However,

    <div class="itemizedlist">

    - A <span class="bold">**passive**</span> adversary learns that the voucher was
      spent, but does not get to observe further interactions.

    - An <span class="bold">**active**</span> adversary can create a new fake group
      to induct the member into, but does not learn anything about the existing group.

    </div>

    In the future, to prevent this one-way impersonation, we could require that Alice
    and
    Bob both bring something on paper to their meeting.

    <div class="itemizedlist">

    - Bob brings the contact voucher.

    - Alice brings a fingerprint for the `VoucherReplyPublicKey` (thwarting
      the active attacker).

    </div>

2.  Only one thing that needs to delivered out-of-band to achieve a two-pass protocol
    (instead of a three-pass protocol):

    <div class="itemizedlist">

    - One of the parties needs to bring key material to a meeting in order to establish
      contact.

    </div>

</div>

The following diagram illustrates the contact voucher authentication handshake.

<div class="figure">

<span id="d58e83"></span>

**Figure 1. Contact voucher handshake**

<div class="figure-contents">

<div class="mediaobject">

![Bob and Alice exchange cryptographic information with the mixnet as proxy. They never have direct contact again after their initial meeting in real life.](/docs/specs/pix/contact-voucher.jpg)

</div>

</div>

</div>

  

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="payload"></span>Self-authenticating BACAP payload

</div>

</div>

</div>

The first message sent, the `VoucherPayload`, is authenticated in the following
manner:

<div class="orderedlist">

1.  The `VoucherPayload` is computed.

2.  A cryptographic hash of the `VoucherPayload` is computed. This hash
    <span class="strong">**is**</span> the <span class="emphasis">*Voucher*</span>.

3.  The <span class="strong">**Voucher**</span> is used to derive a BACAP
    read/write capability set.

4.  The `VoucherPayload` is uploaded to the BACAP sequence described by
    the capability (at index 0).

5.  Anyone who intercepts the <span class="strong">**Voucher**</span> can read
    <span class="strong">**and**</span> write the sequence.

6.  But: Since the <span class="strong">**Voucher**</span> is a hash over the
    `VoucherPayload`, writing the sequence with anything but the
    `VoucherPayload` will be detectable by the recipient.

7.  This means that the contents <span class="emphasis">*cannot*</span> be modified
    undetectably by the interceptor.

</div>

</div>

</div>

</div>
