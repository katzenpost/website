{ "title":"Sphinx cryptographic packet format" , "linkTitle":"Sphinx cryptographic packet format" , "description":"" , "author":"" , "url":"" , "date":"2026-05-10T15:27:25.195144824-07:00" , "draft":"false" , "slug":"sphinx_format" , "layout":"" , "type":"" , "weight":"1" , "version":"" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="sphinx"></span>Sphinx cryptographic packet format

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">Yawning</span> <span class="surname">Angel</span>

</div>

<div class="author">

### <span class="firstname">George</span> <span class="surname">Danezis</span>

</div>

<div class="author">

### <span class="firstname">Claudia</span> <span class="surname">Diaz</span>

</div>

<div class="author">

### <span class="firstname">Ania</span> <span class="surname">Piotrowska</span>

</div>

<div class="author">

### <span class="firstname">David</span> <span class="surname">Stainton</span>

</div>

</div>

</div>

<div>

<div class="abstract">

**Abstract**

This document defines the Sphinx cryptographic packet format for decryption mix networks, and provides a parameterization based around generic cryptographic primitives types. This document does not introduce any new crypto, but is meant to serve as an implementation guide.

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="toc">

**Table of Contents**

<span class="section">[Terminology](#terminology)</span>

<span class="section">[Conventions Used in This Document](#conventions-used-in-this-document)</span>

<span class="section">[1. Introduction](#sphinx_introduction)</span>

<span class="section">[2. Cryptographic Primitives](#cryptographic-primitives)</span>

<span class="section">[2.1 Sphinx Key Derivation Function](#sphinx-key-derivation-function)</span>

<span class="section">[3. Sphinx Packet Parameters](#sphinx-packet-parameters)</span>

<span class="section">[3.1 Sphinx Parameter Constants](#sphinx-parameter-constants)</span>

<span class="section">[3.2 Sphinx Packet Geometry](#sphinx-packet-geometry)</span>

<span class="section">[4. The Sphinx Cryptographic Packet Structure](#the-sphinx-cryptographic-packet-structure)</span>

<span class="section">[4.1 Sphinx Packet Header](#sphinx-packet-header)</span>

<span class="section">[4.1.1 Per-hop routing information](#per-hop-routing-information)</span>

<span class="section">[4.2 Sphinx Packet Payload](#sphinx-packet-payload)</span>

<span class="section">[5. Sphinx Packet Creation](#sphinx-packet-creation)</span>

<span class="section">[5.1 Create a Sphinx Packet Header](#create-a-sphinx-packet-header)</span>

<span class="section">[5.2 Create a Sphinx Packet](#create-a-sphinx-packet)</span>

<span class="section">[6. Sphinx Packet Processing](#sphinx-packet-processing)</span>

<span class="section">[6.1 Sphinx_Unwrap Operation](#sphinx_unwrap-operation)</span>

<span class="section">[7. Single Use Reply Block (SURB) Creation](#single-use-reply-block-surb-creation)</span>

<span class="section">[8. Single Use Reply Block Replies](#single-use-reply-block-replies)</span>

<span class="section">[9. Anonymity Considerations](#anonymity-considerations)</span>

<span class="section">[10. Security Considerations](#security-considerations)</span>

<span class="section">[References](#appendix-a.-references)</span>

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

<span class="term"><span class="bold">**message**</span></span>  
A variable-length sequence of octets sent anonymously through the network. Short messages are sent in a single packet; long messages are fragmented across multiple packets.

<span class="term"><span class="bold">**packet**</span></span>  
A Sphinx packet, of fixed length for each class of traffic, carrying a message payload and metadata for routing. Packets are routed anonymously through the mixnet and cryptographically transformed at each hop.

<span class="term"><span class="bold">**header**</span></span>  
The packet header consisting of several components, which convey the information necessary to verify packet integrity and correctly process the packet.

<span class="term"><span class="bold">**payload**</span></span>  
The fixed-length portion of a packet containing an encrypted message or part of a message, to be delivered anonymously.

<span class="term"><span class="bold">**group element**</span></span>  
An individual element of the group.

<span class="term"><span class="bold">**group generator**</span></span>  
A group element capable of generating any other element of the group, via repeated applications of the generator and the group operation.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="conventions-used-in-this-document"></span>Conventions Used in This Document

</div>

</div>

</div>

The key words <span class="quote">“<span class="quote">MUST</span>”</span>, <span class="quote">“<span class="quote">MUST NOT</span>”</span>, <span class="quote">“<span class="quote">REQUIRED</span>”</span>, <span class="quote">“<span class="quote">SHALL</span>”</span>, <span class="quote">“<span class="quote">SHALL NOT</span>”</span>, <span class="quote">“<span class="quote">SHOULD</span>”</span>, <span class="quote">“<span class="quote">SHOULD NOT</span>”</span>, <span class="quote">“<span class="quote">RECOMMENDED</span>”</span>, <span class="quote">“<span class="quote">MAY</span>”</span>, and <span class="quote">“<span class="quote">OPTIONAL</span>”</span> in this document are to be interpreted as described in <a href="#RFC2119" class="link">RFC2119</a>.

The <span class="emphasis">*C*</span> style Presentation Language as described in <a href="#RFC5246" class="link">RFC5246</a> Section 4 is used to represent data structures, except for cryptographic attributes, which are specified as opaque byte vectors.

<div class="itemizedlist">

- `x | y` denotes the concatenation of x and y.

- `x ^ y` denotes the bitwise XOR of x and y.

- `byte` an 8-bit octet.

- `x[a:b]` denotes the sub-vector of x where a/b denote the start/end byte indexes (inclusive-exclusive); a/b may be omitted to signify the start/end of the vector x respectively.

- `x[y]` denotes the y'th element of list x.

- `x.len` denotes the length of list x.

- `ZEROBYTES(N)` denotes N bytes of 0x00.

- `RNG(N)` denotes N bytes of cryptographic random data.

- `LEN(N)` denotes the length in bytes of N.

- `CONSTANT_TIME_CMP(x, y)` denotes a constant time comparison between the byte vectors x and y, returning true iff x and y are equal.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="sphinx_introduction"></span>1. Introduction

</div>

</div>

</div>

The Sphinx cryptographic packet format is a compact and provably secure design introduced by George Danezis and Ian Goldberg <a href="#SPHINX09" class="link">SPHINX09</a>. It supports a full set of security features: indistinguishable replies, hiding the path length and relay position, detection of tagging attacks and replay attacks, as well as providing unlinkability for each leg of the packet’s journey over the network.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="cryptographic-primitives"></span>2. Cryptographic Primitives

</div>

</div>

</div>

This specification uses the following cryptographic primitives as the foundational building blocks for Sphinx:

<div class="itemizedlist">

- `H(M)` - A cryptographic hash function which takes an octet array M to produce a digest consisting of a `HASH_LENGTH` byte octet array. `H(M)` MUST be pre-image and collision resistant.

- `MAC(K, M)` - A cryptographic message authentication code function which takes a `M_KEY_LENGTH` byte octet array key `K` and arbitrary length octet array message `M` to produce an authentication tag consisting of a `MAC_LENGTH` byte octet array.

- `KDF(SALT, IKM)` - A key derivation function which takes an arbitrary length octet array salt `SALT` and an arbitrary length octet array initial key `IKM`, to produce an octet array of arbitrary length.

- `S(K, IV)` - A pseudo-random generator (stream cipher) which takes a `S_KEY_LENGTH` byte octet array key `K` and a `S_IV_LENGTH` byte octet array initialization vector `IV` to produce an octet array key stream of arbitrary length.

- `SPRP_Encrypt(K, M)/SPRP_Decrypt(K, M)` - A strong pseudo-random permutation (SPRP) which takes a `SPRP_KEY_LENGTH` byte octet array key `K` and arbitrary length message `M`, and produces the encrypted ciphertext or decrypted plaintext respectively.

  When used with the default payload authentication mechanism, the SPRP MUST be "fragile" in that any amount of modifications to `M` results in a large number of unpredictable changes across the whole message upon a `SPRP_Encrypt()` or `SPRP_Decrypt()` operation.

- `EXP(X, Y)` - An exponentiation function which takes the `GROUP_ELEMENT_LENGTH` byte octet array group elements `X` and `Y`, and returns `X ^^ Y` as a `GROUP_ELEMENT_LENGTH` byte octet array.

  Let `G` denote the generator of the group, and `EXP_KEYGEN()` return a `GROUP_ELEMENT_LENGTH` byte octet array group element usable as private key.

  The group defined by `G` and `EXP(X, Y)` MUST satisfy the Decision Diffie-Hellman problem.

- `EXP_KEYGEN()` - Returns a new "suitable" private key for `EXP()`.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="sphinx-key-derivation-function"></span>2.1 Sphinx Key Derivation Function

</div>

</div>

</div>

Sphinx Packet creation and processing uses a common Key Derivation Function (KDF) to derive the required MAC and symmetric cryptographic keys from a per-hop shared secret.

The output of the KDF is partitioned according to the following structure:

``` programlisting
struct {
opaque header_mac[M_KEY_LENGTH];
opaque header_encryption[S_KEY_LENGTH];
opaque header_encryption_iv[S_IV_LENGTH];
opaque payload_encryption[SPRP_KEY_LENGTH]
opaque blinding_factor[GROUP_ELEMENT_LENGTH];
} SphinxPacketKeys;

Sphinx_KDF( info, shared_secret ) -> packet_keys
```

Inputs:

<div class="itemizedlist">

- `info` The optional context and application specific information.

- `shared_secret` The per-hop shared secret derived from the Diffie-Hellman key exchange.

</div>

Outputs:

<div class="itemizedlist">

- `packet_keys` The SphinxPacketKeys required to handle packet creation or processing.

</div>

The output packet_keys is calculated as follows:

``` programlisting
kdf_out = KDF( info, shared_secret )
packet_keys = kdf_out[:LEN( SphinxPacketKeys )]
```

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="sphinx-packet-parameters"></span>3. Sphinx Packet Parameters

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="sphinx-parameter-constants"></span>3.1 Sphinx Parameter Constants

</div>

</div>

</div>

The Sphinx Packet Format is parameterized by the implementation based on the application and security requirements.

<div class="itemizedlist">

- `AD_LENGTH` - The constant amount of per-packet unencrypted additional data in bytes.

- `PAYLOAD_TAG_LENGTH` - The length of the message payload authentication tag in bytes. This SHOULD be set to at least 16 bytes (128 bits).

- `PER_HOP_RI_LENGTH` - The length of the per-hop Routing Information (`Section 4.1.1 <4.1.1>`) in bytes.

- `NODE_ID_LENGTH` - The node identifier length in bytes.

- `RECIPIENT_ID_LENGTH` - The recipient identifier length in bytes.

- `SURB_ID_LENGTH` - The Single Use Reply Block (`Section 7 <7.0>`) identifier length in bytes.

- `MAX_HOPS` - The maximum number of hops a packet can traverse.

- `PAYLOAD_LENGTH` - The per-packet message payload length in bytes, including a `PAYLOAD_TAG_LENGTH` byte authentication tag.

- `KDF_INFO` - A constant opaque byte vector used as the info parameter to the KDF for the purpose of domain separation.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="sphinx-packet-geometry"></span>3.2 Sphinx Packet Geometry

</div>

</div>

</div>

The Sphinx Packet Geometry is derived from the Sphinx Parameter Constants `Section 3.1`. These are all derived parameters, and are primarily of interest to implementors.

<div class="itemizedlist">

- `ROUTING_INFO_LENGTH` - The total length of the "routing information" Sphinx Packet Header component in bytes:

</div>

``` programlisting
ROUTING_INFO_LENGTH = PER_HOP_RI_LENGTH * MAX_HOPS
```

<div class="itemizedlist">

- `HEADER_LENGTH` - The length of the Sphinx Packet Header in bytes:

</div>

``` programlisting
HEADER_LENGTH = AD_LENGTH + GROUP_ELEMENT_LENGTH + ROUTING_INFO_LENGTH + MAC_LENGTH
```

<div class="itemizedlist">

- `PACKET_LENGTH` - The length of the Sphinx Packet in bytes:

</div>

``` programlisting
PACKET_LENGTH = HEADER_LENGTH + PAYLOAD_LENGTH
```

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="the-sphinx-cryptographic-packet-structure"></span>4. The Sphinx Cryptographic Packet Structure

</div>

</div>

</div>

Each Sphinx Packet consists of two parts: the Sphinx Packet Header and the Sphinx Packet Payload:

``` programlisting
struct {
opaque header[HEADER_LENGTH];
opaque payload[PAYLOAD_LENGTH];
} SphinxPacket;
```

<div class="itemizedlist">

- `header` - The packet header consists of several components, which convey the information necessary to verify packet integrity and correctly process the packet.

- `payload` - The application message data.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="sphinx-packet-header"></span>4.1 Sphinx Packet Header

</div>

</div>

</div>

The Sphinx Packet Header refers to the block of data immediately preceding the Sphinx Packet Payload in a Sphinx Packet.

The structure of the Sphinx Packet Header is defined as follows:

``` programlisting
struct {
opaque additional_data[AD_LENGTH]; /* Unencrypted. */
opaque group_element[GROUP_ELEMENT_LENGTH];
opaque routing_information[ROUTING_INFO_LENGTH];
opaque MAC[MAC_LENGTH];
} SphinxHeader;
```

<div class="itemizedlist">

- `additional_data` - Unencrypted per-packet Additional Data (AD) that is visible to every hop. The AD is authenticated on a per-hop basis.

  As the additional_data is sent in the clear and traverses the network unaltered, implementations MUST take care to ensure that the field cannot be used to track individual packets.

- `group_element` - An element of the cyclic group, used to derive the per-hop key material required to authenticate and process the rest of the SphinxHeader and decrypt a single layer of the Sphinx Packet Payload encryption.

- `routing_information` - A vector of per-hop routing information, encrypted and authenticated in a nested manner. Each element of the vector consists of a series of routing commands, specifying all of the information required to process the packet.

  The precise encoding format is specified in `Section 4.1.1 <4.1.1>`.

- `MAC` - A message authentication code tag covering the additional_data, group_element, and routing_information.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="per-hop-routing-information"></span>4.1.1 Per-hop routing information

</div>

</div>

</div>

The routing_information component of the Sphinx Packet Header contains a vector of per-hop routing information. When processing a packet, the per hop processing is set up such that the first element in the vector contains the routing commands for the current hop.

The structure of the routing information is as follows:

``` programlisting
struct {
RoutingCommand routing_commands<1..2^8-1>; /* PER_HOP_RI_LENGTH bytes */
opaque encrypted_routing_commands[ROUTING_INFO_LENGTH - PER_HOP_RI_LENGTH];
} RoutingInformation;
```

The structure of a single routing command is as follows:

``` programlisting
struct {
RoutingCommandType command;
select (RoutingCommandType) {
case null:               NullCommand;
case next_node_hop:      NextNodeHopCommand;
case recipient:          RecipientCommand;
case surb_reply:         SURBReplyCommand;
};
} RoutingCommand;
```

The following routing commands are currently defined:

``` programlisting
enum {
null(0),
next_node_hop(1),
recipient(2),
surb_reply(3),

/* Routing commands between 0 and 0x7f are reserved. */

(255)
} RoutingCommandType;
```

The null routing command structure is as follows:

``` programlisting
struct {
opaque padding<0..PER_HOP_RI_LENGTH-1>;
} NullCommand;
```

The next_node_hop command structure is as follows:

``` programlisting
struct {
opaque next_hop[NODE_ID_LENGTH];
opaque MAC[MAC_LENGTH];
} NextNodeHopCommand;
```

The recipient command structure is as follows:

``` programlisting
struct {
opaque recipient[RECIPEINT_ID_LENGTH];
} RecipientCommand;
```

The surb_reply command structure is as follows:

``` programlisting
struct {
opaque id[SURB_ID_LENGTH];
} SURBReplyCommand;
```

While the `NullCommand` padding field is specified as opaque, implementations SHOULD zero fill the padding. The choice of `0x00` as the terminal NullCommand is deliberate to ease implementation, as `ZEROBYTES(N)` produces a valid NullCommand RoutingCommand, resulting in <span class="quote">“<span class="quote">appending zero filled padding</span>”</span> producing valid output.

Implementations MUST pad the routing_commands vector so that it is exactly `PER_HOP_RI_LENGTH` bytes, by appending a terminal NullCommand if necessary.

Every non-terminal hop’s `routing_commands` MUST include a `NextNodeHopCommand`.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="sphinx-packet-payload"></span>4.2 Sphinx Packet Payload

</div>

</div>

</div>

The Sphinx Packet Payload refers to the block of data immediately following the Sphinx Packet Header in a Sphinx Packet.

For most purposes the structure of the Sphinx Packet Payload can be treated as a single contiguous byte vector of opaque data.

Upon packet creation, the payload is repeatedly encrypted (unless it is a SURB Reply, see `Section 7.0` via keys derived from the Diffie-Hellman key exchange between the packet's `group_element` and the public key of each node in the path.

Authentication of packet integrity is done by prepending a tag set to a known value to the plaintext prior to the first encrypt operation. By virtue of the fragile nature of the SPRP function, any alteration to the encrypted payload as it traverses the network will result in an irrecoverably corrupted plaintext when the payload is decrypted by the recipient.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="sphinx-packet-creation"></span>5. Sphinx Packet Creation

</div>

</div>

</div>

For the sake of brevity, the pseudocode for all of the operations will take a vector of the following PathHop structure as a parameter named path\[\] to specify the path a packet will traverse, along with the per-hop routing commands and per-hop public keys.

``` programlisting
struct {
/* There is no need for a node_id here, as
routing_commands[0].next_hop specifies that
information for all non-terminal hops. */
opaque public_key[GROUP_ELEMENT_LENGTH];
RoutingCommand routing_commands<1...2^8-1>;
} PathHop;
```

It is assumed that each routing_commands vector except for the terminal entry contains at least a RoutingCommand consisting of a partially assembled NextNodeHopCommand with the `next_hop` element filled in with the identifier of the next hop.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="create-a-sphinx-packet-header"></span>5.1 Create a Sphinx Packet Header

</div>

</div>

</div>

Both the creation of a Sphinx Packet and the creation of a SURB requires the generation of a Sphinx Packet Header, so it is specified as a distinct operation.

``` programlisting
Sphinx_Create_Header( additional_data, path[] ) -> sphinx_header,
               payload_keys
```

Inputs:

<div class="itemizedlist">

- `additional_data` The Additional Data that is visible to every node along the path in the header.

- `path` The vector of PathHop structures in hop order, specifying the node id, public key, and routing commands for each hop.

</div>

Outputs: `sphinx_header` The resulting Sphinx Packet Header.

<div class="itemizedlist">

- `payload_keys` The vector of SPRP keys used to encrypt the Sphinx Packet Payload, in hop order.

</div>

The `Sphinx_Create_Header` operation consists of the following steps:

<div class="orderedlist">

1.  Derive the key material for each hop.

</div>

``` programlisting
num_hops = route.len
route_keys = [ ]
route_group_elements = [ ]
priv_key = EXP_KEYGEN()

/* Calculate the key material for the 0th hop. */
group_element = EXP( G, priv_key )
route_group_elements += group_element
shared_secret = EXP( path[0].public_key, priv_key )
route_keys += Sphinx_KDF( KDF_INFO, shared_secret )
blinding_factor = keys[0].blinding_factor

/* Calculate the key material for rest of the hops. */
for i = 1; i < num_hops; ++i:
shared_secret = EXP( path[i].public_key, priv_key )
for j = 0; j < i; ++j:
shared_secret = EXP( shared_secret, keys[j].blinding_factor )
route_keys += Sphinx_KDF( KDF_INFO, shared_secret )
group_element = EXP( group_element, keys[i-1].blinding_factor )
route_group_elements += group_element
```

At the conclusion of the derivation process:

<div class="itemizedlist">

- `route_keys` - A vector of per-hop SphinxKeys.

- `route_group_elements` - A vector of per-hop group elements.

</div>

<div class="orderedlist">

1.  Derive the routing_information keystream and encrypted padding for each hop.

</div>

``` programlisting
ri_keystream = [ ]
ri_padding = [ ]

for i = 0; i < num_hops; ++i:
keystream = ZEROBYTES( ROUTING_INFO_LENGTH + PER_HOP_RI_LENGTH ) ^
S( route_keys[i].header_encryption,
route_keys[i].header_encryption_iv )
ks_len = LEN( keystream ) - (i + 1) * PER_HOP_RI_LENGTH

padding = keystream[ks_len:]
if i > 0:
prev_pad_len = LEN( ri_padding[i-1] )
padding = padding[:prev_pad_len] ^ ri_padding[i-1] |
padding[prev_pad_len]

ri_keystream += keystream[:ks_len]
ri_padding += padding

At the conclusion of the derivation process:
ri_keystream - A vector of per-hop routing_information
encryption keystreams.
ri_padding   - The per-hop encrypted routing_information
padding.
```

<div class="orderedlist">

1.  Create the routing_information block.

</div>

``` programlisting
/* Start with the terminal hop, and work backwards. */
i = num_hops - 1

/* Encode the terminal hop's routing commands. As the
terminal hop can never have a NextNodeHopCommand, there
are no per-hop alterations to be made. */
ri_fragment = path[i].routing_commands |
ZEROBYTES( PER_HOP_RI_LENGTH - LEN( path[i].routing_commands ) )

/* Encrypt and MAC. */
ri_fragment ^= ri_keystream[i]
mac = MAC( route_keys[i].header_mac, additional_data |
route_group_elements[i] | ri_fragment |
ri_padding[i-1] )
routing_info = ri_fragment
if num_hops < MAX_HOPS:
pad_len = (MAX_HOPS - num_hops) * PER_HOP_RI_LENGTH
routing_info = routing_info | RNG( pad_len )

/* Calculate the routing info for the rest of the hops. */
for i = num_hops - 2; i >= 0; --i:
cmds_to_encode = [ ]

/* Find and finalize the NextNodeHopCommand. */
for j = 0; j < LEN( path[i].routing_commands; j++:
cmd = path[i].routing_commands[j]
if cmd.command == next_node_hop:
/* Finalize the NextNodeHopCommand. */
cmd.MAC = mac
cmds_to_encode = cmds_to_encode + cmd /* Append */

/* Append a terminal NullCommand. */
ri_fragment = cmds_to_encode |
ZEROBYTES( PER_HOP_RI_LENGTH - LEN( cmds_to_encode ) )

/* Encrypt and MAC */
routing_info = ri_fragment | routing_info /* Prepend. */
routing_info ^= ri_keystream[i]
if i > 0:
mac = MAC( route_keys[i].header_mac, additional_data |
route_group_elements[i] | routing_info |
ri_padding[i-1] )
else:
mac = MAC( route_keys[i].header_mac, additional_data |
route_group_elements[i] | routing_info )

At the conclusion of the derivation process:
routing_info - The completed routing_info block.
mac          - The MAC for the 0th hop.
```

<div class="orderedlist">

1.  Assemble the completed Sphinx Packet Header and Sphinx Packet Payload SPRP key vector.

</div>

``` programlisting
/* Assemble the completed Sphinx Packet Header. */
SphinxHeader sphinx_header
sphinx_header.additional_data = additional_data
sphinx_header.group_element = route_group_elements[0] /* From step 1. */
sphinx_header.routing_info = routing_info   /* From step 3. */
sphinx_header.mac = mac                     /* From step 3. */

/* Preserve the Sphinx Payload SPRP keys, to return to the
caller. */
payload_keys = [ ]
for i = 0; i < nr_hops; ++i:
payload_keys += route_keys[i].payload_encryption

At the conclusion of the assembly process:
sphinx_header - The completed sphinx_header, to be returned.
payload_keys  - The vector of SPRP keys, to be returned.
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="create-a-sphinx-packet"></span>5.2 Create a Sphinx Packet

</div>

</div>

</div>

``` programlisting
Sphinx_Create_Packet( additional_data, path[], payload ) -> sphinx_packet
```

Inputs:

<div class="itemizedlist">

- `additional_data` The Additional Data that is visible to every node along the path in the header.

- `path` The vector of PathHop structures in hop order, specifying the node id, public key, and routing commands for each hop.

- `payload` The packet payload message plaintext.

</div>

Outputs:

<div class="itemizedlist">

- `sphinx_packet` The resulting Sphinx Packet.

</div>

The `Sphinx_Create_Packet` operation consists of the following steps:

<div class="orderedlist">

1.  Create the Sphinx Packet Header and SPRP key vector.

</div>

``` programlisting
sphinx_header, payload_keys =
Sphinx_Create_Header( additional_data, path )
```

<div class="orderedlist">

1.  Prepend the authentication tag, and append padding to the payload.

</div>

``` programlisting
payload = ZERO_BYTES( PAYLOAD_TAG_LENGTH ) | payload
payload = payload | ZERO_BYTES( PAYLOAD_LENGTH - LEN( payload ) )
```

<div class="orderedlist">

1.  Encrypt the payload.

</div>

``` programlisting
for i = nr_hops - 1; i >= 0; --i:
payload = SPRP_Encrypt( payload_keys[i], payload )
```

<div class="orderedlist">

1.  Assemble the completed Sphinx Packet.

</div>

``` programlisting
SphinxPacket sphinx_packet
sphinx_packet.header = sphinx_header
sphinx_packet.payload = payload
```

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="sphinx-packet-processing"></span>6. Sphinx Packet Processing

</div>

</div>

</div>

Mix nodes process incoming packets first by performing the `Sphinx_Unwrap` operation to authenticate and decrypt the packet, and if applicable prepare the packet to be forwarded to the next node.

If `Sphinx_Unwrap` returns an error for any given packet, the packet MUST be discarded with no additional processing.

After a packet has been unwrapped successfully, a replay detection tag is checked to ensure that the packet has not been seen before. If the packet is a replay, the packet MUST be discarded with no additional processing.

The routing commands for the current hop are interpreted and executed, and finally the packet is forwarded to the next mix node over the network or presented to the application if the current node is the final recipient.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="sphinx_unwrap-operation"></span>6.1 Sphinx_Unwrap Operation

</div>

</div>

</div>

The `Sphinx_Unwrap` operation is the majority of the per-hop packet processing, handling authentication, decryption, and modifying the packet prior to forwarding it to the next node.

``` programlisting
Sphinx_Unwrap( routing_private_key, sphinx_packet ) -> sphinx_packet,
                  routing_commands,
                  replay_tag
```

Inputs:

<div class="itemizedlist">

- `private_routing_key` A group element GROUP_ELEMENT_LENGTH bytes in length, that serves as the unwrapping Mix’s private key.

- `sphinx_packet` A Sphinx packet to unwrap.

</div>

Outputs:

<div class="itemizedlist">

- `error` Indicating a unsuccessful unwrap operation if applicable.

- `sphinx_packet` The resulting Sphinx packet.

- `routing_commands` A vector of RoutingCommand, specifying the post unwrap actions to be taken on the packet.

- `replay_tag` A tag used to detect whether this packet was processed before.

</div>

The `Sphinx_Unwrap` operation consists of the following steps:

<div class="orderedlist">

1.  (Optional) Examine the Sphinx Packet Header’s Additional Data.

</div>

If the header’s `additional_data` element contains information required to complete the unwrap operation, such as specifying the packet format version or the cryptographic primitives used examine it now.

Implementations MUST NOT treat the information in the `additional_data` element as trusted until after the completion of Step 3 (<span class="quote">“<span class="quote">Validate the Sphinx Packet Header</span>”</span>).

<div class="orderedlist">

1.  Calculate the hop's shared secret, and replay_tag.

</div>

``` programlisting
hdr = sphinx_packet.header
shared_secret = EXP( hdr.group_element, private_routing_key )
replay_tag = H( shared_secret )
```

<div class="orderedlist">

1.  Derive the various keys required for packet processing.

</div>

``` programlisting
keys = Sphinx_KDF( KDF_INFO, shared_secret )
```

<div class="orderedlist">

1.  Validate the Sphinx Packet Header.

</div>

``` programlisting
derived_mac = MAC( keys.header_mac, hdr.additional_data |
hdr.group_element |
hdr.routing_information )
if !CONSTANT_TIME_CMP( derived_mac, hdr.MAC):
/* MUST abort processing if the header is invalid. */
return ErrorInvalidHeader
```

<div class="orderedlist">

1.  Extract the per-hop routing commands for the current hop.

</div>

``` programlisting
/* Append padding to preserve length-invariance, as the routing
commands for the current hop will be removed. */
padding = ZEROBYTES( PER_HOP_RI_LENGTH )
B = hdr.routing_information | padding

/* Decrypt the entire routing_information block. */
B = B ^ S( keys.header_encryption, keys.header_encryption_iv )
```

<div class="orderedlist">

1.  Parse the per-hop routing commands.

</div>

``` programlisting
cmd_buf = B[:PER_HOP_RI_LENGTH]
new_routing_information = B[PER_HOP_RI_LENGTH:]

next_mix_command_idx = -1
routing_commands = [ ]
for idx = 0; idx < PER_HOP_RI_LENGTH {
/* WARNING: Bounds checking omitted for brevity. */
cmd_type = b[idx]
cmd = NULL
switch cmd_type {
case null: goto done  /* No further commands. */

case next_node_hop:
cmd = RoutingCommand( B[idx:idx+1+LEN( NextNodeHopCommand )] )
next_mix_command_idx = i /* Save for step 7. */
idx += 1 + LEN( NextNodeHopCommand )
break

case recipient:
cmd = RoutingCommand( B[idx:idx+1+LEN( FinalDestinationCommand )] )
idx += 1 + LEN( RecipientCommand )
break

case surb_reply:
cmd = RoutingCommand( B[idx:idx+1+LEN( SURBReplyCommand )] )
idx += 1 + LEN( SURBReplyCommand )
break

default:
/* MUST abort processing on unrecognized commands. */
return ErrorInvalidCommand
}
routing_commands += cmd /* Append cmd to the tail of the list. */
}
done:
```

At the conclusion of the parsing step:

<div class="itemizedlist">

- `routing_commands` - A vector of SphinxRoutingCommand, to be applied at this hop.

- `new_routing_information` - The routing_information block to be sent to the next hop if any.

</div>

<div class="orderedlist">

1.  Decrypt the Sphinx Packet Payload.

</div>

``` programlisting
payload = sphinx_packet.payload
payload = SPRP_Decrypt( key.payload_encryption, payload )
sphinx_packet.payload = payload
```

<div class="orderedlist">

1.  Transform the packet for forwarding to the next mix, if the routing commands vector included a NextNodeHopCommand.

</div>

``` programlisting
if next_mix_command_idx != -1:
cmd = routing_commands[next_mix_command_idx]
hdr.group_element = EXP( hdr.group_element, keys.blinding_factor )
hdr.routing_information = new_routing_information
hdr.mac = cmd.MAC
sphinx_packet.hdr = hdr
```

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="post-sphinx_unwrap-processing"></span>6.2 Post Sphinx_Unwrap Processing

</div>

</div>

</div>

Upon the completion of the `Sphinx_Unwrap` operation, implementations MUST take several additional steps. As the exact behavior is mostly implementation specific, pseudocode will not be provided for most of the post processing steps.

<div class="orderedlist">

1.  Apply replay detection to the packet.

</div>

The `replay_tag` value returned by Sphinx_Unwrap MUST be unique across all packets processed with a given `private_routing_key`.

The exact specifics of how to detect replays is left up to the implementation, however any replays that are detected MUST be discarded immediately.

<div class="orderedlist">

1.  Act on the routing commands, if any.

</div>

The exact specifics of how implementations chose to apply routing commands is deliberately left unspecified, however in general:

<div class="itemizedlist">

- If there is a `NextNodeHopCommand`, the packet should be forwarded to the next node based on the `next_hop` field upon completion of the post processing.

  The lack of a NextNodeHopCommand indicates that the packet is destined for the current node.

- If there is a `SURBReplyCommand`, the packet should be treated as a SURBReply destined for the current node, and decrypted accordingly (See `Section 7.2`)

- If the implementation supports multiple recipients on a single node, the `RecipientCommand` command should be used to determine the correct recipient for the packet, and the payload delivered as appropriate.

  It is possible for both a RecipientCommand and a NextNodeHopCommand to be present simultaneously in the routing commands for a given hop. The behavior when this situation occurs is implementation defined.

</div>

<div class="orderedlist">

1.  Authenticate the packet if required.

</div>

If the packet is destined for the current node, the integrity of the payload MUST be authenticated.

The authentication is done as follows:

``` programlisting
derived_tag = sphinx_packet.payload[:PAYLOAD_TAG_LENGTH]
expected_tag = ZEROBYTES( PAYLOAD_TAG_LENGTH )
if !CONSTANT_TIME_CMP( derived_tag, expected_tag ):
/* Discard the packet with no further processing. */
return ErrorInvalidPayload
```

Remove the authentication tag before presenting the payload to the application.

``` programlisting
sphinx_packet.payload = sphinx_packet.payload[PAYLOAD_TAG_LENGTH:]
```

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="single-use-reply-block-surb-creation"></span>7. Single Use Reply Block (SURB) Creation

</div>

</div>

</div>

A Single Use Reply Block (SURB) is a delivery token with a short lifetime, that can be used by the recipient to reply to the initial sender.

SURBs allow for anonymous replies, when the recipient does not know the sender of the message. Usage of SURBs guarantees anonymity properties but also makes the reply messages indistinguishable from forward messages both to external adversaries as well as the mix nodes.

When a SURB is created, a matching reply block Decryption Token is created, which is used to decrypt the reply message that is produced and delivered via the SURB.

The Sphinx SURB wire encoding is implementation defined, but for the purposes of illustrating creation and use, the following will be used:

``` programlisting
struct {
SphinxHeader sphinx_header;
opaque first_hop[NODE_ID_LENGTH];
opaque payload_key[SPRP_KEY_LENGTH];
} SphinxSURB;
```

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="create-a-sphinx-surb-and-decryption-token"></span>7.1 Create a Sphinx SURB and Decryption Token

</div>

</div>

</div>

Structurally a SURB consists of three parts, a pre-generated Sphinx Packet Header, a node identifier for the first hop to use when using the SURB to reply, and cryptographic keying material by which to encrypt the reply’s payload. All elements must be securely transmitted to the recipient, perhaps as part of a forward Sphinx Packet's Payload, but the exact specifics on how to accomplish this is left up to the implementation.

When creating a SURB, the terminal routing_commands vector SHOULD include a SURBReplyCommand, containing an identifier to ensure that the payload can be decrypted with the correct set of keys (Decryption Token). The routing command is left optional, as it is conceivable that implementations may chose to use trial decryption, and or limit the number of outstanding SURBs to solve this problem.

``` programlisting
Sphinx_Create_SURB( additional_data, first_hop, path[] ) ->
             sphinx_surb,
             decryption_token
```

Inputs:

<div class="itemizedlist">

- `additional_data` The Additional Data that is visible to every node along the path in the header.

- `first_hop` The node id of the first hop the recipient must use when replying via the SURB.

- `path` The vector of PathHop structures in hop order, specifying the node id, public key, and routing commands for each hop.

</div>

Outputs:

<div class="itemizedlist">

- `sphinx_surb` The resulting Sphinx SURB.

- `decryption_token` The Decryption Token associated with the SURB.

</div>

The Sphinx_Create_SURB operation consists of the following steps:

<div class="orderedlist">

1.  Create the Sphinx Packet Header and SPRP key vector.

</div>

``` programlisting
sphinx_header, payload_keys =
Sphinx_Create_Header( additional_data, path )
```

<div class="orderedlist">

1.  Create a key for the final layer of encryption.

</div>

``` programlisting
final_key = RNG( SPRP_KEY_LENGTH )
```

<div class="orderedlist">

1.  Build the SURB and Decryption Token.

</div>

``` programlisting
SphinxSURB sphinx_surb;
sphinx_surb.sphinx_header = sphinx_header
sphinx_surb.first_hop = first_hop
sphinx_surb.payload_key = final_key

decryption_token = final_key + payload_keys /* Prepend */
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="decrypt-a-sphinx-reply-originating-from-a-surb"></span>7.2 Decrypt a Sphinx Reply Originating from a SURB

</div>

</div>

</div>

A Sphinx Reply packet that was generated using a SURB is externally indistinguishable from a forward Sphinx Packet as it traverses the network. However, the recipient of the reply has an additional decryption step, the packet starts off unencrypted, and accumulates layers of Sphinx Packet Payload decryption as it traverses the network.

Determining which decryption token to use when decrypting the SURB reply can be done via the SURBReplyCommand’s id field, if one is included at the time of the SURB’s creation.

``` programlisting
Sphinx_Decrypt_SURB_Reply( decryption_token, payload ) -> message
```

Inputs:

<div class="itemizedlist">

- `decryption_token` The vector of keys allowing a client to decrypt the reply ciphertext payload. This decryption_token is generated when the SURB is created.

- `payload` The Sphinx Packet ciphertext payload.

</div>

Outputs:

<div class="itemizedlist">

- `error` Indicating a unsuccessful unwrap operation if applicable.

- `message` The plaintext message.

</div>

The Sphinx_Decrypt_SURB_Reply operation consists of the following steps:

<div class="orderedlist">

1.  Encrypt the message to reverse the decrypt operations the payload acquired as it traversed the network.

</div>

``` programlisting
for i = LEN( decryption_token ) - 1; i > 0; --i:
payload = SPRP_Encrypt( decryption_token[i], payload )
```

<div class="orderedlist">

1.  Decrypt and authenticate the message ciphertext.

</div>

``` programlisting
message = SPRP_Decrypt( decryption_token[0], payload )

derived_tag = message[:PAYLOAD_TAG_LENGTH]
expected_tag = ZEROBYTES( PAYLOAD_TAG_LENGTH )
if !CONSTANT_TIME_CMP( derived_tag, expected_tag ):
return ErrorInvalidPayload

message = message[PAYLOAD_TAG_LENGTH:]
```

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="single-use-reply-block-replies"></span>8. Single Use Reply Block Replies

</div>

</div>

</div>

The process for using a SURB to reply anonymously is slightly different from the standard packet creation process, as the Sphinx Packet Header is already generated (as part of the SURB), and there is an additional layer of Sphinx Packet Payload encryption that must be performed.

``` programlisting
Sphinx_Create_SURB_Reply( sphinx_surb, payload ) -> sphinx_packet
```

Inputs:

<div class="itemizedlist">

- `sphinx_surb` The SphinxSURB structure, decoded from the implementation defined wire encoding.

- `payload` The packet payload message plaintext.

</div>

The Sphinx_Create_SURB_Reply operation consists of the following steps:

<div class="orderedlist">

1.  Prepend the authentication tag, and append padding to the payload.

</div>

``` programlisting
payload = ZERO_BYTES( PAYLOAD_TAG_LENGTH ) | payload
payload = payload | ZERO_BYTES( PAYLOAD_LENGTH - LEN( payload ) )
```

<div class="orderedlist">

1.  Encrypt the payload.

</div>

``` programlisting
payload = SPRP_Encrypt( sphinx_surb.payload_key, payload )
```

<div class="orderedlist">

1.  Assemble the completed Sphinx Packet.

</div>

``` programlisting
SphinxPacket sphinx_packet
sphinx_packet.header = sphinx_surb.sphinx_header
sphinx_packet.payload = payload
```

The completed `sphinx_packet` MUST be sent to the node specified via `sphinx_surb.node_id`, as the entire reply `sphinx_packet`’s header is pre-generated.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="anonymity-considerations"></span>9. Anonymity Considerations

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="optional-non-constant-length-sphinx-packet-header-padding"></span>9.1 Optional Non-constant Length Sphinx Packet Header Padding

</div>

</div>

</div>

Depending on the mix topology, there is no hard requirement that the per-hop routing info is padded to one fixed constant length.

For example, assuming a layered topology (referred to as stratified topology in the literature) <a href="#MIXTOPO10" class="link">MIXTOPO10</a>, where the layer of any given mix node is public information, as long as the following two invariants are maintained, there is no additional information available to an adversary:

<div class="orderedlist">

1.  All packets entering any given mix node in a certain layer are uniform in length.

2.  All packets leaving any given mix node in a certain layer are uniform in length.

</div>

The only information available to an external or internal observer is the layer of any given mix node (via the packet length), which is information they are assumed to have by default in such a design.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="additional-data-field-considerations"></span>9.2 Additional Data Field Considerations

</div>

</div>

</div>

The Sphinx Packet Construct is crafted such that any given packet is bitwise unlinkable after a Sphinx_Unwrap operation, provided that the optional Additional Data (AD) facility is not used. This property ensures that external passive adversaries are unable to track a packet based on content as it traverses the network. As the on-the-wire AD field is static through the lifetime of a packet (ie: left unaltered by the `Sphinx_Unwrap` operation), implementations and applications that wish to use this facility MUST NOT transmit AD that can be used to distinctly identify individual packets.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="forward-secrecy-considerations"></span>9.3 Forward Secrecy Considerations

</div>

</div>

</div>

Each node acting as a mix MUST regenerate their asymmetric key pair relatively frequently. Upon key rotation the old private key MUST be securely destroyed. As each layer of a Sphinx Packet is encrypted via key material derived from the output of an ephemeral/static Diffie-Hellman key exchange, without the rotation, the construct does not provide Perfect Forward Secrecy. Implementations SHOULD implement defense-in-depth mitigations, for example by using strongly forward-secure link protocols to convey Sphinx Packets between nodes.

This frequent mix routing key rotation can limit SURB usage by directly reducing the lifetime of SURBs. In order to have a strong Forward Secrecy property while maintaining a higher SURB lifetime, designs such as forward secure mixes <a href="#SFMIX03" class="link">SFMIX03</a> could be used.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="compulsion-threat-considerations"></span>9.4 Compulsion Threat Considerations

</div>

</div>

</div>

Reply Blocks (SURBs), forward and reply Sphinx packets are all vulnerable to the compulsion threat, if they are captured by an adversary. The adversary can request iterative decryptions or keys from a series of honest mixes in order to perform a deanonymizing trace of the destination.

While a general solution to this class of attacks is beyond the scope of this document, applications that seek to mitigate or resist compulsion threats could implement the defenses proposed in <a href="#COMPULS05" class="link">COMPULS05</a> via a series of routing command extensions.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="surb-usage-considerations-for-volunteer-operated-mix-networks"></span>9.5 SURB Usage Considerations for Volunteer Operated Mix Networks

</div>

</div>

</div>

Given a hypothetical scenario where Alice and Bob both wish to keep their location on the mix network hidden from the other, and Alice has somehow received a SURB from Bob, Alice MUST not utilize the SURB directly because in the volunteer operated mix network the first hop specified by the SURB could be operated by Bob for the purpose of deanonymizing Alice.

This problem could be solved via the incorporation of a <span class="quote">“<span class="quote">cross-over point</span>”</span> such as that described in <a href="#MIXMINION" class="link">MIXMINION</a>, for example by having Alice delegating the transmission of a SURB Reply to a randomly selected crossover point in the mix network, so that if the first hop in the SURB’s return path is a malicious mix, the only information gained is the identity of the cross-over point.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="security-considerations"></span>10. Security Considerations

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="sphinx-payload-encryption-considerations"></span>10.1 Sphinx Payload Encryption Considerations

</div>

</div>

</div>

The payload encryption’s use of a fragile (non-malleable) SPRP is deliberate and implementations SHOULD NOT substitute it with a primitive that does not provide such a property (such as a stream cipher based PRF). In particular there is a class of correlation attacks (tagging attacks) targeting anonymity systems that involve modification to the ciphertext that are mitigated if alterations to the ciphertext result in unpredictable corruption of the plaintext (avalanche effect).

Additionally, as the PAYLOAD_TAG_LENGTH based tag-then-encrypt payload integrity authentication mechanism is predicated on the use of a non-malleable SPRP, implementations that substitute a different primitive MUST authenticate the payload using a different mechanism.

Alternatively, extending the MAC contained in the Sphinx Packet Header to cover the Sphinx Packet Payload will both defend against tagging attacks and authenticate payload integrity. However, such an extension does not work with the SURB construct presented in this specification, unless the SURB is only used to transmit payload that is known to the creator of the SURB.

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="appendix-a.-references"></span>References

</div>

</div>

</div>

<span id="COMPULS05"></span><span class="bold">**COMPULS05**</span>

Danezis, G., Clulow, J., <span class="quote">“<span class="quote">Compulsion Resistant Anonymous Communications</span>”</span>, Proceedings of Information Hiding Workshop, June 2005, <a href="https://www.freehaven.net/anonbib/cache/ih05-danezisclulow.pdf" class="link" target="_top">https://www.freehaven.net/anonbib/cache/ih05-danezisclulow.pdf</a>.

<span id="MIXMINION"></span><span class="bold">**MIXMINION**</span>

Danezis, G., Dingledine, R., Mathewson, N., <span class="quote">“<span class="quote">Mixminion: Design of a Type III Anonymous Remailer Protocol</span>”</span>, <a href="https://www.mixminion.net/minion-design.pdf" class="link" target="_top">https://www.mixminion.net/minion-design.pdf</a>.

<span id="MIXTOPO10"></span><span class="bold">**MIXTOPO10**</span>

Diaz, C., Murdoch, S., Troncoso, C., <span class="quote">“<span class="quote">Impact of Network Topology on Anonymity and Overhead in Low-Latency Anonymity Networks</span>”</span>, PETS, July 2010, <a href="https://www.esat.kuleuven.be/cosic/publications/article-1230.pdf" class="link" target="_top">https://www.esat.kuleuven.be/cosic/publications/article-1230.pdf</a>.

<span id="RFC2119"></span><span class="bold">**RFC2119**</span>

Bradner, S., <span class="quote">“<span class="quote">Key words for use in RFCs to Indicate Requirement Levels</span>”</span>, BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997, <a href="http://www.rfc-editor.org/info/rfc2119" class="link" target="_top">http://www.rfc-editor.org/info/rfc2119</a>.

<span id="RFC5246"></span><span class="bold">**RFC5246**</span>

Dierks, T. and E. Rescorla, <span class="quote">“<span class="quote">The Transport Layer Security (TLS) Protocol Version 1.2</span>”</span>, RFC 5246, DOI 10.17487/RFC5246, August 2008, <a href="http://www.rfc-editor.org/info/rfc5246" class="link" target="_top">http://www.rfc-editor.org/info/rfc5246</a>.

<span id="SFMIX03"></span><span class="bold">**SFMIX03**</span>

Danezis, G., <span class="quote">“<span class="quote">Forward Secure Mixes</span>”</span>, Proceedings of 7th Nordic Workshop on Secure IT Systems, 2002, <a href="https://www.freehaven.net/anonbib/cache/Dan:SFMix03.pdf" class="link" target="_top">https://www.freehaven.net/anonbib/cache/Dan:SFMix03.pdf</a>.

<span id="SPHINX09"></span><span class="bold">**SPHINX09**</span>

Danezis, G., Goldberg, I., <span class="quote">“<span class="quote">Sphinx: A Compact and Provably Secure Mix Format</span>”</span>, DOI 10.1109/SP.2009.15, May 2009, <a href="https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf" class="link" target="_top">https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf</a>.

</div>

</div>
