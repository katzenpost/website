{ "title":"Public key infrastructure" , "linkTitle":"Public key infrastructure" , "description":"" , "author":"" , "url":"" , "date":"2026-05-10T15:27:35.938632833-07:00" , "draft":"false" , "slug":"pki" , "layout":"" , "type":"" , "weight":"1" , "version":"" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="pki"></span>Public key infrastructure

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">Yawning</span> <span class="surname">Angel</span>

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

<div class="author">

### <span class="firstname"></span> <span class="surname">Masala</span>

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

<span class="section">[Terminology](#terminology)</span>

<span class="section">[Conventions used in this document](#conventions-used-in-this-document)</span>

<span class="section">[1. Introduction](#pki_introduction)</span>

<span class="section">[1.2 Security properties overview](#security-properties-overview)</span>

<span class="section">[1.3 Differences from Tor and Mixminion directory authority systems](#differences-from-tor-and-mixminion-directory-authority-systems)</span>

<span class="section">[2. Overview of mix PKI interaction](#overview-of-mix-pki-interaction)</span>

<span class="section">[2.1 PKI protocol schedule](#pki-protocol-schedule)</span>

<span class="section">[2.1.1 Directory authority server schedule](#directory-authority-server-schedule)</span>

<span class="section">[2.1.2 Mix schedule](#mix-schedule)</span>

<span class="section">[3. Voting for consensus protocol](#voting-for-consensus-protocol)</span>

<span class="section">[3.1 Protocol messages](#protocol-messages)</span>

<span class="section">[3.1.1 Mix descriptor and directory signing](#mix-descriptor-and-directory-signing)</span>

<span class="section">[3.2 Vote exchange](#vote-exchange)</span>

<span class="section">[3.3 Reveal exchange](#reveal-exchange)</span>

<span class="section">[3.4 Cert exchange](#cert-exchange)</span>

<span class="section">[3.5 Vote tabulation for consensus computation](#vote-tabulation-for-consensus-computation)</span>

<span class="section">[3.6 Signature collection](#signature-collection)</span>

<span class="section">[3.7 Publication](#publication)</span>

<span class="section">[4. PKI Protocol data structures](#pki-protocol-data-structures)</span>

<span class="section">[4.1 Mix descriptor format](#mix-descriptor-format)</span>

<span class="section">[4.1.1 Scheduling mix downtime](#scheduling-mix-downtime)</span>

<span class="section">[4.2 Directory format](#directory-format)</span>

<span class="section">[4.3 Shared random value structure](#shared-random-value-structure)</span>

<span class="section">[5. PKI wire protocol](#pki-wire-protocol)</span>

<span class="section">[5.1 Mix descriptor publication](#mix-descriptor-publication)</span>

<span class="section">[5.1.1 The post_descriptor command](#the-post_descriptor-command)</span>

<span class="section">[5.1.2 The post_descriptor_status command](#the-post_descriptor_status-command)</span>

<span class="section">[6. Voting](#voting)</span>

<span class="section">[6.1. The vote command](#the-vote-command)</span>

<span class="section">[6.2. The vote_status command](#the-vote_status-command)</span>

<span class="section">[6.3. The get_vote command](#the-get_vote-command)</span>

<span class="section">[7. Retrieval of consensus](#retrieval-of-consensus)</span>

<span class="section">[7.1 The get_consensus command](#the-get_consensus-command)</span>

<span class="section">[7.2 The consensus command](#the-consensus-command)</span>

<span class="section">[7.3. The Cert command](#the-cert-command)</span>

<span class="section">[7.4. The CertStatus command](#the-certstatus-command)</span>

<span class="section">[8. Signature exchange](#signature-exchange)</span>

<span class="section">[8.1. The sig command](#the-sig-command)</span>

<span class="section">[8.2. The sig_status command](#the-sigstatus-command)</span>

<span class="section">[9. Scalability considerations](#scalability-considerations)</span>

<span class="section">[10. Future work](#future-work)</span>

<span class="section">[11. Anonymity considerations](#anonymity-considerations)</span>

<span class="section">[12. Security considerations](#security-considerations)</span>

<span class="section">[Acknowledgements](#acknowledgements)</span>

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

<span class="term"><span class="bold">**PKI**</span></span>  
Public key infrastructure

<span class="term"><span class="bold">**directory authority system**</span></span>  
Refers to specific PKI schemes used by Mixminion and Tor.

<span class="term"><span class="bold">**MSL**</span></span>  
Maximum segment lifetime, currently set to 120 seconds.

<span class="term"><span class="bold">**mix descriptor**</span></span>  
A database record which describes a component mix.

<span class="term"><span class="bold">**family**</span></span>  
Identifier of security domains or entities operating one or more mixes in the network. This is used to inform the path selection algorithm.

<span class="term"><span class="bold">**nickname**</span></span>  
A nickname string that is unique in the consensus document, see Katzenpost Mix Network Specification section 2.2. Network Topology.

<span class="term"><span class="bold">**layer**</span></span>  
The layer indicates which network topology layer a particular mix resides in.

<span class="term"><span class="bold">**provider**</span></span>  
A service operated by a third party that Clients communicate directly with to communicate with the Mixnet. It is responsible for Client authentication, forwarding outgoing messages to the Mixnet, and storing incoming messages for the Client. The Provider MUST have the ability to perform cryptographic operations on the relayed messages.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="conventions-used-in-this-document"></span>Conventions used in this document

</div>

</div>

</div>

The key words <span class="quote">“<span class="quote">MUST</span>”</span>, <span class="quote">“<span class="quote">MUST NOT</span>”</span>, <span class="quote">“<span class="quote">REQUIRED</span>”</span>, <span class="quote">“<span class="quote">SHALL</span>”</span>, <span class="quote">“<span class="quote">SHALL NOT</span>”</span>, <span class="quote">“<span class="quote">SHOULD</span>”</span>, <span class="quote">“<span class="quote">SHOULD NOT</span>”</span>, <span class="quote">“<span class="quote">RECOMMENDED</span>”</span>, <span class="quote">“<span class="quote">MAY</span>”</span>, and <span class="quote">“<span class="quote">OPTIONAL</span>”</span> in this document are to be interpreted as described in <a href="#RFC2119" class="link">RFC2119</a>.

The <span class="quote">“<span class="quote">C</span>”</span> style Presentation Language as described in <a href="#RFC5246" class="link">RFC5246</a> Section 4 is used to represent data structures for additional cryptographic wire protocol commands. <a href="#KATZMIXWIRE" class="link">KATZMIXWIRE</a>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="pki_introduction"></span>1. Introduction

</div>

</div>

</div>

Mixnets are designed with the assumption that a Public Key Infrastructure (PKI) exists and it gives each client the same view of the network. This specification is inspired by the Tor and Mixminion Directory Authority systems <a href="#MIXMINIONDIRAUTH" class="link">MIXMINIONDIRAUTH</a><a href="#TORDIRAUTH" class="link">TORDIRAUTH</a> whose main features are precisely what we need for our PKI. These are decentralized systems meant to be collectively operated by multiple entities.

The mix network directory authority system (PKI) is essentially a cooperative decentralized database and voting system that is used to produce network consensus documents which mix clients periodically retrieve and use for their path selection algorithm when creating Sphinx packets. These network consensus documents are derived from a voting process between the Directory Authority servers.

This design prevents mix clients from using only a partial view of the network for their path selection so as to avoid fingerprinting and bridging attacks <a href="#FINGERPRINTING" class="link">FINGERPRINTING</a>, <a href="#BRIDGING" class="link">BRIDGING</a>, and <a href="#LOCALVIEW" class="link">LOCALVIEW</a>.

The PKI is also used by Authority operators to specify network-wide parameters, for example in the Katzenpost Decryption Mix Network <a href="#KATZMIXNET" class="link">KATZMIXNET</a> the Poisson mix strategy is used and, therefore, all clients must use the same lambda parameter for their exponential distribution function when choosing hop delays in the path selection. The Mix Network Directory Authority system, aka PKI, SHALL be used to distribute such network-wide parameters in the network consensus document that have an impact on security and performance.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="security-properties-overview"></span>1.2 Security properties overview

</div>

</div>

</div>

This Directory Authority system has the following feature goals and security properties:

<div class="itemizedlist">

- All Directory Authority servers must agree with each other on the set of Directory Authorities.

- All Directory Authority servers must agree with each other on the set of mixes.

- This system is intentionally designed to provide identical network consensus documents to each mix client. This mitigates epistemic attacks against the client path selection algorithm such as fingerprinting and bridge attacks <a href="#FINGERPRINTING" class="link">FINGERPRINTING</a><a href="#BRIDGING" class="link">BRIDGING</a>.

- This system is NOT byzantine-fault-tolerant, it instead allows for manual intervention upon consensus fault by the Directory Authority operators. Further, these operators are responsible for expelling bad acting operators from the system.

- This system enforces the network policies such as mix join policy wherein intentionally closed mixnets will prevent arbitrary hosts from joining the network by authenticating all descriptor signatures with a list of allowed public keys.

- The Directory Authority system for a given mix network is essentially the root of all authority.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="differences-from-tor-and-mixminion-directory-authority-systems"></span>1.3 Differences from Tor and Mixminion directory authority systems

</div>

</div>

</div>

In this document we specify a Directory Authority system which is different from that of Tor's and Mixminion’s in a number of ways:

<div class="itemizedlist">

- The list of valid mixes is expressed in an allowlist. For the time being there is no specified <span class="quote">“<span class="quote">bandwidth authority</span>”</span> system which verifies the health of mixes (Further research required in this area).

- There’s no non-directory channel to inform clients that a node is down, so it will end up being a lot of packet loss, since clients will continue to include the missing node in their path selection until keys published by the node expire and it falls out of the consensus.

- The schema of the mix descriptors is different from that used in Mixminion and Tor, including a change which allows our mix descriptor to express <span class="emphasis">*n*</span> Sphinx mix routing public keys in a single mix descriptor whereas in the Tor and Mixminion Directory Authority systems, <span class="emphasis">*n*</span> descriptors are used.

- The serialization format of mix descriptors is different from that used in Mixminion and Tor.

- The shared random number computation is performed every voting round, and is required for a vote to be accepted by each authority. The shared random number is used to deterministically generate the network topology.

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="overview-of-mix-pki-interaction"></span>2. Overview of mix PKI interaction

</div>

</div>

</div>

Each Mix MUST rotate the key pair used for Sphinx packet processing periodically for forward secrecy reasons and to keep the list of seen packet tags short. <a href="#SPHINX09" class="link">SPHINX09</a><a href="#SPHINXSPEC" class="link">SPHINXSPEC</a> The Katzenpost Mix Network uses a fixed interval (`epoch`), so that key rotations happen simultaneously throughout the network, at predictable times.

Each Directory Authority server MUST use some time synchronization protocol in order to correctly use this protocol. This Directory Authority system requires time synchronization to within a few minutes.

Let each epoch be exactly `1200 seconds (20 minutes)` in duration, and the 0th Epoch begin at `2017-06-01 00:00 UTC`.

To facilitate smooth operation of the network and to allow for delays that span across epoch boundaries, Mixes MUST publish keys to the PKI for at least 3 epochs in advance, unless the mix will be otherwise unavailable in the near future due to planned downtime.

At an epoch boundary, messages encrypted to keys from the previous epoch are accepted for a grace period of 2 minutes.

Thus, at any time, keys for all Mixes for the Nth through N + 2nd epoch will be available, allowing for a maximum round trip (forward message + SURB) delay + transit time of 40 minutes. SURB lifetime is limited to a single epoch because of the key rotation epoch, however this shouldn’t present any usability problems since SURBs are only used for sending ACK messages from the destination Provider to the sender.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="pki-protocol-schedule"></span>2.1 PKI protocol schedule

</div>

</div>

</div>

There are two main constraints to Authority schedule:

<div class="orderedlist">

1.  There MUST be enough key material extending into the future so that clients are able to construct Sphinx packets with a forward and reply paths.

2.  All participants should have enough time to participate in the protocol; upload descriptors, vote, generate documents, download documents, establish connections for user traffic.

</div>

The epoch duration of 20 minutes is more than adequate for these two constraints.

<span class="emphasis">*NOTE: perhaps we should make it shorter? but first let’s do some scaling and bandwidth calculations to see how bad it gets…*</span>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="directory-authority-server-schedule"></span>2.1.1 Directory authority server schedule

</div>

</div>

</div>

Directory Authority server interactions are conducted according to the following schedule, where `T` is the beginning of the current epoch, and `P` is the length of the epoch period.

<div class="itemizedlist">

- `T` - Epoch begins

- `T + P/2` - Vote exchange

- `T + (5/8)*P` - Reveal exchange

- `T + (6/8)*P` - Tabulation and signature exchange

- `T + (7/8)*P` - Publish consensus

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="mix-schedule"></span>2.1.2 Mix schedule

</div>

</div>

</div>

Mix PKI interactions are conducted according to the following schedule, where T is the beginning of the current epoch.

`T + P/8` - Deadline for publication of all mixes documents for the next epoch.

`T + (7/8)*P` - This marks the beginning of the period where mixes perform staggered fetches of the PKI consensus document.

`T + (8/9)*P` - Start establishing connections to the new set of relevant mixes in advance of the next epoch.

`T + P - 1MSL` - Start accepting new Sphinx packets encrypted to the next epoch’s keys.

`T + P + 1MSL` - Stop accepting new Sphinx packets encrypted to the previous epoch’s keys, close connections to peers no longer listed in the PKI documents and erase the list of seen packet tags.

Mix layer changes are controlled by the Directory Authorities and therefore a mix can be reassigned to a different layer in our stratified topology at any new epoch. Mixes will maintain incoming and outgoing connections to the various nodes until all mix keys have expired, iff the node is still listed anywhere in the current document.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="voting-for-consensus-protocol"></span>3. Voting for consensus protocol

</div>

</div>

</div>

In our Directory Authority protocol, all the actors conduct their behavior according to a common schedule as outlined in section "2.1 PKI Protocol Schedule". The Directory Authority servers exchange messages to reach consensus about the network. Other tasks they perform include collecting mix descriptor uploads from each mix for each key rotation epoch, voting, shared random number generation, signature exchange and publishing of the network consensus documents.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="protocol-messages"></span>3.1 Protocol messages

</div>

</div>

</div>

There are only two document types in this protocol:

<div class="itemizedlist">

- `mix_descriptor`: A mix descriptor describes a mix.

- `directory`: A directory contains a list of descriptors and other information that describe the mix network.

</div>

Mix descriptor and directory documents MUST be properly signed.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="mix-descriptor-and-directory-signing"></span>3.1.1 Mix descriptor and directory signing

</div>

</div>

</div>

Mixes MUST compose mix descriptors which are signed using their private identity key, an ed25519 key. Directories are signed by one or more Directory Authority servers using their authority key, also an ed25519 key. In all cases, signing is done using JWS <a href="#RFC7515" class="link">RFC7515</a>.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="vote-exchange"></span>3.2 Vote exchange

</div>

</div>

</div>

As described in section <span class="quote">“<span class="quote">2.1 PKI Protocol Schedule</span>”</span>, the Directory Authority servers begin the voting process 1/8 of an epoch period after the start of a new epoch. Each Authority exchanges vote directory messages with each other.

Authorities archive votes from other authorities and make them available for retrieval. Upon receiving a new vote, the authority examines it for new descriptors and includes any valid descriptors in its view of the network.

Each Authority includes in its vote a hashed value committing to a choice of a random number for the vote. See section 4.3 for more details.

<span class="strong">**3.2.1 Voting Wire Protocol Commands**</span>

The Katzenpost Wire Protocol as described in `KATZMIXWIRE` is used by Authorities to exchange votes. We define additional wire protocol commands for sending votes:

``` programlisting
enum {

:   vote(22), vote_status(23),

} Command;
```

The structures of these commands are defined as follows:

``` programlisting
struct {
:   uint64_t epoch_number; opaque public_key[ED25519_KEY_LENGTH];
opaque payload[];

} VoteCommand;

struct {
:   uint8 error_code;

} VoteStatusCommand;
```

<span class="strong">**3.2.2 The vote Command**</span>

The vote command is used to send a PKI document to a peer Authority during the voting period of the PKI schedule.

The payload field contains the signed and serialized PKI document representing the sending Authority’s vote. The public_key field contains the public identity key of the sending Authority which the receiving Authority can use to verify the signature of the payload. The epoch_number field is used by the receiving party to quickly check the epoch for the vote before deserializing the payload.

Each authority MUST include its commit value for the shared random computation in this phase along with its signed vote. This computation is derived from the Tor Shared Random Subsystem, <a href="#TORSRV" class="link">TORSRV</a>.

<span class="strong">**3.2.3 The vote_status Command**</span>

The vote_status command is used to reply to a vote command. The error_code field indicates if there was a failure in the receiving of the PKI document.

``` programlisting
enum {

:   vote_ok(0), /\* None error condition. */ vote_too_early(1), /*
The Authority should try again later. */ vote_too_late(2), /*
This round of voting was missed. \*/
}
```

The epoch_number field of the vote struct is compared with the epoch that is currently being voted on. vote_too_early and vote_too_late are replied back to the voter to report that their vote was not accepted.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="reveal-exchange"></span>3.3 Reveal exchange

</div>

</div>

</div>

As described in section <span class="quote">“<span class="quote">2.1 PKI Protocol Schedule</span>”</span>, the Directory Authority servers exchange the reveal values after they have exchanged votes which contain a commit value. Each Authority exchanges reveal messages with each other.

3.3.1 Reveal Wire Protocol Commands

The Katzenpost Wire Protocol as described in <a href="#KATZMIXWIRE" class="link">KATZMIXWIRE</a> is used by Authorities to exchange reveal values previously committed to in their votes. We define additional wire protocol commands for exchanging reveals:

``` programlisting
enum {
:   reveal(25), reveal_status(26),
} Command;
```

The structures of these commands are defined as follows:

``` programlisting
struct {
:   uint64_t epoch_number; opaque public_key[ED25519_KEY_LENGTH];
opaque payload[];

} RevealCommand;

struct {
:   uint8 error_code;

} RevealStatusCommand;
```

<span class="strong">**3.3.2 The reveal Command**</span>

The reveal command is used to send a reveal value to a peer authority during the reveal period of the PKI schedule.

The payload field contains the signed and serialized reveal value. The public_key field contains the public identity key of the sending Authority which the receiving Authority can use to verify the signature of the payload. The epoch_number field is used by the receiving party to quickly check the epoch for the reveal before deserializing the payload.

<span class="strong">**3.3.3 The reveal_status Command**</span>

The reveal_status command is used to reply to a reveal command. The error_code field indicates if there was a failure in the receiving of the shared random reveal value.

``` programlisting
enum {

:   reveal_ok(8), /* None error condition. */ reveal_too_early(9), 
/* The Authority should try again later. */
reveal_not_authorized(10), /* The Authority was rejected. */
reveal_already_received(11), /* The Authority has already revealed
this round. */ reveal_too_late(12) /* This round of revealing was
missed. */

} Errorcodes;
```

The epoch_number field of the reveal struct is compared with the epoch that is currently being voted on. reveal_too_early and reveal_too_late are replied back to the authority to report their reveal was not accepted. The status code reveal_not_authorized is used if the Authority is rejected. The reveal_already_received is used to report that a valid reveal command was already received for this round.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="cert-exchange"></span>3.4 Cert exchange

</div>

</div>

</div>

The Cert command is the same as a Vote but contains the set of Reveal values as seen by the voting peer. In order to ensure that a misconfigured or malicious Authority operator cannot amplify their ability to influence the threshold voting process, after Reveal messages have been exchanged, Authorities vote again, including the Reveals seen by them. Authorities may not introduce new MixDescriptors at this phase in the protocol.

Otherwise, a consensus partition can be obtained by withholding Reveal values from a threshold number of Peers. In the case of an even-number of Authorities, a denial of service by a single Authority was observed.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="vote-tabulation-for-consensus-computation"></span>3.5 Vote tabulation for consensus computation

</div>

</div>

</div>

The main design constraint of the vote tabulation algorithm is that it MUST be a deterministic process that produces the same result for each directory authority server. This result is known as a network consensus file.

A network consensus file is a well formed directory struct where the `status` field is set to `consensus` and contains 0 or more descriptors, the mix directory is signed by 0 or more directory authority servers. If signed by the full voting group then this is called a fully signed consensus.

<div class="orderedlist">

1.  Validate each vote directory:

</div>

<div class="itemizedlist">

- that the liveness fields correspond to the following epoch

- status is `vote`

- version number matches ours

</div>

<div class="orderedlist">

1.  Compute a consensus directory:

</div>

Here we include a modified section from the Mixminion PKI spec <a href="#MIXMINIONDIRAUTH" class="link">MIXMINIONDIRAUTH</a>:

For each distinct mix identity in any vote directory:

<div class="itemizedlist">

- If there are multiple nicknames for a given identity, do not include any descriptors for that identity.

- If half or fewer of the votes include the identity, do not include any descriptors for the identity. <span class="emphasis">*This also guarantees that there will be only one identity per nickname.*</span>

- If we are including the identity, then for each distinct descriptor that appears in any vote directory:

  <div class="itemizedlist">

  - Do not include the descriptor if it will have expired on the date the directory will be published.

  - Do not include the descriptor if it is superseded by other descriptors for this identity.

  - Do not include the descriptor if it not valid in the next epoch.

  - Otherwise, include the descriptor.

  </div>

- Sort the list of descriptors by the signature field so that creation of the consensus is reproducible.

- Set directory `status` field to `consensus`.

</div>

<div class="orderedlist">

1.  Compute a shared random number from the values revealed in the <span class="quote">“<span class="quote">Reveal</span>”</span> step. Authorities whose reveal value does not verify their commit value MUST be excluded from the consensus round. Authorities ensure that their peers MUST participate in Commit-and-Reveal, and MUST use correct Reveal values obtained from other Peers as part of the <span class="quote">“<span class="quote">Cert</span>”</span> exchange.

2.  Generate or update the network topology using the shared random number as a seed to a deterministic random number generator that determines the order that new mixes are placed into the topology.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="signature-collection"></span>3.6 Signature collection

</div>

</div>

</div>

Each Authority signs their view of consensus, and exchanges detached Signatures with each other. Upon receiving each Signature it is added to the signatures on the Consensus if it validates the Consensus. The Authority SHOULD warn the administrator if network partition is detected.

If there is disagreement about the consensus directory, each authority collects signatures from only the servers which it agrees with about the final consensus.

// TODO: consider exchanging peers votes amongst authorities (or hashes thereof) to // ensure that an authority has distributed one and only unique vote amongst its peers.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="publication"></span>3.7 Publication

</div>

</div>

</div>

If the consensus is signed by a majority of members of the voting group then it's a valid consensus and it is published.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="pki-protocol-data-structures"></span>4. PKI Protocol data structures

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="mix-descriptor-format"></span>4.1 Mix descriptor format

</div>

</div>

</div>

Note that there is no signature field. This is because mix descriptors are serialized and signed using JWS. The `IdentityKey` field is a public ed25519 key. The `MixKeys` field is a map from epoch to public X25519 keys which is what the Sphinx packet format uses.

<div class="note" style="margin-left: 0.5in; margin-right: 0.5in;">

<table data-border="0" data-summary="Note: Note">
<tbody>
<tr class="odd">
<td rowspan="2" style="text-align: center;" data-valign="top" width="25"><img src="file:/home/usr/local/Oxygen_XML_Editor_28/frameworks/docbook/css/img/note.png" alt="[Note]" /></td>
<td style="text-align: left;">Note</td>
</tr>
<tr class="even">
<td style="text-align: left;" data-valign="top"><p>XXX David: replace the following example with a JWS example:</p></td>
</tr>
</tbody>
</table>

</div>

``` programlisting
{
"Version": 0,
"Name": "",
"Family": "",
"Email": "",
"AltContactInfo":"",
"IdentityKey": "",
"LinkKey":"",
"MixKeys": {
"Epoch": "EpochPubKey",
},
"Addresses": ["IP:Port"],
"Layer": 0,
"LoadWeight":0,
"AuthenticationType":""
}
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="scheduling-mix-downtime"></span>4.1.1 Scheduling mix downtime

</div>

</div>

</div>

Mix operators can publish a half empty mix descriptor for future epochs to schedule downtime. The mix descriptor fields that MUST be populated are:

<div class="itemizedlist">

- Version

- Name

- Family

- Email

- Layer

- IdentityKey

- MixKeys

</div>

The map in the field called "MixKeys" should reflect the scheduled downtime for one or more epochs by not have those epochs as keys in the map.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="directory-format"></span>4.2 Directory format

</div>

</div>

</div>

<span class="emphasis">*Note: replace the following example with a JWS example*</span>

``` programlisting
{
"Signatures": [],
"Version": 0,
"Status": "vote",
"Lambda" : 0.274,
"MaxDelay" : 30,
"Topology" : [],
"Providers" : [],
}
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="shared-random-value-structure"></span>4.3 Shared random value structure

</div>

</div>

</div>

Katzenpost’s Shared Random Value computation is inspired by Tor’s Shared Random Subsystem <a href="#TORSRV" class="link">TORSRV</a>.

Each voting round a commit value is included in the votes sent to other authorities. These are produced as follows:

``` programlisting
H = blake2b-256

COMMIT = Uint64(epoch) | H(REVEAL) REVEAL = Uint64(epoch) | H(RN)
```

After the votes are collected from the voting round, and before signature exchange, the Shared Random Value field of the consensus document is the output of H over the input string calculated as follows:

<div class="orderedlist">

1.  Validated Reveal commands received including the authorities own reveal are sorted by reveal value in ascending order and appended to the input in format IdentityPublicKeyBytes_n | RevealValue_n

</div>

However instead of the Identity Public Key bytes we instead encode the Reveal with the blake2b 256 bit hash of the public key bytes.

<div class="orderedlist">

1.  If a SharedRandomValue for the previous epoch exists, it is appended to the input string, otherwise 32 NUL (x00) bytes are used.

</div>

``` programlisting
REVEALS = ID_a \| R_a \| ID_b \| R_b \| \... SharedRandomValue =
H("shared-random" | Uint64(epoch) | REVEALS | PREVIOUS_SRV)
```

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="pki-wire-protocol"></span>5. PKI wire protocol

</div>

</div>

</div>

The Katzenpost Wire Protocol as described in <a href="#KATZMIXWIRE" class="link">KATZMIXWIRE</a> is used by both clients and by Directory Authority peers. In the following section we describe additional wire protocol commands for publishing mix descriptors, voting and consensus retrieval.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="mix-descriptor-publication"></span>5.1 Mix descriptor publication

</div>

</div>

</div>

The following commands are used for publishing mix descriptors and setting mix descriptor status:

``` programlisting
enum {
/* Extending the wire protocol Commands. */
post_descriptor(20),
post_descriptor_status(21),
}
```

The structures of these command are defined as follows:

``` programlisting
struct {
uint64_t epoch_number;
opaque payload[];
} PostDescriptor;

struct {
uint8 error_code;
} PostDescriptorStatus;
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-post_descriptor-command"></span>5.1.1 The post_descriptor command

</div>

</div>

</div>

The post_descriptor command allows mixes to publish their descriptors.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-post_descriptor_status-command"></span>5.1.2 The post_descriptor_status command

</div>

</div>

</div>

The post_descriptor_status command is sent in response to a post_descriptor command, and uses the following error codes:

``` programlisting
enum {
descriptor_ok(0),
descriptor_invalid(1),
descriptor_conflict(2),
descriptor_forbidden(3),
} ErrorCodes;
```

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="voting"></span>6. Voting

</div>

</div>

</div>

The following commands are used by Authorities to exchange votes:

``` programlisting
enum {
vote(22),
vote_status(23),
get_vote(24),
} Command;
```

The structures of these commands are defined as follows:

``` programlisting
struct {
uint64_t epoch_number;
opaque public_key[ED25519_KEY_LENGTH];
opaque payload[];
} VoteCommand;

struct {
uint8 error_code;
} VoteStatusCommand;
```

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-vote-command"></span>6.1. The vote command

</div>

</div>

</div>

The `vote` command is used to send a PKI document to a peer Authority during the voting period of the PKI schedule.

The payload field contains the signed and serialized PKI document representing the sending Authority’s vote. The public_key field contains the public identity key of the sending Authority which the receiving Authority can use to verify the signature of the payload. The epoch_number field is used by the receiving party to quickly check the epoch for the vote before deserializing the payload.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-vote_status-command"></span>6.2. The vote_status command

</div>

</div>

</div>

The `vote_status` command is used to reply to a vote command. The error_code field indicates if there was a failure in the receiving of the PKI document.

``` programlisting
enum {
vote_ok(0),               /* None error condition. */
vote_too_early(1),        /* The Authority should try again later. */
vote_too_late(2),         /* This round of voting was missed. */
vote_not_authorized(3),   /* The voter's key is not authorized. */
vote_not_signed(4),       /* The vote signature verification failed */
vote_malformed(5),        /* The vote payload was invalid */
vote_already_received(6), /* The vote was already received */
vote_not_found(7),        /* The vote was not found */
}
```

The epoch_number field of the vote struct is compared with the epoch that is currently being voted on. vote_too_early and vote_too_late are replied back to the voter to report that their vote was not accepted.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-get_vote-command"></span>6.3. The get_vote command

</div>

</div>

</div>

The `get_vote` command is used to request a PKI document (vote) from a peer Authority. The epoch field contains the epoch from which to request the vote, and the public_key field contains the public identity key of the Authority of the requested vote. A successful query is responded to with a vote command, and queries that fail are responded to with a vote_status command with error_code vote_not_found(7).

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="retrieval-of-consensus"></span>7. Retrieval of consensus

</div>

</div>

</div>

Providers in the Katzenpost mix network system <a href="#KATZMIXNET" class="link">KATZMIXNET</a> may cache validated network consensus files and serve them to clients over the mix network's link layer wire protocol <a href="#KATZMIXWIRE" class="link">KATZMIXWIRE</a>. We define additional wire protocol commands for requesting and sending PKI consensus documents:

``` programlisting
enum {
/* Extending the wire protocol Commands. */
get_consensus(18),
consensus(19),
} Command;

The structures of these commands are defined as follows:
```

``` programlisting
struct {
uint64_t epoch_number;
} GetConsensusCommand;

struct {
uint8 error_code;
opaque payload[];
} ConsensusCommand;
```

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-get_consensus-command"></span>7.1 The get_consensus command

</div>

</div>

</div>

The get_consensus command is a command that is used to retrieve a recent consensus document. If a given get_consensus command contains an Epoch value that is either too big or too small then a reply consensus command is sent with an empty payload. Otherwise if the consensus request is valid then a consensus command containing a recent consensus document is sent in reply.

Initiators MUST terminate the session immediately upon reception of a get_consensus command.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-consensus-command"></span>7.2 The consensus command

</div>

</div>

</div>

The consensus command is a command that is used to send a recent consensus document. The error_code field indicates if there was a failure in retrieval of the PKI consensus document.

``` programlisting
enum {
consensus_ok(0),        /* None error condition and SHOULD be accompanied with
a valid consensus payload. */
consensus_not_found(1), /* The client should try again later. */
consensus_gone(2),      /* The consensus will not be available in the future. */
} ErrorCodes;
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-cert-command"></span>7.3. The Cert command

</div>

</div>

</div>

The `cert` command is used to send a PKI document to a peer Authority during the voting period of the PKI schedule. It is the same as the `vote` command, but must contain the set of SharedRandomCommit and SharedRandomReveal values as seen by the Authority during the voting process.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-certstatus-command"></span>7.4. The CertStatus command

</div>

</div>

</div>

The `cert_status` command is the response to a `cert` command, and is the same as a `vote_status` response, other than the command identifier. Responses are CertOK, CertTooEarly, CertNotAuthorized, CertNotSigned, CertAlreadyReceived, CertTooLate

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="signature-exchange"></span>8. Signature exchange

</div>

</div>

</div>

Signatures exchange is the final round of the consensus protocol and consists of the Sig and SigStatus commands.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-sig-command"></span>8.1. The sig command

</div>

</div>

</div>

The `sig` command contains a detached Signature from PublicKey of Consensus for Epoch.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="the-sigstatus-command"></span>8.2. The sig_status command

</div>

</div>

</div>

The `sig_status` command is the response to a `sig` command. Responses are SigOK, SigNotAuthorized, SigNotSigned, SigTooEarly, SigTooLate, SigAlreadyReceived, and SigInvalid.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="scalability-considerations"></span>9. Scalability considerations

</div>

</div>

</div>

<span class="emphasis">*TODO: notes on scaling, bandwidth usage etc.*</span>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="future-work"></span>10. Future work

</div>

</div>

</div>

<div class="itemizedlist">

- byzantine fault tolerance

- PQ crypto signatures for all PKI documents: mix descriptors and directories. <a href="#SPHINCS256" class="link">SPHINCS256</a> could be used, we already have a golang implementation: https://github.com/Yawning/sphincs256/

- Make a Bandwidth Authority system to measure health of the network. Also perform load balancing as described in <a href="#PEERFLOW" class="link">PEERFLOW</a>?

- Implement byzantine attack defenses as described in <a href="#MIRANDA" class="link">MIRANDA</a> and <a href="#MIXRELIABLE" class="link">MIXRELIABLE</a> where mix link performance proofs are recorded and used in a reputation system.

- Choose a different serialization/schema language?

- Use a append only merkle tree instead of this voting protocol.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="anonymity-considerations"></span>11. Anonymity considerations

</div>

</div>

</div>

<div class="itemizedlist">

- This system is intentionally designed to provide identical network consensus documents to each mix client. This mitigates epistemic attacks against the client path selection algorithm such as fingerprinting and bridge attacks <a href="#FINGERPRINTING" class="link">FINGERPRINTING</a>, <a href="#BRIDGING" class="link">BRIDGING</a>.

- If consensus has failed and thus there is more than one consensus file, clients MUST NOT use this compromised consensus and refuse to run.

- We try to avoid randomizing the topology because doing so splits the anonymity sets on each mix into two. That is, packets belonging to the previous topology versus the current topology are trivially distinguishable. On the other hand if enough mixes fall out of consensus eventually the mixnet will need to be rebalanced to avoid an attacker compromised path selection. One example of this would be the case where the adversary controls the only mix is one layer of the network topology.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="security-considerations"></span>12. Security considerations

</div>

</div>

</div>

<div class="itemizedlist">

- The Directory Authority / PKI system for a given mix network is essentially the root of all authority in the system. The PKI controls the contents of the network consensus documents that mix clients download and use to inform their path selection. Therefore if the PKI as a whole becomes compromised then so will the rest of the system in terms of providing the main security properties described as traffic analysis resistance. Therefore a decentralized voting protocol is used so that the system is more resilient when attacked, in accordance with the principle of least authority. <a href="#SECNOTSEP" class="link">SECNOTSEP</a>

- Short epoch durations make it is more practical to make corrections to network state using the PKI voting rounds.

- Fewer epoch keys published in advance is a more conservative security policy because it implies reduced exposure to key compromise attacks.

- A bad acting Directory Authority who lies on each vote and votes inconsistently can trivially cause a denial of service for each voting round.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="acknowledgements"></span>Acknowledgements

</div>

</div>

</div>

We would like to thank Nick Mathewson for answering design questions and thorough design review.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="appendix-a.-references"></span>References

</div>

</div>

</div>

<span id="BRIDGING"></span><span class="bold">**BRIDGING**</span>

Danezis, G., Syverson, P., <span class="quote">“<span class="quote">Bridging and Fingerprinting: Epistemic Attacks on Route Selection</span>”</span>, Proceedings of PETS 2008, Leuven, Belgium, July 2008, <a href="https://www.freehaven.net/anonbib/cache/danezis-pet2008.pdf" class="link" target="_top">https://www.freehaven.net/anonbib/cache/danezis-pet2008.pdf</a>.

<span id="FINGERPRINTING"></span><span class="bold">**FINGERPRINTING**</span>

Danezis, G., Clayton, R., <span class="quote">“<span class="quote">Route Finger printing in Anonymous Communications</span>”</span>, <a href="https://www.cl.cam.ac.uk/~rnc1/anonroute.pdf" class="link" target="_top">https://www.cl.cam.ac.uk/~rnc1/anonroute.pdf</a>.

<span id="KATZMIXNET"></span><span class="bold">**KATZMIXNET**</span>

Angel, Y., Danezis, G., Diaz, C., Piotrowska, A., Stainton, D., <span class="quote">“<span class="quote">Katzenpost Mix Network Specification</span>”</span>, June 2017, <a href="https://katzenpost.network/docs/specs/pdf/mixnet.pdf" class="link" target="_top">https://katzenpost.network/docs/specs/pdf/mixnet.pdf</a>.

<span id="KATZMIXWIRE"></span><span class="bold">**KATZMIXWIRE**</span>

Angel, Y., <span class="quote">“<span class="quote">Katzenpost Mix Network Wire Protocol Specification</span>”</span>, June 2017, <a href="https://katzenpost.network/docs/specs/pdf/wire.pdf" class="link" target="_top">https://katzenpost.network/docs/specs/pdf/wire.pdf</a>.

<span id="LOCALVIEW"></span><span class="bold">**LOCALVIEW**</span>

Gogolewski, M., Klonowski, M., Kutylowsky, M., <span class="quote">“<span class="quote">Local View Attack on Anonymous Communication</span>”</span>, <a href="https://cs.pwr.edu.pl/kutylowski/articles/LocalView-WWW.pdf" class="link" target="_top">https://cs.pwr.edu.pl/kutylowski/articles/LocalView-WWW.pdf</a>.

<span id="MIRANDA"></span><span class="bold">**MIRANDA**</span>

Leibowitz, H., Piotrowska, A., Danezis, G., Herzberg, A., <span class="quote">“<span class="quote">No right to remain silent: Isolating Malicious Mixes</span>”</span>, 2017, <a href="https://eprint.iacr.org/2017/1000.pdf" class="link" target="_top">https://eprint.iacr.org/2017/1000.pdf</a>.

<span id="MIXMINIONDIRAUTH"></span><span class="bold">**MIXMINIONDIRAUTH**</span>

Danezis, G., Dingledine, R., Mathewson, N., <span class="quote">“<span class="quote">Type III (Mixminion) Mix Directory Specification</span>”</span>, December 2005, <a href="https://www.mixminion.net/dir-spec.txt" class="link" target="_top">https://www.mixminion.net/dir-spec.txt</a>.

<span id="MIXRELIABLE"></span><span class="bold">**MIXRELIABLE**</span>

Dingledine, R., Freedman, M., Hopwood, D., Molnar, D., <span class="quote">“<span class="quote">A Reputation System to Increase MIX-Net Reliability</span>”</span>, 2001, Information Hiding, 4th International Workshop, <a href="https://www.freehaven.net/anonbib/cache/mix-acc.pdf" class="link" target="_top">https://www.freehaven.net/anonbib/cache/mix-acc.pdf</a>.

<span id="PEERFLOW"></span><span class="bold">**PEERFLOW**</span>

Johnson, A., Jansen, R., Segal, A., Syverson, P., <span class="quote">“<span class="quote">PeerFlow: Secure Load Balancing in Tor</span>”</span>, July 2017, Proceedings on Privacy Enhancing Technologies, <a href="https://petsymposium.org/2017/papers/issue2/paper12-2017-2-source.pdf" class="link" target="_top">https://petsymposium.org/2017/papers/issue2/paper12-2017-2-source.pdf</a>.

<span id="RFC2119"></span><span class="bold">**RFC2119**</span>

Bradner, S., <span class="quote">“<span class="quote">Key words for use in RFCs to Indicate Requirement Levels</span>”</span>, BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997, <a href="http://www.rfc-editor.org/info/rfc2119" class="link" target="_top">http://www.rfc-editor.org/info/rfc2119</a>.

<span id="RFC5246"></span><span class="bold">**RFC5246**</span>

Dierks, T. and E. Rescorla, <span class="quote">“<span class="quote">The Transport Layer Security (TLS) Protocol Version 1.2</span>”</span>, RFC 5246, DOI 10.17487/RFC5246, August 2008, <a href="http://www.rfc-editor.org/info/rfc5246" class="link" target="_top">http://www.rfc-editor.org/info/rfc5246</a>.

<span id="RFC7515"></span><span class="bold">**RFC7515**</span>

Jones, M., Bradley, J., Sakimura, N., <span class="quote">“<span class="quote">JSON Web Signature (JWS)</span>”</span>, May 2015, <a href="https://www.rfc-editor.org/info/rfc7515" class="link" target="_top">https://www.rfc-editor.org/info/rfc7515</a>.

<span id="SECNOTSEP"></span><span class="bold">**SECNOTSEP**</span>

Miller, M., Tulloh, B., Shapiro, J., <span class="quote">“<span class="quote">The Structure of Authority: Why Security Is not a Separable Concer</span>”</span>, <a href="http://www.erights.org/talks/no-sep/secnotsep.pdf" class="link" target="_top">http://www.erights.org/talks/no-sep/secnotsep.pdf</a>.

<span id="SPHINCS256"></span><span class="bold">**SPHINCS256**</span>

Bernstein, D., Hopwood, D., Hulsing, A., Lange, T., Niederhagen, R., Papachristodoulou, L., Schwabe, P., Wilcox O'Hearn, Z., <span class="quote">“<span class="quote">SPHINCS: practical stateless hash-based signatures</span>”</span>, <a href="http://sphincs.cr.yp.to/sphincs-20141001.pdf" class="link" target="_top">http://sphincs.cr.yp.to/sphincs-20141001.pdf</a>.

<span id="SPHINX09"></span><span class="bold">**SPHINX09**</span>

Danezis, G., Goldberg, I., <span class="quote">“<span class="quote">Sphinx: A Compact and Provably Secure Mix Format</span>”</span>, DOI 10.1109/SP.2009.15, May 2009, <a href="https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf" class="link" target="_top">https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf</a>.

<span id="SPHINXSPEC"></span><span class="bold">**SPHINXSPEC**</span>

Angel, Y., Danezis, G., Diaz, C., Piotrowska, A., Stainton, D., <span class="quote">“<span class="quote">Sphinx Mix Network Cryptographic Packet Format Specification</span>”</span>, July 2017, <a href="https://katzenpost.network/docs/specs/pdf/sphinx.pdf" class="link" target="_top">https://katzenpost.network/docs/specs/pdf/sphinx.pdf</a>.

<span id="TORDIRAUTH"></span><span class="bold">**TORDIRAUTH**</span>

<span class="quote">“<span class="quote">Tor directory protocol, version 3</span>”</span>, <a href="https://spec.torproject.org/dir-spec/index.html" class="link" target="_top">https://spec.torproject.org/dir-spec/index.html</a>.

<span id="TORSRV"></span><span class="bold">**TORSRV**</span>

<span class="quote">“<span class="quote">Tor Shared Random Subsystem Specification</span>”</span>, <a href="https://spec.torproject.org/srv-spec/index.html" class="link" target="_top">https://spec.torproject.org/srv-spec/index.html</a>.

</div>

</div>
