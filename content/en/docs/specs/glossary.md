---
title: ""
linkTitle: "Glossary"
description: ""
author: ""
url: ""
date: "2026-06-02T10:58:08.168023907-07:00"
draft: "false"
slug: "glossary"
layout: ""
type: ""
weight: "90"
version: ""
---

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="glossary"></span>Glossary

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="variablelist">

<span class="term"><span class="bold">**BlockSphinxPlaintext**</span></span>  
The payload structure that is encapsulated by the Sphinx body.

<span class="term"><span class="bold">**classes of traffic**</span></span>  
We distinguish the following classes of traffic:

<div class="itemizedlist">

- SURB replies (sometimes referred to as ACKs)

- Forwarded messages

</div>

<span class="term"><span class="bold">**client**</span></span>  
Software run by a user on their local device to participate in the mixnet.
A client is not considered a node in the
network for purposes of analysis of the core mnixnet protocols.

<span class="term"><span class="bold">**directory authority system**</span></span>  
Refers to PKI schemes used by Mixminion and Tor.

<span class="term"><span class="bold">**entry mix, entry node**</span></span>  
A mix node that has some additional features:

<div class="itemizedlist">

- An entry mix is always the first hop in routes where the message
  originates from a client.

- An entry mix authenticates client’s direct connections via the
  mixnet’s wire protocol.

- An entry mix queues reply messages and allows clients to retrieve
  them later.

</div>

<span class="term"><span class="bold">**epoch**</span></span>  
A fixed-time interval with a current default value of 20 minutes.
A new PKI document containing public key material
is published for each epoch and is valid only for that epoch. For more information,
see
<a href="https://katzenpost.network/docs/specs/mix_network/#sphinx-mix-and-provider-key-rotation" class="link" target="_top">Sphinx
mix and provider key rotation</a>.

<span class="term"><span class="bold">**family**</span></span>  
Identifier of security domains or entities operating one or more mix nodes in
the network. This is used to inform the path selection algorithm.

<span class="term"><span class="bold">**gateway**</span></span>  
A mix node on the edge of the mixnet that is the first hop for messages coming from
clients.
The gateway authenticates client connections and queues reply messages (SURBs) for
retrieval.

<span class="term"><span class="bold">**group**</span></span>  
A finite set of elements and a binary operation that satisfy the
properties of closure, associativity, invertability, and the presence of an
identity element.

<span class="term"><span class="bold">**group element**</span></span>  
An individual element of a group.

<span class="term"><span class="bold">**group generator**</span></span>  
A group element capable of generating any other element of a group, via
repeated applications of the generator and the group operation.

<span class="term"><span class="bold">**header**</span></span>  
The packet header consisting of several components which convey the
information necessary to verify packet integrity and to correctly process the
packet.

<span class="term"><span class="bold">**KiB**</span></span>  
Defined as 1024 8 bit octets.

<span class="term"><span class="bold">**layer**</span></span>  
The layer value indicates which network topology layer a particular mix node resides
in.

<span class="term"><span class="bold">**message**</span></span>  
A variable-length sequence of octets sent anonymously through the network.
Short messages are sent in a single packet; long messages are fragmented
across multiple packets.

<span class="term"><span class="bold">**mix descriptor**</span></span>  
A database record that describes a mixnet server component.

<span class="term"><span class="bold">**mix node**</span></span>  
A cryptographic router that is used to compose a mixnet. Mix nodes use a
cryptographic operation on messages being routed which provides bitwise
unlinkability with respect to input versus output messages. Katzenpost is a
decryption mixnet that uses the Sphinx cryptographic packet format.

<span class="term"><span class="bold">**mixnet**</span></span>  
A mixnet, or mix network, is a network of mix servers that can be
used to build various privacy-preserving protocols.

<span class="term"><span class="bold">**MSL**</span></span>  
Maximum segment lifetime, currently set to 120 seconds.

<span class="term"><span class="bold">**nickname**</span></span>  
A component nickname string that must be unique in the consensus document.

<span class="term"><span class="bold">**node**</span></span>  
Clients are NOT considered nodes in the mix network. However,
network protocols are often layered. In our design documents, we describe
"mixnet hidden services" that can be operated by mixnet clients. Therefore
if you are using the term "node" in some adherence to mathematical terminology, one
could conceivably designate a client as a node. However, in discussion of our core
mixnet protocol, it is inappropriate to refer to clients as nodes.

<span class="term"><span class="bold">**packet**</span></span>  
A Sphinx packet, of fixed
length for each class of traffic, carrying a message payload and metadata for routing.
Packets are routed anonymously through the mixnet and cryptographically transformed
at
each hop.

<span class="term"><span class="bold">**payload**</span></span>  
The fixed-length portion of a packet containing an encrypted message or
part of a message, to be delivered anonymously.

<span class="term"><span class="bold">**PKI**</span></span>  
Public key infrastructure.

<span class="term"><span class="bold">**SEDA**</span></span>  
Staged Event Driven Architecture. 1. A
highly parallelizable computation model. 2. A computational pipeline
composed of multiple stages connected by queues utilizing active
queue-management algorithms that can evict items from a queue based on dwell
time or other criteria where each stage is a thread pool. 3. The only
correct way to efficiently implement a software based router on general
purpose computing hardware.

<span class="term"><span class="bold">**service node**</span></span>  
A service node is a mix node with additional features:

<div class="itemizedlist">

- A service node is always the last hop in routes where the message
  originates from a client.

- A service node runs mixnet services which use a Sphinx SURB-based
  protocol.

</div>

<span class="term"><span class="bold">**SURB**</span></span>  
Single use reply block. SURBs are used to achieve recipient anonymity,
that is to say, SURBs function as a cryptographic delivery token that
you can give to another client entity so that they can send you a
message without them knowing your identity or location on the network.
See `SPHINXSPEC` and `SPHINX`.

<span class="term"><span class="bold">**user**</span></span>  
An agent using the Katzenpost system.

<span class="term"><span class="bold">**wire protocol**</span></span>  
Refers to our PQ Noise-based protocol that currently uses TCP but in the
near future will optionally use QUIC. This protocol has messages known as
wire protocol `commands`, which are used for various mixnet
functions such as sending or retrieving a message and dirauth voting. For
more information, see our <a href="https://github.com/katzenpost/katzenpost/blob/main/docs/specs/wire-protocol.md" class="link" target="_top">wire protocol specification</a>.

</div>

</div>
