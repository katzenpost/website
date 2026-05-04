{ "title": "", "linkTitle": "Contact Voucher Design", "description": "",
"url": "docs/specs/voucher.html", "date":
"2026-05-01T15:15:43.499681-07:00", "draft": "false", "slug": "",
"layout": "", "type": "", "weight": "5" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="voucher"></span>Contact Voucher Design

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

<div class="toc">

**Table of Contents**

<span class="section">[Voucher Design](#d58e28)</span>

<span class="section">[Self-authenticating BACAP
payload](#d58e62)</span>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="d58e28"></span>Voucher Design

</div>

</div>

</div>

In order to join or initiate a conversation, participants need to
exchange cryptographic key material. To address this problem we have a
slightly unusual design: Contact vouchers.

In many systems, invites to conversations flow from an existing member
of the conversation to the user being invited. In our "Contact Voucher"
protocol this flow is reversed: A member wishing to join a conversation
hands a "Contact Voucher" (out of band) to the existing member, who then
inducts the new member into the group.

This design mitigates two potential problem with the former way of doing
it:

<div class="orderedlist">

1.  If the Contact Voucher is observed by a third-party, the third-party
    does not get to read neither participants' actual messages.

    <div class="itemizedlist">

    - <span class="strong">**Passive**</span> adversaries learn that the
      voucher was spent, but do not get to observe further interactions.

    - <span class="strong">**Active**</span> adversaries can create a
      new fake group to induct the member into but does not learn
      anything about the existing group.

      <div class="itemizedlist">

      - In the future to prevent this one-way impersonation we could
        allow a "both parties bring something on paper to the meeting":

        <div class="itemizedlist">

        - Bob brings Contact Voucher

        - Alice brings fingerprint for the VoucherReplyPublicKey
          (thwarts the active attacker)

        </div>

      </div>

    </div>

2.  Only one thing needs to delivered out of band to achieve a 2-pass
    protocol (instead of a 3-pass protocol).

</div>

<div class="itemizedlist">

- Only one of the parties need to bring key material to a meeting in
  order to establish contact.

</div>


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

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="d58e62"></span>Self-authenticating BACAP payload

</div>

</div>

</div>

The first message sent (The VoucherPayload) is authenticated in the
following manner:

<div class="itemizedlist">

- The VoucherPayload is computed (first).

- A cryptographic hash of the VoucherPayload is computed. This hash
  <span class="strong">**is**</span> the
  <span class="emphasis">*Voucher*</span>\*.

- The <span class="strong">**Voucher**</span> is then used to derive a
  BACAP read/write capability set.

- The VoucherPayload is uploaded to the sequence described by the
  capability (at index 0).

- Anyone who intercepts the <span class="strong">**Voucher**</span> can
  read <span class="strong">**and**</span> write the sequence.

- But: Since the <span class="strong">**Voucher**</span> is a hash over
  the VoucherPayload, writing the sequence with anything but the
  VoucherPayload will be detectable by the recipient.

- This means that the contents <span class="emphasis">*cannot*</span> be
  undetectably be modified by the interceptor.

</div>

</div>

</div>

</div>
