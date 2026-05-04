{ "title": "", "linkTitle": "Provider-side autoresponder extension",
"description": "", "url": "docs/specs/autoresponder.html", "date":
"2026-05-01T14:11:24.543410094-07:00", "draft": "false", "slug": "",
"layout": "", "type": "", "weight": "5" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="autoresponder"></span>Provider-side autoresponder extension (Kaetzchen)

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">Yawning</span> <span class="surname">Angel</span>

</div>

<div class="author">

### <span class="firstname">Kali</span> <span class="surname">Kaneko</span>

</div>

<div class="author">

### <span class="firstname">David</span> <span class="surname">Stainton</span>

</div>

</div>

</div>

<div>

<div class="abstract">

**Abstract**

This interface is meant to provide support for various autoresponder
agents <span class="quote">“<span class="quote">Kaetzchen</span>”</span>
that run on Katzenpost provider instances, thus bypassing the need to
run a discrete client instance to provide functionality. The use-cases
for such agents include, but are not limited to, user identity key
lookup, a discard address, and a loop-back responder for the purpose of
cover traffic.

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="toc">

**Table of Contents**

<span class="section">[Conventions Used in This
Document](#d58e35)</span>

<span class="section">[Terminology](#terminology)</span>

<span class="section">[1. Extension
Overview](#extension-overview)</span>

<span class="section">[1.1 Agent
Requirements](#agent-requirements)</span>

<span class="section">[1.2 Mix Message
Formats](#mix-message-formats)</span>

<span class="section">[2. PKI Extensions](#pki-extensions)</span>

<span class="section">[3. Anonymity
Considerations](#anonymity-considerations)</span>

<span class="section">[4. Security
Considerations](#security-considerations)</span>

<span class="section">[Acknowledgments](#acknowledgments)</span>

<span class="section">[References](#appendix-a.-references)</span>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="d58e35"></span>Conventions Used in This Document

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
<a href="#RFC2119" class="link">RFC2119</a>.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="terminology"></span>Terminology

</div>

</div>

</div>

The following terms are used in this specification.

<div class="variablelist">

<span class="term">SURB</span>  
Single use reply block. SURBs are used to achieve recipient anonymity,
that is to say, SURBs function as a cryptographic delivery token that
you can give to another client entity so that they can send you a
message without them knowing your identity or location on the network.
See `SPHINXSPEC` and `SPHINX`.

<span class="term">BlockSphinxPlaintext</span>  
The payload structure which is encapsulated by the Sphinx body.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="extension-overview"></span>1. Extension Overview

</div>

</div>

</div>

Each Kaetzchen agent will register as a potential recipient on its
Provider. When the Provider receives a forward packet destined for a
Kaetzchen instance, it will hand off the fully unwrapped packet along
with its corresponding SURB to the agent, which will then act on the
packet and optionally reply utilizing the SURB.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="agent-requirements"></span>1.1 Agent Requirements

</div>

</div>

</div>

<div class="itemizedlist">

- Each agent operation MUST be idempotent.

- Each agent operation request and response MUST fit within one Sphinx
  packet.

- Each agent SHOULD register a recipient address that is prefixed with
  (Or another standardized delimiter, agreed to by all participating
  providers in a given mixnet).

- Each agent SHOULD register a recipient address that consists of an
  RFC5322 dot-atom value, and MUST register recipient addresses that are
  at most 64 octets in length.

- The first byte of the agent's response payload MUST be 0x01 to allow
  clients to easily differentiate between SURB-ACKs and agent responses.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="mix-message-formats"></span>1.2 Mix Message Formats

</div>

</div>

</div>

Messages from clients to Kaetzchen use the following payload format in
the forward Sphinx packet:

``` programlisting
struct {
uint8_t flags;
uint8_t reserved; /* Set to 0x00. */
select (flags) {
case 0:
opaque padding[sizeof(SphinxSURB)];
case 1:
SphinxSURB surb;
}
opaque plaintext[];
} KaetzchenMessage;
```

The plaintext component of a `KaetzchenMessage` MUST be padded by
appending <span class="quote">“<span class="quote">0x00</span>”</span>
bytes to make the final total size of a `KaetzchenMessage` equal to that
of a `BlockSphinxPlaintext`.

Messages (replies) from the Kaetzchen to client use the following
payload format in the SURB generated packet:

``` programlisting
struct {
opaque plaintext[];
} KaetzchenReply;
```

The plaintext component of a `KaetzchenReply` MUST be padded by
appending <span class="quote">“<span class="quote">0x00</span>”</span>
bytes to make the final total size of a `KaetzchenReply` equal to that
of a `BlockSphinxPlaintext`

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="pki-extensions"></span>2. PKI Extensions

</div>

</div>

</div>

Each provider SHOULD publish the list of publicly accessible Kaetzchen
agent endpoints in its MixDescriptor, along with any other information
required to utilize the agent.

Provider should make this information available in the form of a map in
which the keys are the label used to identify a given service, and the
value is a map with arbitrary keys.

Valid service names refer to the services defined in extensions to this
specification. Every service MUST be implemented by one and only one
Kaetzchen agent.

For each service, the provider MUST advertise a field for the endpoint
at which the Kaetzchen agent can be reached, as a key value pair where
the key is `endpoint`, and the value is the provider side endpoint
identifier.

``` programlisting
{ "kaetzchen":
{ "keyserver" : {
"endpoint": "+keyserver",
"version" : 1 } },
{ "discard" : {
"endpoint": "+discard", } },
{ "loop" : {
"endpoint": "+loopback",
"restrictedToUsers": true } },
}
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="anonymity-considerations"></span>3. Anonymity Considerations

</div>

</div>

</div>

In the event that the mix keys for the entire return path are
compromised, it is possible for adversaries to unwrap the SURB and
determine the final recipient of the reply.

Depending on what sort of operations a given agent implements, there may
be additional anonymity impact that requires separate consideration.

Clients MUST NOT have predictable retransmission otherwise this makes
active confirmations attacks possible which could be used to discover
the ingress Provider of the client.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="security-considerations"></span>4. Security Considerations

</div>

</div>

</div>

It is possible to use this mechanism to flood a victim with unwanted
traffic by constructing a request with a SURB destined for the target.

Depending on the operations implemented by each agent, the added
functionality may end up being a vector for Denial of Service attacks in
the form of CPU or network overload.

Unless the agent implements additional encryption, message integrity and
privacy is limited to that which is provided by the base Sphinx packet
format and parameterization.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="acknowledgments"></span>Acknowledgments

</div>

</div>

</div>

The inspiration for this extension comes primarily from a design by
Vincent Breitmoser.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="appendix-a.-references"></span>References

</div>

</div>

</div>

<span id="KATZMIXPKI"></span><span class="bold">**KATZMIXPKI**</span>

Angel, Y., Piotrowska, A., Stainton, D.,
<span class="quote">“<span class="quote">Katzenpost Mix Network Public
Key Infrastructure Specification</span>”</span>, December 2017,
<a href="https://katzenpost.network/docs/specs/pdf/pki.pdf" class="link"
target="_top">https://katzenpost.network/docs/specs/pdf/pki.pdf</a>.

<span id="RFC2119"></span><span class="bold">**RFC2119**</span>

Bradner, S., <span class="quote">“<span class="quote">Key words for use
in RFCs to Indicate Requirement Levels</span>”</span>, BCP 14, RFC 2119,
DOI 10.17487/RFC2119, March 1997,
<a href="http://www.rfc-editor.org/info/rfc2119" class="link"
target="_top">http://www.rfc-editor.org/info/rfc2119</a>.

<span id="RFC5322"></span><span class="bold">**RFC5322**</span>

Resnick, P., Ed., <span class="quote">“<span class="quote">Internet
Message Format</span>”</span>, RFC 5322, DOI 10.17487/RFC5322, October
2008, <a href="https://www.rfc-editor.org/info/rfc5322" class="link"
target="_top">https://www.rfc-editor.org/info/rfc5322</a>.

<span id="SPHINX09"></span><span class="bold">**SPHINX09**</span>

Danezis, G., Goldberg, I.,
<span class="quote">“<span class="quote">Sphinx: A Compact and Provably
Secure Mix Format</span>”</span>, DOI 10.1109/SP.2009.15, May 2009,
<a href="https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf"
class="link"
target="_top">https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf</a>.

<span id="SPHINXSPEC"></span><span class="bold">**SPHINXSPEC**</span>

Angel, Y., Danezis, G., Diaz, C., Piotrowska, A., Stainton, D.,
<span class="quote">“<span class="quote">Sphinx Mix Network
Cryptographic Packet Format Specification</span>”</span>, July 2017,
<a href="https://katzenpost.network/docs/specs/pdf/sphinx.pdf"
class="link"
target="_top">https://katzenpost.network/docs/specs/pdf/sphinx.pdf</a>.

</div>

</div>
