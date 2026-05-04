{ "title": "" , "linkTitle": "Glossary" , "description": "" , "url":
"docs/specs/glossary.html" , "date":
"2026-05-01T16:00:49.311611406-07:00", "draft": "false" , "slug": "" ,
"layout": "" , "type": "" , "weight": "100" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="glossary"></span>Glossary

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="variablelist">

<span class="term"><span class="bold">**BlockSphinxPlaintext**</span></span>  
The payload structure which is encapsulated by the Sphinx body.

<span class="term"><span class="bold">**classes of traffic**</span></span>  
We distinguish the following classes of traffic:

<div class="itemizedlist">

- SURB Replies (also sometimes referred to as ACKs)

- Forward messages

</div>

<span class="term"><span class="bold">**client**</span></span>  
Software run by the User on its local device to participate in the
Mixnet. Again let us reiterate that a client is not considered a "node
in the network" at the level of analysis where we are discussing the
core mixnet protocol in this here document.

<span class="term"><span class="bold">**directory authority system**</span></span>  
Refers to specific PKI schemes used by Mixminion and Tor.

<span class="term"><span class="bold">**entry mix, entry node**</span></span>  
A mix that has some additional features:

<div class="itemizedlist">

- An entry mix is always the first hop in routes where the message
  originates from a client.

- An entry mix authenticates client’s direct connections via the
  mixnet’s wire protocol.

- An entry mix queues reply messages and allows clients to retrieve them
  later.

</div>

<span class="term"><span class="bold">**epoch**</span></span>  
A fixed time interval defined in section 4.2 Sphinx Mix and Provider Key
Rotation. The epoch is currently set to 20 minutes. A new PKI document
containing public key material is published for each epoch and is valid
only for that epoch.

<span class="term"><span class="bold">**family**</span></span>  
Identifier of security domains or entities operating one or more mixes
in the network. This is used to inform the path selection algorithm.

<span class="term"><span class="bold">**group**</span></span>  
A finite set of elements and a binary operation that satisfy the
properties of closure, associativity, invertability, and the presence of
an identity element.

<span class="term"><span class="bold">**group element**</span></span>  
An individual element of the group.

<span class="term"><span class="bold">**group generator**</span></span>  
A group element capable of generating any other element of the group,
via repeated applications of the generator and the group operation.

<span class="term"><span class="bold">**header**</span></span>  
The packet header consisting of several components, which convey the
information necessary to verify packet integrity and correctly process
the packet.

<span class="term"><span class="bold">**KiB**</span></span>  
Defined as 1024 8 bit octets.

<span class="term"><span class="bold">**Katzenpost**</span></span>  
A project to design many improved decryption mixnet protocols.

<span class="term"><span class="bold">**layer**</span></span>  
The layer indicates which network topology layer a particular mix
resides in.

<span class="term"><span class="bold">**message**</span></span>  
A variable-length sequence of octets sent anonymously through the
network. Short messages are sent in a single packet; long messages are
fragmented across multiple packets.

<span class="term"><span class="bold">**mix descriptor**</span></span>  
A database record which describes a component mix.

<span class="term"><span class="bold">**mix**</span></span>  
A cryptographic router that is used to compose a mixnet. Mixes use a
cryptographic operation on messages being routed which provides bitwise
unlinkability with respect to input versus output messages. Katzenpost
is a decryption mixnet that uses the Sphinx cryptographic packet format.

<span class="term"><span class="bold">**mixnet**</span></span>  
A mixnet also known as a mix network is a network of mixes that can be
used to build various privacy preserving protocols.

<span class="term"><span class="bold">**MSL**</span></span>  
Maximum segment lifetime, currently set to 120 seconds.

<span class="term"><span class="bold">**nickname**</span></span>  
A nickname string that is unique in the consensus document, see
Katzenpost Mix Network Specification section 2.2. Network Topology.

<span class="term"><span class="bold">**node**</span></span>  
Clients are NOT considered nodes in the mix network. However note that
network protocols are often layered; in our design documents we describe
"mixnet hidden services" which can be operated by mixnet clients.
Therefore if you are using node in some adherence to mathematical
terminology one could conceivably designate a client as a node. That
having been said, it would not be appropriate to the discussion of our
core mixnet protocol to refer to the clients as nodes.

<span class="term"><span class="bold">**packet**</span></span>  
A Sphinx packet, of fixed length for each class of traffic, carrying a
message payload and metadata for routing. Packets are routed anonymously
through the mixnet and cryptographically transformed at each hop.

<span class="term"><span class="bold">**payload**</span></span>  
The fixed-length portion of a packet containing an encrypted message or
part of a message, to be delivered anonymously.

<span class="term"><span class="bold">**PKI**</span></span>  
Public key infrastructure

<span class="term"><span class="bold">**provider**</span></span>  
A service operated by a third party that Clients communicate directly
with to communicate with the Mixnet. It is responsible for Client
authentication, forwarding outgoing messages to the Mixnet, and storing
incoming messages for the Client. The Provider MUST have the ability to
perform cryptographic operations on the relayed messages.

<span class="term"><span class="bold">**SEDA**</span></span>  
Staged Event Driven Architecture. 1. A highly parallelizable computation
model. 2. A computational pipeline composed of multiple stages connected
by queues utilizing active queue management algorithms that can evict
items from the queue based on dwell time or other criteria where each
stage is a thread pool. 3. The only correct way to efficiently implement
a software based router on general purpose computing hardware.

<span class="term"><span class="bold">**service mix**</span></span>  
A service mix is a mix that has some additional features:

<div class="itemizedlist">

- A service mix is always the last hop in routes where the message
  originates from a client.

- A service mix runs mixnet services which use a Sphinx SURB based
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
Refers to our PQ Noise based protocol which currently uses TCP but in
the near future will optionally use QUIC. This protocol has messages
known as wire protocol `commands`, which are used for various mixnet
functions such as sending or retrieving a message, dirauth voting etc.
For more information, please see our design doc: <a
href="https://github.com/katzenpost/katzenpost/blob/main/docs/specs/wire-protocol.md"
class="link" target="_top">wire protocol specification</a>

</div>

</div>
