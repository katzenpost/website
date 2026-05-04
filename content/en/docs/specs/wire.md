{ "title": "" , "linkTitle": "Wire protocol" , "description": "" ,
"url": "docs/specs/wire_protocol.html" , "date":
"2026-05-01T16:31:59.479833284-07:00", "draft": "false" , "slug": "" ,
"layout": "" , "type": "" , "weight": "60" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="wire_protocol"></span>Katzenpost mix network wire protocol

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

This document defines the Katzenpost Mix Network Wire Protocol for use
in all network communications to, from, and within the Katzenpost Mix
Network.

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="toc">

**Table of Contents**

<span class="section">[1.1 Conventions Used in This
Document](#conventions-used-in-this-document)</span>

<span class="section">[1.
Introduction](#wire_protocol_introduction)</span>

<span class="section">[1.2 Key Encapsulation
Mechanism](#key-encapsulation-mechanism)</span>

<span class="section">[2. Core Protocol](#core-protocol)</span>

<span class="section">[2.1 Handshake Phase](#handshake-phase)</span>

<span class="section">[2.1.1 Handshake
Authentication](#handshake-authentication)</span>

<span class="section">[2.2 Data Transfer
Phase](#data-transfer-phase)</span>

<span class="section">[3. Predefined
Commands](#predefined-commands)</span>

<span class="section">[3.1 The no_op Command](#the-no_op-command)</span>

<span class="section">[3.2 The disconnect
Command](#the-disconnect-command)</span>

<span class="section">[3.3 The send_packet
Command](#the-send_packet-command)</span>

<span class="section">[4. Command Padding](#command-padding)</span>

<span class="section">[5. Anonymity
Considerations](#anonymity-considerations)</span>

<span class="section">[6. Security
Considerations](#security-considerations)</span>

<span class="section">[Acknowledgments](#acknowledgments)</span>

<span class="section">[References](#appendix-a.-references)</span>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="conventions-used-in-this-document"></span>1.1 Conventions Used in This Document

</div>

</div>

</div>

The key words
<span class="quote">“<span class="quote">MUST</span>”</span>,
<span class="quote">“<span class="quote">MUST NOT</span>”</span>,
<span class="quote">“<span class="quote">REQUIRED</span>”</span>,
<span class="quote">“<span class="quote">SHALL</span>”</span>,
<span class="quote">“<span class="quote">SHALL NOT</span>”</span>,
<span class="quote">“<span class="quote">SHOULD</span>”</span>,
<span class="quote">“<span class="quote">SHOULD NOT</span>”</span>,
<span class="quote">“<span class="quote">RECOMMENDED</span>”</span>,
<span class="quote">“<span class="quote">MAY</span>”</span>, and
<span class="quote">“<span class="quote">OPTIONAL</span>”</span> in this
document are to be interpreted as described in
<a href="#RFC2119" class="xref">the section called “References”</a>.

The <span class="quote">“<span class="quote">C</span>”</span> style
Presentation Language as described in
<a href="#RFC5246" class="xref">the section called “References”</a>
Section 4 is used to represent data structures, except for cryptographic
attributes, which are specified as opaque byte vectors.

`x | y` denotes the concatenation of x and y.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="wire_protocol_introduction"></span>1. Introduction

</div>

</div>

</div>

The Katzenpost Mix Network Wire Protocol (KMNWP) is the custom wire
protocol for all network communications to, from, and within the
Katzenpost Mix Network. This protocol provides mutual authentication,
and an additional layer of cryptographic security and forward secrecy.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="key-encapsulation-mechanism"></span>1.2 Key Encapsulation Mechanism

</div>

</div>

</div>

This protocol uses ANY Key Encapsulation Mechanism. However it’s
recommended that most users select a hybrid post quantum KEM such as
Xwing. <a href="#XWING" class="xref">the section called “References”</a>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="core-protocol"></span>2. Core Protocol

</div>

</div>

</div>

The protocol is based on Kyber and Trevor Perrin’s Noise Protocol
Framework
<a href="#NOISE" class="xref">the section called “References”</a> along
with <span class="quote">“<span class="quote">Post Quantum
Noise</span>”</span> paper <a href="#PQNOISE" class="link">PQNOISE</a>.
Older previous versions of our transport were based on
<a href="#NOISEHFS" class="link">NOISEHFS</a>.

Our transport protocol begins with a prologue, Noise handshake, followed
by a stream of Noise Transport messages in a minimal framing layer, over
a TCP/IP connection.

Our Noise protocol is configurable via the KEM selection in the TOML
configuration files, here’s an example PQ Noise protocol string:

``` programlisting
Noise_pqXX_Xwing_ChaChaPoly_BLAKE2b
```

The protocol string is a very condensed description of our protocol. We
use the pqXX two way Noise pattern which is described as follows:

``` programlisting
pqXX: -> e <- ekem, s -> skem, s <- skem
```

The next part of the protocol string specifies the KEM, `Xwing` which is
a hybrid KEM where the share secret outputs of both X25519 and MLKEM768
are combined.

Finally the `ChaChaPoly_BLAKE2b` parts of the protocol string indicate
which stream cipher and hash function we are using.

As a non-standard modification to the Noise protocol, the 65535 byte
message length limit is increased to 1300000 bytes. We send very large
messages over our Noise protocol because of our using the Sphincs+
signature scheme which has signatures that are about 49k bytes.

It is assumed that all parties using the KMNWP protocol have a fixed
long or short lived `Xwing` keypair
<a href="#XWING" class="link">XWING</a>, the public component of which
is known to the other party in advance. How such keys are distributed is
beyond the scope of this document.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="handshake-phase"></span>2.1 Handshake Phase

</div>

</div>

</div>

All sessions start in the Handshake Phase, in which an anonymous
authenticated handshake is conducted.

The handshake is a unmodified Noise handshake, with a fixed prologue
prefacing the initiator's first Noise handshake message. This prologue
is also used as the `prologue` input to the Noise HandshakeState
`Initialize()` operation for both the initiator and responder.

The prologue is defined to be the following structure:

``` programlisting
struct {
uint8_t protocol_version; /* 0x03 */
} Prologue;
```

As all Noise handshake messages are fixed sizes, no additional framing
is required for the handshake.

Implementations MUST preserve the Noise handshake hash `[h]` for the
purpose of implementing authentication (Section 2.3).

Implementations MUST reject handshake attempts by terminating the
session immediately upon any Noise protocol handshake failure and when,
as a responder, they receive a Prologue containing an unknown
protocol_version value.

Implementations SHOULD impose reasonable timeouts for the handshake
process, and SHOULD terminate sessions that are taking too long to
handshake.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="handshake-authentication"></span>2.1.1 Handshake Authentication

</div>

</div>

</div>

Mutual authentication is done via exchanging fixed sized payloads as
part of the `pqXX` handshake consisting of the following structure:

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

- `additional_data` - Optional additional data, such as a username, if
  any.

- `unix_time` - 0 for the initiator, the approximate number of seconds
  since 1970-01-01 00:00:00 UTC for the responder.

</div>

The initiator MUST send the `AuthenticateMessage` after it has received
the peer's response (so after `-> s, se` in Noise parlance).

The contents of the optional `additional_data` field is deliberately
left up to the implementation, however it is RECOMMENDED that
implementations pad the field to be a consistent length regardless of
contents to avoid leaking information about the authenticating identity.

To authenticate the remote peer given an AuthenticateMessage, the
receiving peer must validate the `s` component of the Noise handshake
(the remote peer's long term public key) with the known value, along
with any of the information in the `additional_data` field such as the
user name, if any.

If the validation procedure succeeds, the peer is considered
authenticated. If the validation procedure fails for any reason, the
session MUST be terminated immediately.

Responders MAY add a slight amount (+- 10 seconds) of random noise to
the unix_time value to avoid leaking precise load information via packet
queueing delay.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="data-transfer-phase"></span>2.2 Data Transfer Phase

</div>

</div>

</div>

Upon successfully concluding the handshake the session enters the Data
Transfer Phase, where the initiator and responder can exchange KMNWP
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
uint32_t msg_length; /* 0 <= msg_length <= 1048554) */
opaque message[msg_length];
opaque padding[];    /* length is implicit */
} Message;
```

Notes:

<div class="itemizedlist">

- The padding field, if any MUST be padded with `'0x00'` bytes.

</div>

All outgoing Message(s) are encrypted and authenticated into a pair of
Noise Transport messages, each containing one of the following
structures:

``` programlisting
struct {
uint32_t message_length;
} CiphertextHeader;

struct {
uint32_t message[ciphertext_length-16];
} Ciphertext;
```

Notes:

<div class="itemizedlist">

- The `ciphertext_length` field includes the Noise protocol overhead of
  16 bytes, for the Noise Transport message containing the Ciphertext.

</div>

All outgoing Message(s) are preceded by a Noise Transport Message
containing a `CiphertextHeader`, indicating the size of the Noise
Transport Message transporting the Message Ciphertext. After generating
both Noise Transport Messages, the sender MUST call the Noise
CipherState `Rekey()` operation.

To receive incoming Ciphertext messages, first the Noise Transport
Message containing the CiphertextHeader is consumed off the network,
authenticated and decrypted, giving the receiver the length of the Noise
Transport Message containing the actual message itself. The second Noise
Transport Message is consumed off the network, authenticated and
decrypted, with the resulting message being returned to the caller for
processing. After receiving both Noise Transport Messages, the receiver
MUST call the Noise CipherState `Rekey()` operation.

Implementations MUST immediately terminate the session any of the
`DecryptWithAd()` operations fails.

Implementations MUST immediately terminate the session if an unknown
command is received in a Message, or if the Message is otherwise
malformed in any way.

Implementations MAY impose a reasonable idle timeout, and terminate the
session if it expires.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="predefined-commands"></span>3. Predefined Commands

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-no_op-command"></span>3.1 The no_op Command

</div>

</div>

</div>

The `no_op` command is a command that explicitly is a No Operation, to
be used to implement functionality such as keep-alives and or
application layer padding.

Implementations MUST NOT send any message payload accompanying this
command, and all received command data MUST be discarded without
interpretation.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-disconnect-command"></span>3.2 The disconnect Command

</div>

</div>

</div>

The `disconnect` command is a command that is used to signal explicit
session termination. Upon receiving a disconnect command,
implementations MUST interpret the command as a signal from the peer
that no additional commands will be sent, and destroy the cryptographic
material in the receive CipherState.

While most implementations will likely wish to terminate the session
upon receiving this command, any additional behavior is explicitly left
up to the implementation and application.

Implementations MUST NOT send any message payload accompanying this
command, and MUST not send any further traffic after sending a
disconnect command.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-send_packet-command"></span>3.3 The send_packet Command

</div>

</div>

</div>

The `send_packet` command is the command that is used by the initiator
to transmit a Sphinx Packet over the network. The command’s message is
the Sphinx Packet destined for the responder.

Initiators MUST terminate the session immediately upon reception of a
`send_packet` command.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="command-padding"></span>4. Command Padding

</div>

</div>

</div>

We use traffic padding to hide from a passive network observer which
command has been sent or received.

Among the set of padded commands we exclude the `Consensus` command
because it’s contents are a very large payload which is usually many
times larger than our Sphinx packets. Therefore we only pad these
commands:

GetConsensus NoOp Disconnect SendPacket RetrieveMessage MessageACK
Message MessageEmpty

However we split them up into two directions, client to server and
server to client because they differ in size due to the difference in
size between `SendPacket` and `Message`:

Client to Server commands:

NoOp SendPacket Disconnect RetrieveMessage GetConsensus

Server to client commands:

Message MessageACK MessageEmpty

The `GetConsensus` command is a special case because we only want to pad
it when it’s sent over the mixnet. We don’t want to pad it when sending
to the dirauths. Although it would not be so terrible if it’s padded
when sent to the dirauths… it would just needlessly take up bandwidth
without providing any privacy benefits.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="anonymity-considerations"></span>5. Anonymity Considerations

</div>

</div>

</div>

Adversaries being able to determine that two parties are communicating
via KMNWP is beyond the threat model of this protocol. At a minimum, it
is trivial to determine that a KMNWP handshake is being performed, due
to the length of each handshake message, and the fixed positions of the
various public keys.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="security-considerations"></span>6. Security Considerations

</div>

</div>

</div>

It is imperative that implementations use ephemeral keys for every
handshake as the security properties of the Kyber KEM are totally lost
if keys are ever reused.

Kyber was chosen as the KEM algorithm due to it’s conservative
parameterization, simplicity of implementation, and high performance in
software. It is hoped that the addition of a quantum resistant algorithm
will provide forward secrecy even in the event that large scale quantum
computers are applied to historical intercepts.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="acknowledgments"></span>Acknowledgments

</div>

</div>

</div>

I would like to thank Trevor Perrin for providing feedback during the
design of this protocol, and answering questions regarding Noise.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="appendix-a.-references"></span>References

</div>

</div>

</div>

<span id="XWING"></span><span class="bold">**XWING**</span>

Manuel Barbosa, Deirdre Connolly, João Diogo Duarte, Aaron Kaiser, Peter
Schwabe, Karoline Varner, Bas Westerbaan,
<span class="quote">“<span class="quote">X-Wing: The Hybrid KEM You’ve
Been Looking For</span>”</span>,
<a href="https://eprint.iacr.org/2024/039.pdf" class="link"
target="_top">https://eprint.iacr.org/2024/039.pdf</a>.

<span id="NOISE"></span><span class="bold">**NOISE**</span>

Perrin, T., <span class="quote">“<span class="quote">The Noise Protocol
Framework</span>”</span>, May 2017,
<a href="https://noiseprotocol.org/noise.pdf" class="link"
target="_top">https://noiseprotocol.org/noise.pdf</a>.

<span id="NOISEHFS"></span><span class="bold">**NOISEHFS**</span>

Weatherley, R., <span class="quote">“<span class="quote">Noise
Extension: Hybrid Forward Secrecy</span>”</span>, <a
href="https://github.com/noiseprotocol/noise_hfs_spec/blob/master/output/noise_hfs.pdf"
class="link"
target="_top">https://github.com/noiseprotocol/noise_hfs_spec/blob/master/output/noise_hfs.pdf</a>.

<span id="PQNOISE"></span><span class="bold">**PQNOISE**</span>

Yawning Angel, Benjamin Dowling, Andreas Hülsing, Peter Schwabe and
Florian Weber, <span class="quote">“<span class="quote">Post Quantum
Noise</span>”</span>, September 2023,
<a href="https://eprint.iacr.org/2022/539.pdf" class="link"
target="_top">https://eprint.iacr.org/2022/539.pdf</a>.

<span id="RFC2119"></span><span class="bold">**RFC2119**</span>

Bradner, S., <span class="quote">“<span class="quote">Key words for use
in RFCs to Indicate Requirement Levels</span>”</span>, BCP 14, RFC 2119,
DOI 10.17487/RFC2119, March 1997,
<a href="http://www.rfc-editor.org/info/rfc2119" class="link"
target="_top">http://www.rfc-editor.org/info/rfc2119</a>.

<span id="RFC5246"></span><span class="bold">**RFC5246**</span>

Dierks, T. and E. Rescorla, <span class="quote">“<span class="quote">The
Transport Layer Security (TLS) Protocol Version 1.2</span>”</span>, RFC
5246, DOI 10.17487/RFC5246, August 2008,
<a href="http://www.rfc-editor.org/info/rfc5246" class="link"
target="_top">http://www.rfc-editor.org/info/rfc5246</a>.

<span id="RFC7748"></span><span class="bold">**RFC7748**</span>

Langley, A., Hamburg, M., and S. Turner,
<span class="quote">“<span class="quote">Elliptic Curves for
Security</span>”</span>, RFC 7748, January 2016,
<a href="https://www.rfc-editor.org/info/rfc7748" class="link"
target="_top">https://www.rfc-editor.org/info/rfc7748</a>.

</div>

</div>
