---
title:
linkTitle: "Pigeonhole Protocol Design Specification"
url: "docs/specs/pigeonhole"
description: ""
categories: [""]
tags: [""]
author: ["Threebit Hacker", "David Stainton"]
version: 0
draft: false
---

# Pigeonhole Protocol Design Specification

# Abstract

In this specification we describe the components and protocols that
compose Pigeonhole scattered storage. We define the behavior of
communication clients that send and retrieve individual messages,
BACAP streams, and AllOrNothing streams. Client actions are mediated
through courier services that interact with storage replicas.


# Introduction

Pigeonhole scattered storage enables persistent anonymous
communication in which participants experience a coherent sequence of
messages or a continuous data stream, but where user relationships and
relations between data blocks remain unlinkable not only from the
perspective of third-party observers, but also from that of the mixnet
components. This latter attribute provides resilience against
deanonymization by compromised mixnet nodes.

The data blocks that Pigeonhole stores are supplied by the BACAP
(Blinding-and-Capability) scheme. The Pigeonhole protocol scatters
messages around the many storage servers and among a space of BACAP Box IDs.
From a passive network observer's perspective all of this is seemingly random.
All communication among users consists of
user-generated read or write queries to Pigeonhole storage, never
directly to other users.


Many protocols are possible to compose using Pigeonhole communication channels,
including group communications. This specification
describes the protocols that are also detailed in our paper, in section entitled
"5.6. End-to-end reliable group channels". For more
information about BACAP, see "Echomix: a Strong Anonymity System with
Messaging", chapter 4: https://arxiv.org/abs/2501.02933. For an
understanding of how the core BACAP primitives are implemented,see
https://github.com/katzenpost/hpqc/blob/main/bacap/bacap.go.

All code snippets are in Golang.

# Glossary

* **Box**: BACAP's unit of data storage. Each box has a box ID (which also serves as its public key), a signature, and a ciphertext signed payload.

* **Courier**: Service that runs on a service node and interacts with
  storage replicas. Proxies requests from clients and routes replies
  back to clients (via SURBs).

* **Storage replica**: The actual storage nodes where message ciphertexts
  are stored and retrieved.

* **Intermediate replica**: See "5.4.1. Writing messages": 

  Intermediate replicas are chosen independently of the two final
  replicas for that box ID, which they are derived using the sharding
  scheme. The reason Alice designates intermediate replicas, as
  opposed to addressing the final replicas directly, is to avoid
  revealing to the courier which shard the box falls into.

# BACAP message parameters

BACAP messages in Katzenpost are defined as follows.

```
Max BACAP payload = SphinxGeometry's UserForwardPayloadLength - CBOR overhead
```

```  
BACAP_PAYLOAD_SIZE (c_i^{ctx}) = UserForwardPayloadLength – COURIER_ENVELOPE_SIZE
```
```
COURIER_ENVELOPE_SIZE = 32 bytes + CTIDH1024PKSIZE + 2*(32+1) bytes + REPLICA_ENVELOPE_SIZE
```
```
REPLICA_ENVELOPE_SIZE = 32 bytes + CTIDH1024PKSIZE + 32 bytes + BACAP PAYLOAD SIZE 32 + 64 bytes
```
```
CTIDH1024PKSIZE = ??? is this just 128 bytes ???
```

Courier envelopes (seen by courier, coming in via SPHINX) have the following structure:

```
1) Sender’s ephemeral hybrid public key:
    a) x25519 public key: 32 bytes
    b) CTIDH-1024 public key
2) For each designated replica:
    Envelope DEK encrypted with shared secret between sender private key 
    and replica public key: 32 bytes
3) Replica/shard id designating each replica to contact: 1 byte
4) ReplicaEnvelope: 32 bytes + CTIDH1024PKSIZE + 32 bytes + BACAP PAYLOAD SIZE 32 + 64 bytes  
```

Replica envelopes (seen by storage replicas) have the following structure:

```
1) Sender’s ephemeral public key
    a) x25519 public key: 32 bytes
    b) CTIDH-1024 public key
2) 256-bit DEK encrypted to the replica’s public key: 32 bytes
3) Enveloped message, encrypted with DEK, containing a BACAP message:
    a) BACAP box ID (M ctx i ): 32 bytes
    b) BACAP payload (c ctx i )
    c) BACAP signature (s ctx i ): 64 bytes
```


# Message types and interactions

**Overview**

* For each message passed to a courier, clients ask for a reply from either replica  
  number 1 or number 2.
* The courier returns the corresponding reply if it has that reply. If it doesn't  
  have the requested reply, but it does have the other reply, it sends the reply  
  that it *does* have to the client. The courier indicates in either case which 
  replica the reply came from.
* If the client doesn’t receive any reply, it will eventually resend the request.

**CourierEnvelope**

Sent from a client to its courier when the client is trying to either read or write a single BACAP box.

```CourierEnvelope``` specifies intermediate replica IDs and NOT the final
destination replica IDs. Saving bandwidth, only one ```CourierEnvelope``` needs to be sent to the courier, which then writes to each of the specified IDs.  

```
type CourierEnvelope struct {

    // Messages are initially sent to IntermediateReplicas, and eventually
    // replicated to their locations. This hides the real locations from the
    // courier.

    IntermediateReplicas      [2]uint8

    // DEK is used for each replica: ReplicaMessage.DEK

    DEK           [2]*[32]byte

    // Explanation of ReplyIndex:
    //
    // The client resends its messages to the courier until it receives
    // a reply. The courier is responsible for NOT sending each of those resent
    // messages to the replicas. It can use the EnvelopeHash to deduplicate them.
    // When the client sends a CourierEnvelope for which the courier already has   
    // multiple ReplicaMessageReply objects, the courier needs to respond 
    // with exactly one of those. ReplyIndex lets the client choose which one.  
    // Could also be a bool.

    ReplyIndex uint8 

    // The next two fields are hashed to form the EnvelopeHash that is 
    // later used in ReplicaMessageReply:

    // SenderEPubKey 
    SenderEPubKey []byte   // x25519 + ctidh1024 NIKE key of the client

    // Ciphertext is encrypted and MACed
    Ciphertext    []byte // ReplicaMessage.Ciphertext
}
```

**ReplicaMessage**

Sent over the wire protocol from a courier to the replicas, one replica at a time.

The courier service transforms one ```CourierEnvelope``` into two ```ReplicaMessage``` objects, one for each destination replica. The courier forwards those two ```ReplicaMessage``` objects to their respective replicas.


```
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

**ReplicaMessageReply**

In response to a ```ReplicaMessage```, the courier expects an asynchronous ```ReplicaMessageReply``` from each replica.

```
type ReplicaMessageReply struct {
    Cmds *Commands

    ErrorCode     uint8
    EnvelopeHash  *[32]byte
    EnvelopeReply []byte    // TODO we haven't defined this
}
```

**CourierBookKeeping**

The courier MUST keep track of each each ```ReplicaMessage``` and each ```EnvelopeHash``` (in ```ReplicaMessageReply```) that it sends to the replicas, AND it must link each of the hashes to a client SURB so that it can send a reply.

For each EnvelopeHash, the courier keeps a map to ```CourierBookKeeping```:

```
type CourierBookKeeping struct {
    SURB [2]*[]byte // maybe we only need one

    SURBTimestamps [2]*time.Time // when we received SURB[i], so we can delete it when it's too old

    EnvelopeReplies [2]*ReplicaMessageReply // from replicas to courier, eventually sent to client
}
```

**CourierEnvelopeReply**

Sent by the courier to the client.

```
type CourierEnvelopeReply struct {
    EnvelopeHash EnvelopeHash // the EnvelopeHash that this reply corresponds to

    // ReplyIndex is a copy of the CourierEnvelope.ReplyIndex field from the
    // CourierEnvelope that this CourierEnvelopeReply corresponds to

    ReplyIndex uint8

    Payload ReplicaMessageReply
}
```

# Embedded message types

These message types are not used directly on the wire protocol, but are embedded in other message types.

**ReplicaRead** 

Embedded inside ```ReplicaMessage```, which is sent by couriers to replicas.

```
type ReplicaRead struct {
    Cmds *Commands

    BoxID *[32]byte
}
```

**ReplicaReadReply**

Embedded inside ```ReplicaMessageReply```, which is sent by replicas to couriers. ```ReplicaReadReply``` needs no padding because ```ReplicaMessageReply``` has padding.

```
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

# Internal message types


These message types are only used for storage node replication between replicas.


**ReplicaWrite**

Can be used directly on the wire for replication between replicas, or embedded inside a ```ReplicaMessage``` object which is sent from a courier to a replica.

```
type ReplicaWrite struct {
    Cmds *Commands

    BoxID     *[32]byte
    Signature *[32]byte
    Payload   []byte
}
```

**ReplicaWriteReply**

Facilitates replication between replicas as the reply to the ```ReplicaWrite``` command. It can also be embedded in a ```ReplicaMessageReply``` object sent from a replica to courier.

```
type ReplicaWriteReply struct {
    Cmds *Commands

    ErrorCode uint8
}

```

# Protocol sequence visualizations

For simplicity, the following diagrams omit replication while illustrating the Pigeonhole write and read operations.

**Pigeonhole write operation**

![protocol annotatation image of writes](/docs/specs/annotated_write.png "Annotated Writes")

**Pigeonhole read operation**

![protocol annotatation image of reads](/docs/specs/annotated_read.png "Annotated Reads")



# Pigeonhole AllOrNothing protocol

The AllOrNothing delivery mechanism ensures that a set of associated BACAP writes  either succeeds or fails atomically from the point of view of a replica or second-party client reader. This behavior prevents an adversary from detecting a correlation between (A) the sending client's failure to transmit multiple messages at once with (B) a network interruption on the sending client's side of the network. Regardless of the number of messages in the set, the adversary  gets to observe "at most once" that the sending client interacted with the
network.

The protocol works as follows.

## Step 1

The client uploads a BACAP stream to the storage replicas.

The stream payloads consist of ```[]CourierEnvelope``` objects concatenated
back-to-back. Because a ```CourierEnvelope``` is strictly larger than a BACAP
payload, which itself contains BACAP payloads, multiple boxes must be used.

## Step 2

The client sends the BACAP stream read capability to the courier service and tells it to decrypt and process the embedded ```CourierEnvelope``` structs.

The courier does NOT need to keep track of the ```EnvelopeHash``` for each
of the contained ```CourierEnvelope``` for the purpose of replying to the
client (which is in this case the courier itself), but it does need to
keep resending them to the replicas until the intermediate replicas
have ACK'ed them.

On the other hand, the courier MUST keep track of the hash of the ```CourierAtMostOnce``` message and MUST NOT process a stream more than once.


**CourierAllOrNothing**

Sent by the client to its courier. It MUST NOT be sent before the client has successfully uploaded each box in the stream to a courier.

```
type CourierAllOrNothing struct {
    Version uint8 // == 0, reserved for future extensions to this spec.
    
    StreamReadCap StreamReadCap
}
```

**CourierAllOrNothingACK**

Sent from the courier to the client. It means, "STOP RESENDING THIS ```CourierAllOrNothing```".

```
type CourierAllOrNothingACK struct {
    HashOfCourierAllOrNothing []byte
}
```

## Potential use cases of AllOrNothing


In no particular order:

* Atomically writing to two or more boxes.
  - The boxes can reside on distinct streams (or not); the courier
    doesn't know anything about streams of ```CourierEnvelope```.
* Sending long messages that span more than one BACAP payload, like a
  file / document / picture.
* Group chat join uses AllOrNothing when adding a new member to the group:
    * The person introducing a new member writes to their group chat stream.
    * The person introducing a new member also writes to the existing conversation 
      stream that the new member can already read.
* Group chat uses AllOrNothing in all cases where it needs to send long messages -- 
  files, pictures, audio, long cryptographic keys such as the group
  membership list, and so on.



# Protocol narration example
    
Alice wants to send a message to Bob, who is already connected to Alice. That is, Alice will write to a box with ID 12345 that Bob is trying to read from.
    
1. Alice sends:

    1.1. SPHINX packet containing:

    - SPHINX header

        - Routing commands to make it arrive at a courier (on a service provider)

    - SPHINX payload

        - Reply SURB

        - ```CourierEnvelope``` encrypted for a courier chosen at random. The  
        envelope tells the courier about two randomly chosen replicas
        ("intermediate replicas").

    1.2 Alice doesn't know if the packet makes it through the network. Until she    
    receives a reply, she keeps resending the ```CourierEnvelope``` to the same 
    courier.

2. The courier receives the ```CourierEnvelope``` from Alice.

   2.1. The courier records the ```EnvelopeHash``` of the ```CourierEnvelope``` in 
   its ```CourierBookKeeping``` datastructure.

   2.2. If the courier has already seen that hash, GOTO Step 4.

3. The courier sends an ACK to Alice using the SURB on file for Alice, telling her to stop resending the ```CourierEnvelope```. If there's no SURB, the Courier waits for the next re-sent ```CourierEnvelope``` from Alice matching the ```EnvelopeHash```.

   3.1. The courier constructs two ```ReplicaMessage``` objects and puts them in 
   its outgoing queue for the two intermediate replicas. (Note that each courier    
   maintains constant-rate traffic with all replicas).

   3.2. The courier keeps doing this for each intermediate replica until it 
   receives an ACK from that replica.

Alice’s actions are now complete.

4. The two intermediate replicas receive the two ```ReplicaMessage``` objects.

   4.1. They decrypt them and compute the "designated replicas" based on 
   the BACAP box ID. 

   4.2. The replicas put ACKs in their outgoing queues for the courier saying "we 
   have received these messages” (see step 3.2), referencing the     
   ```EnvelopeHash```. This tells the courier to stop resending to the intermediate 
   replicas.

   4.3. They put the decrypted contents (a ```ReplicaWrite``` BACAP tuple: box ID 
   12345; signature; encrypted payload) in their outgoing queues for the 
   "designated replicas".

   4.4. Each replica waits for a reply from its designated replica.

   4.5. When an intermediate replica receives its ACK from the designated replica,    
   the intermediate replica has no more tasks.

Bob now wants to check if Alice has written a message at box 12345

5. Similar to step 1, Bob sends a SPHINX packet to a courier chosen at random.

     5.1. SPHINX packet containing:

     - SPHINX header

         - Routing commands to make it arrive at a courier (on a service provider).

     - SPHINX payload          

         - The envelope tells the courier about two randomly chosen replicas    
           (“intermediate replicas”).

         - ```CourierEnvelope``` encrypted for a courier chosen at random. Its 
           encrypted payload is a ```ReplicaRead``` command (reference box ID 
           12345).

   5.2. Bob doesn't know if the packet makes it through the network. Until he    
   receives a reply, he keeps resending the ```CourierEnvelope``` 
   to the same courier.

6. The courier receives Bob's ```CourierEnvelope``` (see step 2),

7. See step 3.

8. The two intermediate replicas receive the two ```ReplicaMessage``` objects containing Bob's ```ReplicaRead```

   8.1. (See 4.1.)

   8.2. (See 4.2.)

   8.3. (See 4.3.)

   8.4. (See 4.4.)

   8.5. When the intermediate replica receives its ACK from the designated replica,  
   it will include the (perhaps confusingly named) ```ReplicaWrite``` (BACAP 
   tuple).

   8.6. The intermediate replica wraps it in a ```ReplicaMessageReply``` encrypted 
   for Bob's ```ReplicaMessage.EPubKey``` and puts it in its outgoing queue for the 
   Courier.

9. The Courier receives two ```ReplicaMessageReply```.
   
   9.1. It matches ```ReplicaMessageReply.EnvelopeHash``` to its recorded state 
   (step 2.1).

   9.2. If it has a SURB on file for Bob, it forwards a ```ReplicaMessageReply```   
   to Alice.

   9.3. Either way it stores the ```ReplicaMessageReply``` "for a while".


10. Bob keeps resending his ```CourierEnvelope``` from step 5 until he receives a ```ReplicaMessageReply```.
      
    10.1. Bob decrypts it with the private key corresponding to his
    ```CourierEnvelope.EpubKey```

    10.2. It's either a ```ReplicaWrite``` / BACAP tuple, or a NACK. If it's a 
    NACK, GOTO step 10.

    10.3. Bob can now read Alice's message.

