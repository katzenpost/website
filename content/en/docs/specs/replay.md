{ "title":"Sphinx packet replay detection" , "linkTitle":"Sphinx packet replay detection" , "description":"" , "author":"" , "url":"" , "date":"2026-05-10T15:27:28.854086985-07:00" , "draft":"false" , "slug":"packet_replay" , "layout":"" , "type":"" , "weight":"1" , "version":"" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="replay"></span>Sphinx packet replay detection

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">David</span> <span class="surname">Stainton</span>

</div>

</div>

</div>

<div>

<div class="abstract">

**Abstract**

This document defines the replay detection for any protocol that uses Sphinx cryptographic packet format. This document is meant to serve as an implementation guide and document the existing replay protect for deployed mix networks.

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="toc">

**Table of Contents**

<span class="section">[Terminology](#terminology)</span>

<span class="section">[Conventions Used in This Document](#d58e95)</span>

<span class="section">[1. Introduction](#sphinx_replay_detection_introduction)</span>

<span class="section">[2. Sphinx Cryptographic Primitives](#sphinx-cryptographic-primitives)</span>

<span class="section">[2.1 Sphinx Parameter Constants](#sphinx-parameter-constants)</span>

<span class="section">[3. System Overview](#system-overview)</span>

<span class="section">[4. Sphinx Packet Replay Cache](#sphinx-packet-replay-cache)</span>

<span class="section">[4.1 Sphinx Replay Tag Composition](#sphinx-replay-tag-composition)</span>

<span class="section">[4.2 Sphinx Replay Tag Caching](#sphinx-replay-tag-caching)</span>

<span class="section">[4.3 Epoch Boundaries](#epoch-boundaries)</span>

<span class="section">[4.4 Cost Of Checking Replays](#cost-of-checking-replays)</span>

<span class="section">[5. Concurrent Processing of Sphinx Packet Replay Tags](#concurrent-processing-of-sphinx-packet-replay-tags)</span>

<span class="section">[5.1 PKI Updates](#pki-updates)</span>

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

<span class="term"><span class="bold">**epoch**</span></span>  
A fixed time interval defined in section 4.2 Sphinx Mix and Provider Key Rotation. The epoch is currently set to 20 minutes. A new PKI document containing public key material is published for each epoch and is valid only for that epoch.

<span class="term"><span class="bold">**packet**</span></span>  
A Sphinx packet, of fixed length for each class of traffic, carrying a message payload and metadata for routing. Packets are routed anonymously through the mixnet and cryptographically transformed at each hop.

<span class="term"><span class="bold">**header**</span></span>  
The packet header consisting of several components, which convey the information necessary to verify packet integrity and correctly process the packet.

<span class="term"><span class="bold">**payload**</span></span>  
The fixed-length portion of a packet containing an encrypted message or part of a message, to be delivered anonymously.

<span class="term"><span class="bold">**group**</span></span>  
A finite set of elements and a binary operation that satisfy the properties of closure, associativity, invertability, and the presence of an identity element.

<span class="term"><span class="bold">**group element**</span></span>  
An individual element of the group.

<span class="term"><span class="bold">**group generator**</span></span>  
A group element capable of generating any other element of the group, via repeated applications of the generator and the group operation.

<span class="term"><span class="bold">**SEDA**</span></span>  
Staged Event Driven Architecture. 1. A highly parallelizable computation model. 2. A computational pipeline composed of multiple stages connected by queues utilizing active queue management algorithms that can evict items from the queue based on dwell time or other criteria where each stage is a thread pool. 3. The only correct way to efficiently implement a software based router on general purpose computing hardware.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="d58e95"></span>Conventions Used in This Document

</div>

</div>

</div>

The key words <span class="quote">“<span class="quote">MUST</span>”</span>, <span class="quote">“<span class="quote">MUST NOT</span>”</span>, <span class="quote">“<span class="quote">REQUIRED</span>”</span>, <span class="quote">“<span class="quote">SHALL</span>”</span>, <span class="quote">“<span class="quote">SHALL NOT</span>”</span>, <span class="quote">“<span class="quote">SHOULD</span>”</span>, <span class="quote">“<span class="quote">SHOULD NOT</span>”</span>, <span class="quote">“<span class="quote">RECOMMENDED</span>”</span>, <span class="quote">“<span class="quote">MAY</span>”</span>, and <span class="quote">“<span class="quote">OPTIONAL</span>”</span> in this document are to be interpreted as described in <a href="#RFC2119" class="link">RFC2119</a>.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="sphinx_replay_detection_introduction"></span>1. Introduction

</div>

</div>

</div>

The Sphinx cryptographic packet format is a compact and provably secure design introduced by George Danezis and Ian Goldberg <a href="#SPHINX09" class="link">SPHINX09</a>. Although it supports replay detection, the exact mechanism of replay detection is neither described in <a href="#SPHINX09" class="link">SPHINX09</a> nor is it described in our <a href="#SPHINXSPEC" class="link">SPHINXSPEC</a>. Therefore we shall describe in detail how to efficiently detect Sphinx packet replay attacks.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="sphinx-cryptographic-primitives"></span>2. Sphinx Cryptographic Primitives

</div>

</div>

</div>

This specification borrows the following cryptographic primitives constants from our <a href="#SPHINXSPEC" class="link">SPHINXSPEC</a>:

<div class="itemizedlist">

- `H(M)` - A cryptographic hash function which takes an byte array M to produce a digest consisting of a `HASH_LENGTH` byte array. `H(M)` MUST be pre-image and collision resistant.

- `EXP(X, Y)` - An exponentiation function which takes the `GROUP_ELEMENT_LENGTH` byte array group elements `X` and `Y`, and returns `X ^^ Y` as a `GROUP_ELEMENT_LENGTH` byte array.

</div>

Let `G` denote the generator of the group, and `EXP_KEYGEN()` return a `GROUP_ELEMENT_LENGTH` byte array group element usable as private key.

The group defined by `G` and `EXP(X, Y)` MUST satisfy the Decision Diffie-Hellman problem.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="sphinx-parameter-constants"></span>2.1 Sphinx Parameter Constants

</div>

</div>

</div>

<div class="itemizedlist">

- `HASH_LENGTH` - 32 bytes. Katzenpost currently uses SHA-512/256. <a href="#RFC6234" class="link">RFC6234</a>

- `GROUP_ELEMENT_LENGTH` - 32 bytes. Katzenpost currently uses X25519. <a href="#RFC7748" class="link">RFC7748</a>

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="system-overview"></span>3. System Overview

</div>

</div>

</div>

Mixes as currently deployed, have two modes of operation:

<div class="orderedlist">

1.  Sphinx routing keys and replay caches are persisted to disk

2.  Sphinx routing keys and replay caches are persisted to memory

</div>

These two modes of operation fundamentally represent a tradeoff between mix server availability and notional compulsion attack resistance. Ultimately it will be the mix operator’s decision to make since they affect the security and availability of their mix servers. In particular since mix networks are vulnerable to the various types of compulsion attacks (see <a href="#SPHINXSPEC" class="link">SPHINXSPEC</a> section 9.4 Compulsion Threat Considerations) and therefore there is some advantage to NOT persisting the Sphinx routing keys to disk. The mix operator can simply poweroff the mix server before seizure rather than physically destroying the disk in order to prevent capture of the Sphinx routing keys. An argument can be made for the use of full disk encryption, however this may not be practical for servers hosted in remote locations.

On the other hand, persisting Sphinx routing keys and replay caches to disk is useful because it allows mix operators to shutdown their mix server for maintenance purposes without loosing these Sphinx routing keys and replay caches. This means that as soon as the maintenance operation is completed the mix server is able to rejoin the network. Our current PKI system <a href="#KATZMIXPKI" class="link">KATZMIXPKI</a> does NOT provide a mechanism to notify Directory Authorities of such an outage or maintenance period. Therefore if there is loss of Sphinx routing keys this results in a mix outage until the next epoch.

The two modes of operation both completely prevent replay attacks after a system restart. In the case of the disk persistence, replay attacks are prevented because all packets traversing the mix have their replay tags persisted to disk cache. This cache is therefore once again used to prevent replays after a system restart. In the case of memory persistence replays are prevented upon restart because the Sphinx routing keys are destroyed and therefore the mix will not participant in the network until at least the next epoch rotation. However availability of the mix may require two epoch rotations because in accordance with <a href="#KATZMIXPKI" class="link">KATZMIXPKI</a> mixes publish future epoch keys so that Sphinx packets flowing through the network can seamlessly straddle the epoch boundaries.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="sphinx-packet-replay-cache"></span>4. Sphinx Packet Replay Cache

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="sphinx-replay-tag-composition"></span>4.1 Sphinx Replay Tag Composition

</div>

</div>

</div>

The following excerpt from our <a href="#SPHINXSPEC" class="link">SPHINXSPEC</a> shows how the replay tag is calculated.

``` programlisting
hdr = sphinx_packet.header
shared_secret = EXP( hdr.group_element, private_routing_key )
replay_tag = H( shared_secret )
```

However this tag is not utilized in replay detection until the rest of the Sphinx packet is fully processed and it’s header MAC verified as described in <a href="#SPHINXSPEC" class="link">SPHINXSPEC</a>.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="sphinx-replay-tag-caching"></span>4.2 Sphinx Replay Tag Caching

</div>

</div>

</div>

It would be sufficient to use a key value store or hashmap to detect the presence of a duplicate replay tag however we additionally employ a bloom filter to increase performance. Sphinx keys must periodically be rotated and destroyed to mitigate compulsion attacks and therefore our replay caches must likewise be rotated. This kind of key erasure scheme limits the window of time that an adversary can perform a compulsion attack. See our PKI specification <a href="#KATZMIXPKI" class="link">KATZMIXPKI</a> for more details regarding epoch key rotation and the grace period before and after the epoch boundary.

We tune our bloom filter for line-speed; that is to say the bloom filter for a given replay cache is tuned for the maximum number of Sphinx packets that can be sent on the wire during the epoch duration of the Sphinx routing key. This of course has to take into account the size of the Sphinx packets as well as the maximum line speed of the network interface. This is a conservative tuning heuristic given that there must be more than this maximum number of Sphinx packets in order for there to be duplicate packets.

Our bloomfilter with hashmap replay detection cache looks like this:

<div class="figure">

<span id="d58e243"></span>

**Figure 1. replay cache**

<div class="figure-contents">

<div class="mediaobject">

![replay cache](../../diagrams/replay1.png)

</div>

</div>

</div>

  

Note that this diagram does NOT express the full complexity of the replay caching system. In particular it does not describe how entries are entered into the bloom filter and hashmap. Upon either bloom filter mismatch or hashmap mismatch both data structures must be locked and the replay tag inserted into each.

For the disk persistence mode of operation the hashmap can simply be replaced with an efficient key value store. Persistent stores may use a write back cache and other techniques for efficiency.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="epoch-boundaries"></span>4.3 Epoch Boundaries

</div>

</div>

</div>

Since mixes publish future epoch keys (see <a href="#KATZMIXPKI" class="link">KATZMIXPKI</a>) so that Sphinx packets flowing through the network can seamlessly straddle the epoch boundaries, our replay detection forms a special kind of double bloom filter system. During the epoch grace period mixes perform trial decryption of Sphinx packets. The replay cache used will be the one that is associated with the Sphinx routing key which was successfully used to decrypt (unwrap transform) the Sphinx packet. This is not a double bloom filter in the normal sense of this term since each bloom filter used is distinct and associated with it’s own cache, furthermore, replay tags are only ever inserted into one cache and one bloom filter.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="cost-of-checking-replays"></span>4.4 Cost Of Checking Replays

</div>

</div>

</div>

The cost of checking a replay tag from a single replay cache is the sum of the following operations:

<div class="orderedlist">

1.  Sphinx packet unwrap operation

2.  A bloom filter lookup

3.  A hashmap or cache lookup

</div>

Therefore these operations are roughly O(1) in complexity. However Sphinx packets processed near epoch boundaries will not be constant time due to trial decryption with two Sphinx routing keys as mentioned above in section <span class="quote">“<span class="quote">3.3 Epoch Boundaries</span>”</span>.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="concurrent-processing-of-sphinx-packet-replay-tags"></span>5. Concurrent Processing of Sphinx Packet Replay Tags

</div>

</div>

</div>

The best way to implement a software based router is with a <a href="#SEDA" class="link">SEDA</a> computational pipeline. We therefore need a mechanism to allow multiple threads to reference our rotating Sphinx keys and associated replay caches. Here we shall describe a shadow memory system which the mix server uses such that the individual worker threads shall always have a reference to the current set of candidate mix keys and associates replay caches.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="pki-updates"></span>5.1 PKI Updates

</div>

</div>

</div>

The mix server periodically updates it’s knowledge of the network by downloading a new consensus document as described in <a href="#KATZMIXPKI" class="link">KATZMIXPKI</a>. The individual threads in the <span class="quote">“<span class="quote">cryptoworker</span>”</span> thread pool which process Sphinx packets make use of a `MixKey` data structure which consists of:

<div class="orderedlist">

1.  Sphinx routing key material (public and private X25519 keys)

2.  Replay Cache

3.  Reference Counter

</div>

Each of these <span class="quote">“<span class="quote">cryptoworker</span>”</span> thread pool has it’s own hashmap associating epochs to a reference to the `MixKey`. The mix server PKI threat maintains a single hashmap which associates the epochs with the corresponding `MixKey`. We shall refer to this hashmap as `MixKeys`. After a new `MixKey` is added to `MixKeys`, a <span class="quote">“<span class="quote">reshadow</span>”</span> operation is performed for each <span class="quote">“<span class="quote">cryptoworker</span>”</span> thread. The <span class="quote">“<span class="quote">reshadow</span>”</span> operation performs two tasks:

<div class="orderedlist">

1.  Removes entries from each <span class="quote">“<span class="quote">cryptoworker</span>”</span> thread's hashmap that are no longer present in `MixKeys` and decrements the `MixKey` reference counter.

2.  Adds entries present in `MixKeys` but are not present in the thread’s hashmap and increments the `MixKey` reference counter.

</div>

Once a given `MixKey` reference counter is decremented to zero, the `MixKey` and it’s associated on disk data is purged. Note that we do not discuss synchronization primitives, however it should be obvious that updating the replay cache should likely make use of a mutex or similar primitive to avoid data races between <span class="quote">“<span class="quote">cryptoworker</span>”</span> threads.

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

<span id="KATZMIXNET"></span><span class="bold">**KATZMIXNET**</span>

Angel, Y., Danezis, G., Diaz, C., Piotrowska, A., Stainton, D., <span class="quote">“<span class="quote">Katzenpost Mix Network Specification</span>”</span>, June 2017, <a href="https://katzenpost.network/docs/specs/pdf/mixnet.pdf" class="link" target="_top">https://katzenpost.network/docs/specs/pdf/mixnet.pdf</a>.

<span id="KATZMIXPKI"></span><span class="bold">**KATZMIXPKI**</span>

Angel, Y., Piotrowska, A., Stainton, D., <span class="quote">“<span class="quote">Katzenpost Mix Network Public Key Infrastructure Specification</span>”</span>, December 2017, <a href="https://katzenpost.network/docs/specs/pdf/pki.pdf" class="link" target="_top">https://katzenpost.network/docs/specs/pdf/pki.pdf</a>.

<span id="RFC2119"></span><span class="bold">**RFC2119**</span>

Bradner, S., <span class="quote">“<span class="quote">Key words for use in RFCs to Indicate Requirement Levels</span>”</span>, BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997, <a href="http://www.rfc-editor.org/info/rfc2119" class="link" target="_top">http://www.rfc-editor.org/info/rfc2119</a>.

<span id="RFC6234"></span><span class="bold">**RFC6234**</span>

Eastlake 3rd, D. and T. Hansen, <span class="quote">“<span class="quote">US Secure Hash Algorithms (SHA and SHA-based HMAC and HKDF)</span>”</span>, RFC 6234, DOI 10.17487/RFC6234, May 2011, <a href="https://www.rfc-editor.org/info/rfc6234" class="link" target="_top">https://www.rfc-editor.org/info/rfc6234</a>.

<span id="RFC7748"></span><span class="bold">**RFC7748**</span>

Langley, A., Hamburg, M., and S. Turner, <span class="quote">“<span class="quote">Elliptic Curves for Security</span>”</span>, RFC 7748, January 2016, <a href="https://www.rfc-editor.org/info/rfc7748" class="link" target="_top">https://www.rfc-editor.org/info/rfc7748</a>.

<span id="SEDA"></span><span class="bold">**SEDA**</span>

Welsh, M., Culler, D., Brewer, E., <span class="quote">“<span class="quote">SEDA: An Architecture for Well-Conditioned, Scalable Internet Services</span>”</span>, 2001, ACM Symposium on Operating Systems Principles, <a href="http://www.sosp.org/2001/papers/welsh.pdf" class="link" target="_top">http://www.sosp.org/2001/papers/welsh.pdf</a>.

<span id="SPHINX09"></span><span class="bold">**SPHINX09**</span>

Danezis, G., Goldberg, I., <span class="quote">“<span class="quote">Sphinx: A Compact and Provably Secure Mix Format</span>”</span>, DOI 10.1109/SP.2009.15, May 2009, <a href="https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf" class="link" target="_top">https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf</a>.

<span id="SPHINXSPEC"></span><span class="bold">**SPHINXSPEC**</span>

Angel, Y., Danezis, G., Diaz, C., Piotrowska, A., Stainton, D., <span class="quote">“<span class="quote">Sphinx Mix Network Cryptographic Packet Format Specification</span>”</span>, July 2017, <a href="https://katzenpost.network/docs/specs/pdf/sphinx.pdf" class="link" target="_top">https://katzenpost.network/docs/specs/pdf/sphinx.pdf</a>.

</div>

</div>
