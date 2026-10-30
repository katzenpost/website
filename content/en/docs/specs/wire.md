---
title: ""
linkTitle: "Wire protocol"
description: ""
author: ""
url: ""
date: "2026-06-02T10:58:49.751573055-07:00"
draft: "false"
slug: "wireprotocol"
aliases: ["/docs/specs/wire/"]
layout: ""
type: ""
weight: "65"
version: ""
---

{{% pageinfo %}}
The [Namenlos profile](#wire-kem-profile) defines the v0.0.107 link KEM, handshake, authentication payloads, and transport keys.
The [directory wire protocol](/docs/specs/dirauth#222-wire-protocol) defines directory commands and consensus retrieval over direct authority or persistent gateway sessions.
{{% /pageinfo %}}

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="wire_protocol"></span>Mix network wire protocol specification

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">Yawning</span> <span class="surname">Angel</span>

</div>

<div class="author">

### <span class="firstname">David</span> <span class="surname">Stainton</span>

</div>

</div>

</div>

<div>

<div class="abstract">

**Abstract**

This document defines the Katzenpost mix network wire protocol for use in all
network communications to, from, and within the Katzenpost Mix Network.

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="conventions-used-in-this-document"></span>Conventions used in this document

</div>

</div>

</div>

The key words <span class="quote">“<span class="quote">MUST</span>”</span>, <span class="quote">“<span class="quote">MUST NOT</span>”</span>, <span class="quote">“<span class="quote">REQUIRED</span>”</span>,
<span class="quote">“<span class="quote">SHALL</span>”</span>, <span class="quote">“<span class="quote">SHALL NOT</span>”</span>, <span class="quote">“<span class="quote">SHOULD</span>”</span>, <span class="quote">“<span class="quote">SHOULD
NOT</span>”</span>, <span class="quote">“<span class="quote">RECOMMENDED</span>”</span>, <span class="quote">“<span class="quote">MAY</span>”</span>, and
<span class="quote">“<span class="quote">OPTIONAL</span>”</span> in this document are to be interpreted as described in <a href="#RFC2119" class="xref">the section called “References”</a>.

The <span class="quote">“<span class="quote">C</span>”</span> style Presentation Language as described in <a href="#RFC5246" class="xref">the section called “References”</a> Section 4 is used to represent data structures, except for
cryptographic attributes, which are specified as opaque byte vectors.

`x | y` denotes the concatenation of x and y.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="wire_protocol_introduction"></span>Introduction

</div>

</div>

</div>

The Katzenpost mix network wire protocol (KMNWP) is the custom wire protocol for
all network communications to, from, and within the Katzenpost mix network. This
protocol provides mutual authentication along with an additional layer of cryptographic
security and forward secrecy.

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="key-encapsulation-mechanism"></span>Key encapsulation mechanism

</div>

</div>

</div>

This protocol uses ANY key encapsulation mechanism. However, it is recommended
that most users select a hybrid post-quantum KEM such as Xwing. <a href="#XWING" class="xref">the section called “References”</a>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="core-protocol"></span>Core protocol

</div>

</div>

</div>

The protocol is based on Kyber and Trevor Perrin’s Noise protocol framework <a href="#NOISE" class="xref">the section called “References”</a> along with <span class="quote">“<span class="quote">Post Quantum Noise</span>”</span> paper <a href="#PQNOISE" class="link">PQNOISE</a>. Older previous versions of our transport were
based on <a href="#NOISEHFS" class="link">NOISEHFS</a>.

Our transport protocol begins with a prologue, Noise handshake, followed by a stream
of Noise transport messages in a minimal framing layer, over a TCP/IP connection.

The TOML configuration selects the KEM. This protocol string gives an Xwing example:

``` programlisting
Noise_pqXX_Xwing_ChaChaPoly_BLAKE2b
```

Namenlos uses the canonical KEM name `Kyber768-X25519` in its [protocol name](#pq-handshake-profile).
The [baseline KEM profile](#wire-kem-profile) defines its key encodings, adapter, and combiner.

The protocol string is a very condensed description of our protocol. We use the pqXX
two-way Noise pattern which is described as follows:

``` programlisting
pqXX: -> e <- ekem, s -> skem, s <- skem
```

The next part of the protocol string specifies the KEM, `Xwing` which is a
hybrid KEM where the share secret outputs of both X25519 and MLKEM768 are combined.

Finally the `ChaChaPoly_BLAKE2b` parts of the protocol string indicate
which stream cipher and hash function we are using.

Katzenpost permits larger transport messages than Noise's 65535-byte default.
Directory sessions apply the [configured receive size ceiling](/docs/specs/dirauth#receive-size-ceiling).

Each peer has a static key pair for the configured KEM.
The [authentication rules](#authentication-payload-profile) determine whether a peer needs a configured key pin.

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="handshake-phase"></span>Handshake phase

</div>

</div>

</div>

All sessions start in the <span class="emphasis">*handshake phase*</span>, in which an
anonymous authenticated handshake is conducted.

The [pqXX handshake](#pq-handshake-profile) starts with a fixed prologue before the initiator's first Noise message.
Both peers also use this byte as the Noise `prologue` input.

The prologue is defined to be the following structure:

``` programlisting
struct {
uint8_t protocol_version; /* 0x03 */
} Prologue;
```

As all Noise handshake messages are fixed sizes, no additional framing is required
for the handshake.

Implementations MUST preserve the Noise handshake hash `[h]` for the
purpose of implementing authentication (Section 2.3).

Implementations MUST reject handshake attempts by terminating the session
immediately upon any Noise protocol handshake failure and when, as a responder, they
receive a Prologue containing an unknown protocol_version value.

Implementations SHOULD impose reasonable timeouts for the handshake process, and
SHOULD terminate sessions that are taking too long to handshake.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="handshake-authentication"></span>Handshake authentication

</div>

</div>

</div>

Mutual authentication is done via exchanging fixed sized payloads as part of the
`pqXX` handshake consisting of the following structure:

``` programlisting
struct {
uint8_t ad_len;
opaque additional_data[ad_len];
opaque padding[255 - ad_len];
uint32_t unix_time;
} AuthenticateMessage;
```

Where:

<div class="itemizedlist">

- `ad_len` - The length of the optional additional data.

- `additional_data` - Optional additional data, such as a
  username, if any.

- `unix_time` - 0 for the initiator, the approximate number of
  seconds since 1970-01-01 00:00:00 UTC for the responder.

</div>

The responder sends `AuthenticateMessage` in flight 2. The initiator sends it in flight 3.
The [four-flight profile](#pq-handshake-profile) defines the tokens, payloads, and byte counts.
The [authentication payload profile](#authentication-payload-profile) defines the padding, integer encoding, and role-specific additional data.

The receiver MUST authenticate the remote static link key and additional data under the [peer's role](#authentication-payload-profile).
If authentication fails, the receiver MUST terminate the session immediately.

Responders MAY add a slight amount (+- 10 seconds) of random noise to the
`unix_time` value to avoid leaking precise load information via
packet queueing delay.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="data-transfer-phase"></span>Data transfer phase

</div>

</div>

</div>

Upon successfully concluding the handshake the session enters the <span class="emphasis">*data
transfer phase*</span>, where the initiator and responder can exchange KMNWP
messages.

A KMNWP message is defined to be the following structure:

``` programlisting
enum {
no_op(0),
disconnect(1),
send_packet(2),

(255),
} Command;

struct {
Command command;
uint8_t reserved;    /* MUST be '0x00' */
uint32_t msg_length; /* bounded by the session message limit */
opaque message[msg_length];
opaque padding[];    /* length is implicit */
} Message;
```

Notes:

<div class="itemizedlist">

- The padding field, if any MUST be padded with `'0x00'` bytes.

</div>

All outgoing Message(s) are encrypted and authenticated into a pair of Noise
Transport messages, each containing one of the following structures:

``` programlisting
struct {
uint32_t ciphertext_length;
} CiphertextHeader;

struct {
opaque message[ciphertext_length-16];
} Ciphertext;
```

Notes:

<div class="itemizedlist">

- The `ciphertext_length` field includes the Noise protocol
  overhead of 16 bytes, for the Noise Transport message containing the
  Ciphertext.

</div>

All outgoing Message(s) are preceded by a Noise Transport Message containing a
`CiphertextHeader`, indicating the size of the Noise Transport
Message transporting the Message Ciphertext. After generating both Noise Transport
Messages, the sender MUST call the Noise CipherState `Rekey()` operation.

To receive incoming Ciphertext messages, first the Noise Transport Message
containing the CiphertextHeader is consumed off the network, authenticated and
decrypted, giving the receiver the length of the Noise Transport Message containing
the actual message itself. The second Noise Transport Message is consumed off the
network, authenticated and decrypted, with the resulting message being returned to
the caller for processing. After receiving both Noise Transport Messages, the
receiver MUST call the Noise CipherState `Rekey()` operation.

Implementations MUST immediately terminate the session any of the
`DecryptWithAd()` operations fails.

Implementations MUST immediately terminate the session if an unknown command is
received in a Message, or if the Message is otherwise malformed in any way.

Implementations MAY impose a reasonable idle timeout, and terminate the session if
it expires.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="predefined-commands"></span>Predefined commands

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="the-no_op-command"></span>The <span class="emphasis">*no_op*</span> command

</div>

</div>

</div>

The `no_op` command is a command that explicitly is a No Operation, to
be used to implement functionality such as keep-alives and or application layer
padding.

Implementations MUST NOT send any message payload accompanying this command, and
all received command data MUST be discarded without interpretation.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="the-disconnect-command"></span>The disconnect command

</div>

</div>

</div>

The disconnect command is a command that is used to signal explicit session
termination. Upon receiving a disconnect command, implementations MUST interpret the
command as a signal from the peer that no additional commands will be sent, and
destroy the cryptographic material in the receive CipherState.

While most implementations will likely wish to terminate the session upon
receiving this command, any additional behavior is explicitly left up to the
implementation and application.

Implementations MUST NOT send any message payload accompanying this command, and
MUST not send any further traffic after sending a disconnect command.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="the-send_packet-command"></span>The send_packet command

</div>

</div>

</div>

The <span class="command">**send_packet**</span> command is the command that is used by the
initiator to transmit a Sphinx Packet over the network. The command’s message is the
Sphinx packet destined for the responder.

Initiators MUST terminate the session immediately upon reception of a
<span class="command">**send_packet**</span> command.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="command-padding"></span>Command padding

</div>

</div>

</div>

We use traffic padding to prevent a passive network observer from observing what
command has been sent or received. The following commands are padded:

<span class="bold">**Client-to-server commands**</span>

<div class="itemizedlist">

- <span class="command">**GetConsensus**</span>

- <span class="command">**NoOp**</span>

- <span class="command">**Disconnect**</span>

- <span class="command">**SendPacket**</span>

- <span class="command">**RetrieveMessage**</span>

</div>

<span class="bold">**Server-to-client commands**</span>

<div class="itemizedlist">

- <span class="command">**MessageACK**</span>

- <span class="command">**Message**</span>

- <span class="command">**MessageEmpty**</span>

</div>

We exclude the <span class="command">**Consensus**</span> command because its contents are a very
large payload that is usually many times larger than our Sphinx packets.

The <span class="command">**GetConsensus**</span> command is a special case because we only pad it
when sending it over the mixnet. We don’t pad it when sending to directory authorities,
because that would needlessly take up bandwidth without providing privacy benefits.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="anonymity-considerations"></span>Anonymity considerations

</div>

</div>

</div>

Adversaries being able to determine that two parties are communicating via KMNWP is
beyond the threat model of this protocol. At a minimum, it is trivial to determine
that
a KMNWP handshake is being performed, due to the length of each handshake message,
and
the fixed positions of the various public keys.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="security-considerations"></span>Security considerations

</div>

</div>

</div>

Each handshake MUST use a fresh ephemeral key pair. Each KEM encapsulation MUST use fresh randomness.
Static link keys identify peers under the [authentication rules](#authentication-payload-profile).

Kyber was chosen as the KEM algorithm due to it’s conservative parameterization,
simplicity of implementation, and high performance in software. It is hoped that the
addition of a quantum resistant algorithm will provide forward secrecy even in the
event
that large scale quantum computers are applied to historical intercepts.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="acknowledgments"></span>Acknowledgments

</div>

</div>

</div>

I would like to thank Trevor Perrin for providing feedback during the design of this
protocol, and answering questions regarding Noise.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="appendix-a.-references"></span>References

</div>

</div>

</div>

<span id="NOISE"></span><span class="bold">**NOISE**</span>

Perrin, T., <span class="quote">“<span class="quote">The Noise Protocol Framework</span>”</span>, May 2017,
<a href="https://noiseprotocol.org/noise.pdf" class="link" target="_top">https://noiseprotocol.org/noise.pdf</a>.

<span id="NOISEHFS"></span><span class="bold">**NOISEHFS**</span>

Weatherley, R., <span class="quote">“<span class="quote">Noise Extension: Hybrid Forward Secrecy</span>”</span>,
<a href="https://github.com/noiseprotocol/noise_hfs_spec/blob/master/output/noise_hfs.pdf" class="link" target="_top">https://github.com/noiseprotocol/noise_hfs_spec/blob/master/output/noise_hfs.pdf</a>.

<span id="PQNOISE"></span><span class="bold">**PQNOISE**</span>

Yawning Angel, Benjamin Dowling, Andreas Hülsing, Peter Schwabe and Florian Weber,
<span class="quote">“<span class="quote">Post Quantum Noise</span>”</span>, September 2023,
<a href="https://eprint.iacr.org/2022/539.pdf" class="link" target="_top">https://eprint.iacr.org/2022/539.pdf</a>.

<span id="RFC2119"></span><span class="bold">**RFC2119**</span>

Bradner, S., <span class="quote">“<span class="quote">Key words for use in RFCs to Indicate Requirement
Levels</span>”</span>, BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997, <a href="http://www.rfc-editor.org/info/rfc2119" class="link" target="_top">http://www.rfc-editor.org/info/rfc2119</a>.

<span id="RFC5246"></span><span class="bold">**RFC5246**</span>

Dierks, T. and E. Rescorla, <span class="quote">“<span class="quote">The Transport Layer Security (TLS) Protocol
Version 1.2</span>”</span>, RFC 5246, DOI 10.17487/RFC5246, August 2008, <a href="http://www.rfc-editor.org/info/rfc5246" class="link" target="_top">http://www.rfc-editor.org/info/rfc5246</a>.

<span id="RFC7748"></span><span class="bold">**RFC7748**</span>

Langley, A., Hamburg, M., and S. Turner, <span class="quote">“<span class="quote">Elliptic Curves for Security</span>”</span>, RFC 7748, January 2016,
<a href="https://www.rfc-editor.org/info/rfc7748" class="link" target="_top">https://www.rfc-editor.org/info/rfc7748</a>.

<span id="XWING"></span><span class="bold">**XWING**</span>

Manuel Barbosa, Deirdre Connolly, João Diogo Duarte, Aaron Kaiser, Peter Schwabe,
Karoline Varner, Bas Westerbaan, <span class="quote">“<span class="quote">X-Wing: The Hybrid KEM You’ve Been Looking
For</span>”</span>,
<a href="https://eprint.iacr.org/2024/039.pdf" class="link" target="_top">https://eprint.iacr.org/2024/039.pdf</a>.

</div>

</div>

## Appendix: Namenlos wire profile {#wire-kem-profile}

This profile defines the Namenlos link KEM and handshake with Katzenpost v0.0.107. Implementations MUST use these formats with that configuration. The linked primitive specifications define X25519, Kyber, BLAKE2, and ChaCha20-Poly1305. The composition rules below define their use on the wire.

Here, `||` means byte concatenation, `empty` means zero bytes, and `zero[n]` means n zero bytes. `BE32`, `LE32`, and `LE64` encode unsigned integers in the indicated byte order. ASCII literals have no terminating zero.

`H256` means unkeyed BLAKE2b with a 32-byte output. `H512` means unkeyed BLAKE2b with a 64-byte output. Configure BLAKE2b-256 for 32 output bytes. Do not truncate BLAKE2b-512 to produce BLAKE2b-256. Both use the sequential mode in [RFC 7693](https://www.rfc-editor.org/rfc/rfc7693).

### Link key encodings

<div class="key-value-table">

| Key | Value | Explanation |
| --- | --- | --- |
| Wire KEM | `Kyber768-X25519` | This is the canonical name used in the Noise protocol name. Configuration lookup also accepts the Namenlos spelling `KYBER768-X25519`. |
| Public key | 1216 bytes | X25519 public key, 32 bytes, followed by Kyber768 public key, 1184 bytes. |
| Private key | 2432 bytes | X25519 scalar, 32 bytes, followed by Kyber768 secret key, 2400 bytes. |
| Ciphertext | 1120 bytes | X25519 adapter ciphertext, 32 bytes, followed by Kyber768 ciphertext, 1088 bytes. |
| Shared secret | 32 bytes | The combiner output defined below. |

</div>

Keys use raw component encodings without ASN.1, text encoding, or length prefixes. X25519 uses the 32-byte little-endian u-coordinate encoding and scalar operation in [RFC 7748, Section 5](https://www.rfc-editor.org/rfc/rfc7748#section-5). The [scheme definition](https://github.com/katzenpost/hpqc/blob/v0.0.93/kem/schemes/schemes.go#L111-L118) fixes the component order.

The public PEM label is `KYBER768-X25519 PUBLIC KEY`. The private PEM label is `KYBER768-X25519 PRIVATE KEY`. A PEM payload is the base64 encoding of the corresponding raw key. There are no PEM headers or ASN.1 fields. This encoding permits import of reference key files. An implementation can use its own internal storage format.

The [PEM codec](https://github.com/katzenpost/hpqc/blob/v0.0.93/kem/pem/pem.go#L21-L34) wraps raw key bytes.

### Link KEM adapter and combiner

The Kyber component is **Kyber768.CCAKEM from the round 3 specification, version 3.02**, with its public-key, secret-key, and ciphertext encodings. Use [Algorithms 7-9 and the Kyber768 parameters](https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf). This is the round 3 Kyber KEM, not ML-KEM. The [pinned Kyber implementation](https://github.com/katzenpost/circl/blob/e2d217fd59f5/kem/kyber/kyber768/kyber.go#L1-L38) identifies that primitive and its sizes.

For the X25519 component, let `X_s` be the recipient's public key. Generate a fresh ephemeral scalar `x_e` and its public key `X_e`. Compute:

```text
Z    = X25519(x_e, X_s)
ct_X = X_e
ss_X = BLAKE2Xb(output_length=32, key=Z, message=X_s || X_e)
```

Reject an all-zero `Z`. Decapsulation computes `Z = X25519(x_s, ct_X)` and uses the same recipient-public-key-first input. The output length supplied to [BLAKE2Xb](https://www.blake2.net/blake2x.pdf) is exactly 32. Its unknown-length mode produces different bytes and MUST NOT be used here. The [adapter](https://github.com/katzenpost/hpqc/blob/v0.0.93/kem/adapter/kem.go#L145-L169) defines the inputs. Its [PRF](https://github.com/katzenpost/hpqc/blob/v0.0.93/kem/adapter/kem.go#L214-L243) selects the fixed-length keyed XOF.

For this invocation, BLAKE2Xb first produces a keyed 64-byte root over `X_s || X_e`. It then produces one unkeyed 32-byte output block over that root. Each BLAKE2 parameter block is 64 bytes and starts with all bytes zero. Set these fields:

<div class="key-value-table">

| Key | Value | Explanation |
| --- | --- | --- |
| Root bytes 0-3 | `64, 32, 1, 1` | Digest length, key length, fanout, and depth. The key is `Z`, with standard BLAKE2b key-block padding. |
| Root bytes 12-15 | `LE32(32)` | XOF output length. |
| Output byte 0 | `32` | Output digest length. |
| Output bytes 4-7 | `LE32(64)` | Leaf length. |
| Output bytes 8-11 | `LE32(0)` | Output block number. |
| Output bytes 12-15 | `LE32(32)` | XOF output length. |
| Output byte 17 | `64` | Inner digest length. |

</div>

All unlisted fields, salt, and personalization remain zero. Set the normal final-block flag for each hash. Do not set the last-node flag. The [fixed-output BLAKE2Xb implementation](https://github.com/golang/crypto/blob/v0.58.0/blake2b/blake2x.go#L104-L183) gives these parameter blocks.

Encapsulate independently to each component public key. Let `(ct_X, ss_X)` be the adapter output and `(ct_K, ss_K)` be the Kyber output. Both component shared secrets are 32 bytes. Define:

```text
T = ASCII("splitprf-v1") || BE32(2)
    || BE32(32) || ct_X || BE32(1088) || ct_K

k_X = H256(ss_X)
k_K = H256(ss_K)
ss  = BLAKE2b-256(key=k_X, message=T)
      XOR BLAKE2b-256(key=k_K, message=T)
ct  = ct_X || ct_K
```

The two keyed hashes use BLAKE2b's native keyed mode. They are not HMAC. XOR is bytewise across all 32 bytes.

Decapsulation splits the 1120-byte ciphertext at byte 32, decapsulates both components, and applies the same formula to the received component ciphertexts. Reject an incorrect total length or an error from either component. Kyber's implicit-rejection behavior remains part of the Kyber primitive. The [combiner definition](https://github.com/katzenpost/hpqc/blob/v0.0.93/kem/combiner/split_prf.go#L37-L122) fixes the label, length fields, prehashes, and XOR.

### PQ Noise handshake {#pq-handshake-profile}

Use the symmetric operations from [Noise revision 34](https://noiseprotocol.org/noise.html), with the KEM token rules below. The exact protocol name is the following 45 ASCII bytes:

```text
Noise_pqXX_Kyber768-X25519_ChaChaPoly_BLAKE2b
```

There are no pre-messages or pre-shared keys. Both peers have a static link KEM key pair. An anonymous fetcher generates a fresh link key pair for its connection. The initiator also generates a fresh ephemeral KEM key pair for token `e`. Each KEM encapsulation uses fresh randomness.

Initialize `h` to the protocol name followed by 19 zero bytes. Copy this value to `ck`. Start with no cipher key and nonce zero. Then set `h = H512(h || 0x03)`.

The single byte `0x03` is the Noise prologue and is also sent in clear before the first flight. It is not a token or payload byte. The responder MUST reject any other version byte.

The following rules define the symmetric operations. HMAC uses BLAKE2b-512. For `HKDF(ck, input, count)`, compute:

```text
prk = HMAC-BLAKE2b-512(key=ck, message=input)
t1  = HMAC-BLAKE2b-512(key=prk, message=0x01)
t2  = HMAC-BLAKE2b-512(key=prk, message=t1 || 0x02)
t3  = HMAC-BLAKE2b-512(key=prk, message=t2 || 0x03)
```

Return the first `count` values, each 64 bytes. No HKDF info bytes are present.

<div class="key-value-table">

| Key | Value | Explanation |
| --- | --- | --- |
| `MixHash(x)` | `h = H512(h \|\| x)` | This operation also runs when `x` is empty. |
| `MixKey(x)` | `(ck, t) = HKDF(ck, x, 2)` | Set the cipher key to the first 32 bytes of `t`, and reset the nonce to zero. |
| `MixKeyAndHash(x)` | `(ck, u, t) = HKDF(ck, x, 3)` | Run `MixHash(u)`, set the cipher key to the first 32 bytes of `t`, and reset the nonce to zero. |
| `EncryptAndHash(p)` | Encrypt `p` with associated data `h`, then run `MixHash(ciphertext)` | Without a cipher key, use `p` unchanged as the ciphertext. |
| `DecryptAndHash(c)` | Decrypt `c` with associated data equal to the prior `h`, then run `MixHash(c)` | Without a cipher key, the plaintext is `c`. Reject an AEAD failure. |

</div>

Encryption uses [IETF ChaCha20-Poly1305](https://www.rfc-editor.org/rfc/rfc8439), a 32-byte key, and the 12-byte nonce `zero[4] || LE64(n)`. Its 16-byte tag follows the ciphertext. Increase `n` after each keyed encryption or successful keyed decryption. Do not increase it for an unkeyed operation. A normal encryption or decryption MUST fail when `n = 2^64-1`.

The [symmetric-state implementation](https://github.com/katzenpost/nyquist/blob/v0.0.13/symmetricstate.go#L61-L179) defines these operations. The [cipher implementation](https://github.com/katzenpost/nyquist/blob/v0.0.13/cipher/cipher.go#L75-L91) fixes the AEAD and nonce bytes.

Each flight processes its tokens in order, then calls `EncryptAndHash` on its payload. The receiver performs the inverse operations in the same order.

<div class="key-value-table">

| Key | Value | Explanation |
| --- | --- | --- |
| `e` | Raw ephemeral public key, 1216 bytes | Send the initiator's ephemeral KEM public key, and run `MixHash` on those bytes. |
| `ekem` | Raw KEM ciphertext, 1120 bytes | Encapsulate to the peer's ephemeral key. Send the ciphertext, run `MixHash(ciphertext)`, then `MixKey(shared_secret)`. The receiver decapsulates with its ephemeral private key. |
| `s` | `EncryptAndHash(static_public_key)` | Send the sender's 1216-byte static link public key. The receiver decrypts it and retains it as the peer's static key. |
| `skem` | `EncryptAndHash(KEM_ciphertext)` | Encapsulate to the peer's static key. Encrypt and hash the ciphertext with the current cipher state, then run `MixKeyAndHash(shared_secret)`. The receiver decrypts, decapsulates with its static private key, then runs `MixKeyAndHash`. |

</div>

The [pqXX pattern](https://github.com/katzenpost/nyquist/blob/v0.0.13/pattern/pq_interactive.go#L96-L105) and [KEM token processing](https://github.com/katzenpost/nyquist/blob/v0.0.13/handshakestate_kem.go#L47-L236) define this order. In particular, `skem` updates both `ck` and `h` after its encrypted ciphertext.

Let `P=1216`, `C=1120`, `A=260`, and `T=16`. Each length below is an exact stream byte count. There is no handshake length prefix or padding outside the stated fields.

<div class="key-value-table">

| Key | Value | Explanation |
| --- | --- | --- |
| Flight 1, initiator -> responder | `0x03`, `e`, empty payload. 1217 bytes. | `1+P`. The empty payload emits no bytes but still runs `MixHash(empty)`. |
| Flight 2, responder -> initiator | `ekem`, `s`, responder authentication. 2628 bytes. | `C + (P+T) + (A+T)`. After `ekem`, the static key and payload use nonces 0 and 1. |
| Flight 3, initiator -> responder | `skem`, `s`, initiator authentication. 2644 bytes. | `(C+T) + (P+T) + (A+T)`. `skem` uses nonce 2 from flight 2. Its key update resets the nonce, so `s` and the payload use 0 and 1. |
| Flight 4, responder -> initiator | `skem`, empty payload. 1152 bytes. | `(C+T) + T`. `skem` uses nonce 2 from flight 3. Its key update resets the nonce. The empty payload uses nonce 0 and emits a 16-byte tag. |

</div>

The session uses these [flight lengths](https://github.com/katzenpost/katzenpost/blob/v0.0.107/core/wire/session.go#L252-L274) and [payload assignments](https://github.com/katzenpost/katzenpost/blob/v0.0.107/core/wire/session.go#L391-L540). The [payload operation](https://github.com/katzenpost/nyquist/blob/v0.0.13/handshakestate.go#L511-L522) runs once after every flight's tokens, including flights 1 and 4.

### Authentication payload {#authentication-payload-profile}

An `AuthenticateMessage` is exactly 260 bytes:

```text
u8(length(AD)) || AD || zero[255-length(AD)] || BE32(unix_time)
```

`AD` has 0 to 255 bytes. The timestamp starts at offset 256. The initiator sends timestamp zero. The responder sends its current Unix time in whole seconds, encoded as an unsigned 32-bit value.

Senders MUST set the padding to zero. The v0.0.107 receiver extracts the length, AD, and timestamp. It ignores the padding bytes. The [authentication codec](https://github.com/katzenpost/katzenpost/blob/v0.0.107/core/wire/session.go#L120-L154) defines this layout.

<div class="key-value-table">

| Key | Value | Explanation |
| --- | --- | --- |
| Authority responder | 32 raw identity-hash bytes | Its static Noise key is its configured link public key. |
| Authority or node uploading to an authority | 32 raw identity-hash bytes | The identity hash selects the configured peer. Authority peers also require the pinned link key. Node uploads bind the descriptor link key to this session. |
| Anonymous direct directory fetcher | Empty AD | Use a fresh link key pair. The authority grants the anonymous fetch role. |
| Client daemon connecting to a gateway | 32 lowercase ASCII hexadecimal bytes | Encode 16 fresh random bytes as two hex characters per byte. This is the gateway queue identifier. It is not a raw identity hash. |

</div>

The [identity signature profile](/docs/specs/certificate#identity-signature-profile) defines identity hashes. The authority's [responder configuration](https://github.com/katzenpost/katzenpost/blob/v0.0.107/authority/voting/server/wire_handler.go#L71-L87), [initiator configuration](https://github.com/katzenpost/katzenpost/blob/v0.0.107/authority/voting/client/client.go#L384-L411), and [peer classification](https://github.com/katzenpost/katzenpost/blob/v0.0.107/authority/voting/server/wire_handler.go#L886-L937) distinguish these roles. The [client connection](https://github.com/katzenpost/katzenpost/blob/v0.0.107/client/connection.go#L435-L454) defines the queue identifier.

The initiator authenticates the responder after flight 2. It uses the responder's static key and authentication payload. The responder authenticates the initiator after flight 3.

For an authority responder, the v0.0.107 client requires at least 32 AD bytes. It compares the first 32 bytes with the configured identity hash. It also compares the full static link key with its configured pin. Authority receivers accept only empty or 32-byte initiator AD and apply the role requirements above. Any failed authentication terminates the session. The [authority authenticator](https://github.com/katzenpost/katzenpost/blob/v0.0.107/authority/voting/client/client.go#L67-L86) implements these requirements.

### Transport keys and framing {#transport-key-profile}

After flight 4's empty payload, compute `(t_I, t_R) = HKDF(ck, empty, 2)`. The first 32 bytes of `t_I` are the initiator-to-responder transport key. The first 32 bytes of `t_R` are the responder-to-initiator key. Each direction starts with nonce zero. Transport encryption uses empty AEAD associated data. It does not continue `EncryptAndHash` or update the handshake hash.

For each command, encrypt `BE32(length(serialized_command)+16)` as a separate 20-byte header. Then encrypt the serialized command with the next nonce. Both operations use the same direction's cipher key. After the body, update that direction's key to the first 32 bytes of `ChaCha20-Poly1305(key, zero[4] || LE64(2^64-1), empty_AD, zero[32])`. Keep the ordinary nonce counter at its value after the two frame operations. The receiver follows the same sequence.

The responder's first transport command MUST be `NoOp`. The initiator MUST receive it before using the session. The session implements [transport sending](https://github.com/katzenpost/katzenpost/blob/v0.0.107/core/wire/session.go#L615-L644), [rekeying](https://github.com/katzenpost/nyquist/blob/v0.0.13/cipherstate.go#L164-L186), and [handshake finalization](https://github.com/katzenpost/katzenpost/blob/v0.0.107/core/wire/session.go#L544-L577).
