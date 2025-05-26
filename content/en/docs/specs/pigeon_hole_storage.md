---
title: "Pigeonhole Design Specification"
linkTitle: "Pigeonhole Design Specification"
url: "docs/specs/pigeonhole.html"
description: ""
categories: [""]
tags: [""]
author: ["Threebit Hacker", "David Stainton"]
version: 0
draft: false
---

# Abstract

This is the specification of the Pigeonhole protocol.

Here we define the client behavior and describe how it sends and
receives BACAP streams and individual messages as well as the
AllOrNothing streams. All of this interaction of the client is
mediated through the courier services who interact with the storage
replicas.


# Introduction

Definition of BACAP: "Echomix: a Strong Anonymity System with
Messaging" chapter 4:
    https://arxiv.org/abs/2501.02933

This specification describes an instantiation of the protocol briefly
described in "5.6. End-to-end reliable group channels" in that paper.

Implementation of core primitives:
    https://github.com/katzenpost/hpqc/blob/main/bacap/bacap.go


# Glossary

* (BACAP?) Box: Box has a Box ID (which is also public key), Signature
  and Ciphertext Signed Payload

* Courier: a service that runs on the service nodes and interacts with
  storage replicas. Proxies requests from clients and routes replies
  back to clients (via SURBs).

* Storage replica: The actual storage nodes where message ciphertexts
  are stored and retrieved.

* Intermediate replica. See [5.4.1. Writing messages] """These
  intermediate replicas are chosen independently of the two final
  replicas for that box ID which are derived using the sharding
  scheme. The reason Alice designates intermediate replicas, as
  opposed to addressing the final replicas directly, os as to avoid
  revealing to the courier which shard the box falls into."""



# Protocol parameters
* The maximum size of BACAP messages in Katzenpost is:
    
    SphinxGeometry's UserForwardPayloadLength - CBOR overhead = Max BACAP Payload
    
        // TODO: This is a rough estimate, we need to additionally account for
        // TODO: courier commands (overhead where the client is telling the
        // courier what to do; "go read from this BACAP stream" etc)
    BACAP_PAYLOAD_SIZE (c_i^{ctx}) = UserForwardPayloadLength - COURIER_ENVELOPE_SIZE
    COURIER_ENVELOPE_SIZE = 32 + CTIDH1024PKSIZE + 2*(32+1) + REPLICA_ENVELOPE_SIZE
    REPLICA_ENVELOPE_SIZE = 32 + CTIDH1024PKSIZE + 32 + BACAP PAYLOAD SIZE 32 + 64
    CTIDH1024PKSIZE = ??? is this just 128 bytes ???

    Appendix II: courier envelopes (the courier sees, coming in via SPHINX) 
        1) The sender’s ephemeral hybrid public key:
           a) 32 bytes: x25519 public key
           b) CTIDH-1024 public key
        2) for each designated replica:
           32 bytes: envelope DEK encrypted with shared secret between sender private key and replica public key 
        3) 1 byte: replica/shard id designating each replica to contact
        4) ReplicaEnvelope: 32 + CTIDH1024PKSIZE + 32 + BACAP PAYLOAD SIZE 32 + 64
    
    Appendix III replica envelopes (that the storage replicas see):
        1) sender’s ephemeral public key
           a) 32 bytes: x25519 public key
           b) CTIDH-1024 public key
        2) 32 bytes: 256-bit DEK encrypted to the replica’s public key
        3) enveloped message, encrypted with DEK, containing a BACAP message:
            a) 32 bytes: BACAP box ID (M ctx i )
            b) BACAP payload (c ctx i )
            c) 64 bytes: BACAP signature (s ctx i )


# Protocol Messages

```golang

// This is sent from the Client to its Courier.
// This is used when the Client is trying to either read or write a single BACAP box.
type CourierEnvelope struct {

    // IntermediateReplicas are used to initially send the message to, and eventually
    // the message gets replicated to the correct locations. This hides the correct 
    // locations from the courier.
    IntermediateReplicas      [2]uint8

    // DEK is used for each replica: ReplicaMessage.DEK
    DEK           [2]*[32]byte

    // ReplyIndex is described:

    //  The client will be resending its thing to the courier until it receives

     // a reply. The courier is responsible for NOT sending each of those resent

    // messages to the replicas. It can use the EnvelopeHash to deduplicate.

    // When the client sends a CourierEnvelope that the courier has already got

    // ReplicaMessageReply's for, the courier needs to respond with one of those.

    // ReplyIndex will let the client choose which one. I guess it could be a bool.

    ReplyIndex uint8 


// these two fields below get hashed to form the EnvelopeHash later used
// in ReplicaMessageReply:

    // SenderEPubKey 
    SenderEPubKey []byte   // x25519 + ctidh1024 NIKE key of the client

    // Ciphertext is encrypted and MAC'ed
    Ciphertext    []byte // ReplicaMessage.Ciphertext
}

// ReplicaMessage used over wire protocol from couriers to replicas,
// one replica at a time.
type ReplicaMessage struct {
    Cmds   *Commands
    Geo    *geo.Geometry
    Scheme nike.Scheme

    SenderEPubKey []byte
    DEK           *[32]byte // copied from CourierEnvelope.DEK by the courier
    
    // Ciphertext decrypts to a ReplicaWrite or a ReplicaRead
    Ciphertext    []byte    // copied from CourierEnvelope.Ciphertext
}
```

CourierEnvelope specifies intermediate replica IDs and NOT the final
destination replica IDs. The courier service writes to the specified
IDs and the storage node replication will take care of writing it to
the correct storage node and Box ID.

CourierEnvelope type is used to save bandwidth. It is sent by clients
to the courier services. The courier service then transforms one
CourierEnvelope into two ReplicaMessage types, one for each
destination replica. The courier then forwards those two
ReplicaMessage's to their respective replicas.

The courier expects an asynchronous ReplicaMessageReply in response from each replica:

```golang
// ReplicaMessageReply is sent by replicas to couriers as a reply
// to the ReplicaMessage command.
type ReplicaMessageReply struct {
    Cmds *Commands

    ErrorCode     uint8
    EnvelopeHash  *[32]byte
    EnvelopeReply []byte    // TODO we haven't defined this
}
```


The courier MUST keep track of EnvelopeHash'es of ALL ReplicaMessage's
which it sends to the replicas. AND it must link each of these hashes
to a client SURB so that it can send a reply.



For each EnvelopeHash it needs to remember:

```golang
// for each EnvelopeHash, the courier keeps a map from EnvelopeHash to CourierBookKeeping
type CourierBookKeeping struct {
    SURB [2]*[]byte // maybe we only need one

    SURBTimestamps [2]*time.Time // when we received SURB[i], so we can delete it when it's too old

    EnvelopeReplies [2]*ReplicaMessageReply // from replicas to courier, eventually sent to client
}
```
The Courier sends to the client:
```golang
type CourierEnvelopeReply struct {
    EnvelopeHash EnvelopeHash // the envelopehash this reply corresponds to


    // ReplyIndex is a copy of the CourierEnvelope.ReplyIndex field from the
    // CourierEnvelope that this CourierEnvelopeREply corresponds to
    ReplyIndex uint8

    Payload ReplicaMessageReply
}
```

* Clients ask for the reply from Replica either number 1 or number 2
  in each message to the courier (ReplyIndex).
* The courier replies with the corresponding reply if it has that
  reply.
* If it doesn't have the reply, but it does have the other reply, it
  sends the ReplicaMessageReply that it *does* have to the client.
* It always indicates to the client *which* replica's reply it sent (1
  or 2).
* If the client doesnt receive an answer with a MessageReply, it will
  eventually resend the read request.

These two message types are embedded

```golang

// ReplicaRead isn't used directly on the wire protocol
// but is embedded inside the ReplicaMessage which of course
// are sent by the couriers to the replicas.
type ReplicaRead struct {
    Cmds *Commands

    BoxID *[32]byte
}

// ReplicaReadReply isn't used directly on the wire protocol
// but is embedded inside the ReplicaMessageReply which of course
// are sent by the replicas to the couriers. Therefore the
// ReplicaReadReply command is never padded because it is always
// encapsulated by the ReplicaMessageReply which is padded.
type ReplicaReadReply
 struct {
    Cmds *Commands
    Geo  *geo.Geometry

    ErrorCode uint8
    BoxID     *[32]byte
    Signature *[32]byte
    Payload   []byte
}
```

These message types below are only used for storage node replication between replicas:

```golang


// ReplicaWrite has two distinct uses. Firstly, it is
// to be used directly on the wire for replication between replicas.
// Secondly, it can be embedded inside a ReplicaMessage which of course
// are sent from couriers to replicas.
type ReplicaWrite struct {
    Cmds *Commands

    BoxID     *[32]byte
    Signature *[32]byte
    Payload   []byte
}

// ReplicaWriteReply can facilitate replication between replicas as the
// reply to the ReplicaWrite command. Otherwise it is embedded in a
// ReplicaMessageReply and sent from replicas to couriers.
type ReplicaWriteReply struct {
    Cmds *Commands

    ErrorCode uint8
}

```

# Protocol Sequence Annotations

The following two images indicate the protocol from for reads and writes without
showing the replication. This is the simplest way to annotate the protocol sequences:

![protatocol annotatation image of writes](/docs/specs/annotated_write.png "Annotated Writes")

![protatocol annotatation image of reads](/docs/specs/annotated_read.png "Annotated Reads")



# Pigeonhole AllOrNothing protocol

This AllOrNothing message is an "at most once" delivery mechanism, its
purpose is to ensure that a set of individual BACAP writes either
succeed or fail atomically from the point of a Replica (or 2nd party
client reader) trying to correlate the sending Client's failure to
transmit multiple messages at once with network interruptions on the
sending Client's side of the network.

Regardless of the number of messages in the set, the adversaries get
to observe "at most once" that the sending client interacted with the
network.

## Step 1

First, the client uploads a BACAP stream to the storage replicas.

The stream payloads are filled with []CourierEnvelope concatenated
back-to-back.  Since CourierEnvelope is strictly larger than a BACAP
payload, because they themselves contain BACAP payloads, multiple
stream boxes will be used.

## Step 2.

The client sends the BACAP stream read capability to the courier
service.  And tells the courier to decrypt them and process the
embedded CourierEnvelope structs.

The courier does NOT need to keep track of the EnvelopeHash for each
of the contained CourierEnvelope for the purpose of replying to the
client (which is in this case the courier itself), but it does need to
keep resending them to the replicas until the intermediate replicas
have ACK'ed them.

OTOH the courier MUST keep track of the hash of the CourierAtMostOnce
message and MUST NOT process a stream more than once.

```golang

// This is sent from the Client to its Courier
// It MUST NOT be sent before the Client has successfully uploaded each box in the stream to a courier.
type CourierAllOrNothing struct {
    Version uint8 // == 0, reserved for future extensions to this spec.
    
    StreamReadCap StreamReadCap
}

// This is sent from the Courier to the Client
// It means "STOP RESENDING THIS CourierAllOrNothing"
type CourierAllOrNothingACK struct {
    HashOfCourierAllOrNothing []byte
}
```

## AllOrNothing potential use cases


In no particular order:

* Atomically writing to two or more boxes
  - The boxes can reside on distinct streams (or not); the courier
    doesn't know anything about streams of the CourierEnvelopes.
* Sending long messages that span more than one BACAP payload, like a
  file / document / picture.
* Group chat join uses All or Nothing protocol when we add a new
  member to the group:
    * The person introducing a new member writes to their group chat
      stream
    * The person introducing a new member also writes to their
      existing conversation stream that the new member is reading
* Group chat uses it in all cases where it needs to send long messages
  (files, pictures, audio, long cryptographic keys like the group
  membership list)



# Protocol narration example:
    
    Alice wants to send a message to Bob, who is already connected to Alice.
    i.e. Alice will be writing to box 12345 that Bob is trying to read from.
    
1. She sends:
  - SPHINX packet containing:
    - SPHINX header:
        - Routing commands to make it arrive at a Courier (KP Service Provider)
    - SPHINX payload:
        - reply SURB
        - Payload encrypted for a Courier (chosen at random): CourierEnvelope
          The envelope tells the Courier about two randomly chosen replicas
          ("intermediate replicas").
    - Alice doesn't know whether the packet makes it through the network or not.
      Until she receives a reply, she will keep resending the CourierEnvelope to
      the same Courier. (TODO: This spec needs names for all these timers)

2. The Courier receives the CourierEnvelope from Alice.
   2.1) The Courier records the EnvelopeHash of the CourierEnvelope in its CourierBookKeeping datastructure.
   2.2) If the Courier has already seen that hash, GOTO STEP 4.

3) The Courier sends an ACK to Alice using the SURB on file for Alice, telling her to stop resending the CourierEnvelope. If there's no SURB, the Courier waits for the next resent CourierEnvelope from Alice matching the EnvelopeHash.
   3.1) The Courier constructs two ReplicaMessage and put them in its outgoing queue for the two intermediate replicas. (Bear in mind that each Courier maintains constant-rate traffic with all replicas).
   3.2) It will keep doing this for each intermediate replica until it receives an ACK from that replica.

   Alice is done with her part now.

4) The two "intermediate replicas" receive the two ReplicaMessage.
   4.1) They decrypt them and compute the "designated replicas" based on the BACAP box ID. TODO see paper for how that works. TODO: each intermediate replica should only contact one designated replica, but how does it do that without knowing about the other intermediate replica? we need to add a field somewhere.
   4.2) They put ACKs in their outgoing queue for the Courier saying "we have got these messages (see step 3.2)", referencing the EnvelopeHash. This tells the Courier to stop resending to the intermediate replicas.
   4.3) They put the decrypted contents (a ReplicaWrite BACAP tuple: box ID 12345; signature; encrypted payload) in their outgoing queues for the "designated replicas".
   4.4) Each replica waits for a reply from its designated replica.
   4.5) When the intermediate replica receives its ACK from the designated replica, the intermediate replica is done.

  Bob now wants to check if Alice has written a message at box 12345

5) Similar to step 1, Bob sends a SPHINX packet to a Courier chosen at random.

     5.1) The payload is a CourierEnvelope:

          - Two intermediate replicas

          - Its encrypted payload is a ReplicaRead command (reference box ID 12345)

   5.2) This is resent to the same Courier until a reply comes in.

6) Courier receives Bob's CourierEnvelope (see step 2)

7) (see step 3)

8) The two intermediate replicas receive the two ReplicaMessage (containing Bob's ReplicaRead)
   8.1) (see 4.1)
   8.2) (see 4.2)
   8.3) (see 4.3)
   8.4) (see 4.4)
   8.5) When the intermediate replica receives its ACK from the designated replica, it will include the (perhaps confusingly named) ReplicaWrite (BACAP tuple).
   8.6) The intermediate replica wraps it in a ReplicaMessageReply encrypted for Bob's ReplicaMessage.EPubKey and puts it in its outgoing queue for the Courier.


9) The Courier receives two ReplicaMessageReply.
   9.1) It matches ReplicaMessageReply.EnvelopeHash to its recorded state (step 2.1).
   9.2) If it has a SURB on file for Bob, it forwards a ReplicaMessageReply to Alice.
   9.3) Either way it stores the ReplicaMessageReply "for a while".

10) Bob keeps resending his CourierEnvelope from 5) until he receives a ReplicaMessageReply
   10.1) Bob decrypts it with the private key corresponding to his
         CourierEnvelope.EPubKey
   10.2) It's either a ReplicaWrite / BACAP tuple (TODO Bob doesn't really need to receive the PK since he asked for it TODO), or a NACK. If it's a NACK, goto 10).
   10.3) Bob can now read Alice's message. Bob is done.

