---
title:
linkTitle: Katzenpost Client Integration Guide
description: ""
categories: [""]
tags: [""]
author: []
version: 0
draft: false
slug: "/client_integration/"
---


## Overview

This guide is intended to help developers connect their applications
and projects to a Katzenpost mixnet client.

The Katzenpost client daemon - <b>kpclientd</b> - connects to the
Katzenpost mixnet. It has <i>thin client</i> libraries in Go, Python
and Rust, which you can integrate into your app that you want to work
over Katzenpost. The client can multiplex connections to the mixnet
from multiple applications on the same device.

A <i>thin client</i> is an API interface for the client. It's a simple
protocol where clients send and receive CBOR encoded length prefixed
blobs. All of the cryptographic and network complexities are handled
by the daemon so that applications don't need to do it. However, you
should think of the client as part of the application, and remember
that it's the outgoing connection from the client that has the
mixnet's privacy properties.

Our thin client protocol is described here:
https://katzenpost.network/docs/specs/thin_client.html

It can be extended to be used by any language that has a CBOR
serialization library and can talk over TCP or UNIX domain
socket. Currently there are three thin client libraries and
the reference implementation is written in golang:

{{< tabpane text=true >}}
{{% tab header="**Go**" %}}
**Source code:** https://github.com/katzenpost/katzenpost/tree/main/client2

**API docs:** https://pkg.go.dev/github.com/katzenpost/katzenpost/client2/thin

The Go thin client provides a comprehensive API for interacting with the Katzenpost mixnet.
{{% /tab %}}

{{% tab header="**Rust**" %}}
**Source code:** https://github.com/katzenpost/thin_client/blob/main/src/lib.rs

**API docs:** https://docs.rs/katzenpost_thin_client/0.0.4/katzenpost_thin_client/

**Example:** https://github.com/katzenpost/thin_client/blob/main/examples/echo_ping.rs

The Rust thin client provides async/await support for modern Rust applications.
{{% /tab %}}

{{% tab header="**Python**" %}}
**Source code:** https://github.com/katzenpost/thin_client/blob/main/thinclient/__init__.py

**API docs:** https://katzenpost.network/docs/python_thin_client.html

**Examples:**
- https://github.com/katzenpost/thin_client/blob/main/examples/echo_ping.rs
- https://github.com/katzenpost/status
- https://github.com/katzenpost/worldmap

The Python thin client is ideal for rapid prototyping and integration with existing Python applications.
{{% /tab %}}
{{< /tabpane >}}

### Table Of Contents

*Complete guide sections:*

| Section | Description |
|---------|-------------|
| **🔹 [Overview](#overview)** | **Introduction to Katzenpost client integration and thin client libraries** |
| **🔸 [Core functionality API](#core-functionality)** | **Basic client operations: connection management, PKI documents, mixnet service discovery, events/replies** |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Connecting and Disconnecting](#connecting-and-disconnecting) | How to establish and terminate connections to the kpclientd daemon |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Get a view of the network via the PKI Document](#get-a-view-of-the-network-via-the-pki-document) | Obtaining network topology and service information |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Get a random instance of a specific service](#get-a-random-instance-of-a-specific-service) | Finding and selecting mixnet services |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Receiving Thin Client Events and Service Reply Messages](#receiving-thin-client-events-and-service-reply-messages) | Event handling patterns and message processing |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Thin client events](#thin-client-events) | Core events: shutdown, connection status, and PKI document updates |
| **🔸 [Legacy API](#legacy-api)** | **Message oriented communication with mixnet services, with optional ARQ error correction scheme** |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Legacy Events](#legacy-events) | Events specific to the legacy message API |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Sending a message](#sending-a-message) | How to send messages using the legacy API |
| **🔸 [Pigeonhole Channel API](#pigeonhole-channel-api)** | **Reliable, ordered, persistent, replicated communication channels** |


## Core functionality

### Connecting and Disconnecting

The thin client connects and disconnects from the kpclientd daemon
like so:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Load thin client configuration
cfg, err := thin.LoadFile("thinclient.toml")
if err != nil {
    log.Fatal(err)
}

logging := &config.Logging{Level: "INFO"}
// create thin client
client := thin.NewThinClient(cfg, logging)

// Connect to kpclientd daemon
err = client.Dial()
if err != nil {
    log.Fatal(err)
}

// ... do stuff ...

// Disconnect from kpclientd daemon
client.Close()
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
// connect to kpclientd daemon
let client = ThinClient::new(cfg).await?;

// ... do stuff ...

// disconnect from kpclientd daemon
client.stop().await?;

{{< /tab >}}

{{< tab header="Python" lang="python" >}}
thin_client = ThinClient(config)

# connect to kpclientd daemon
await thin_client.start()

# ... do stuff ...

# disconnect from kpclientd daemon
thin_client.stop()
{{< /tab >}}
{{< /tabpane >}}

### Get a view of the network via the PKI Document

`kpclient` needs the PKI document for internal use for Sphinx packet routing.
However applications will also need the PKI document to learn about the
mixnet services that are available and to choose which ones to use.

You can obtain a PKI document using the thin client API, like so:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}

// Usage example:
doc := thin.PKIDocument()
if doc == nil {
    panic("No Document")
}
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
// Get the PKI document asynchronously
let doc = thin_client.pki_document().await;
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Get the PKI document
doc = thin_client.pki_document()
{{< /tab >}}
{{< /tabpane >}}

### Get a random instance of a specific service

When creating an app that works over a mixnet, you will need to
interact with <i>mixnet services</i> that are listed in the PKI
document. For example, our mixnet ping CLI tool gets a random echo
service from the PKI document and handles its business using
that information:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
desc, err := thin.GetService("echo")
if err != nil {
    panic(err)
}
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
let service_desc = thin_client.get_service(service_name).await?;
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
service_descriptor = thin_client.get_service(doc, service_name)
{{< /tab >}}
{{< /tabpane >}}

The `GetService` or `get_service` is a convenient helper method which searches the PKI
document for the the service name we give it and then selects a random
entry from that set. I don't care which XYZ service I talk to just so
long as I can talk to one of them. The result is that you procure a
`service descriptor object` which contains a destination mix descriptor
and a destination queue ID.

## Receiving Thin Client Events and Service Reply Messages

It's worth noting that our Go thin client implementation gives you
an events channel for receiving events from the client daemon, whereas
the Python and Rust thin clients allow you to specify callbacks for
each event type. Both approaches are equivalent to each other. HOWEVER,
the events channel approach is more flexible and allows you to
easily write higher level abstractions that do automatic retries.
So we might consider updating our Rust and Python thin clients to use
the events channel approach.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
thin := thin.NewThinClient(cfg)
err = thin.Dial()
if err != nil {
    panic(err)
}

// Use EventSink() to get a channel of events
eventCh := thin.EventSink()
for ev := range eventCh {
    switch ev.(type) {
        case *thin.NewDocumentEvent:
            // handle new PKI document event
        case *thin.MessageReplyEvent:
            // handle message reply event
        case *thin.ConnectionStatusEvent:
            // handle connection status change
        default:
            // handle other events
    }
}
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
// Set up event callbacks when creating the client
let mut thin_client = ThinClient::new(config)
    .on_new_document(|doc| {
        // handle new PKI document
    })
    .on_message_reply(|reply| {
        // handle message reply
    })
    .on_connection_status(|status| {
        // handle connection status change
    });

thin_client.start().await?;
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Define callback functions
def on_new_document(doc):
    # handle new PKI document
    pass

def on_message_reply(reply):
    # handle message reply
    pass

def on_connection_status(status):
    # handle connection status change
    pass

# Create client with callbacks
thin_client = ThinClient(
    config,
    on_new_document=on_new_document,
    on_message_reply=on_message_reply,
    on_connection_status=on_connection_status
)

thin_client.start()
{{< /tab >}}
{{< /tabpane >}}

### Thin client events

Here I'll tell you a bit about each of the events that thin clients
receive. Firstly, these are the core events that all thin clients
receive:

* `shutdown_event`: This event tells your application that the Katzenpost
  client daemon is shutting down.

* `connection_status_event`: This event notifies your app of a network
  connectvity status change, which is either connected or not
  connected.

* `new_pki_document_event`: This event tells encapsulates the new PKI
  document, a view of the network, including a list of network
  services.


# Legacy API

The legacy API implements a message oriented send and receive protocol
that mixnet clients can use to interact with specific mixnet services
that they choose to interact with. This inevitably creates a non-uniform
packet distribution on the service nodes which a clever adversary could
use to try and deanonymize clients. Therefore for that and many other reasons
we are encouraging the use of the pigeonhole channel API instead.

## Legacy Events

These are the events that are specific to sending and
receiving messages using the legacy API:

* `message_sent_event`: This event tells your app that it's message was
  successfully sent to a gateway node on the mix network.

* `message_reply_event`: This event encapsulates a reply from a service on
  the mixnet.

* `arq_garbage_collected_event`: This event is an ARQ garbage collecton
  event which is used to notify clients so that they can clean up
  their ARQ specific book keeping, if any.

## Sending a message

Each send operation that a thin client can do requires you to specify
the payload to be sent and the destination mix node identity hash and
the destination recipient queue identity.

The API by design lets you specify either a SURB ID or a message ID
for the sent message depending on if it's using an ARQ to send
reliably or not. This implies that the application using the thin
client must do it's own book keeping to keep track of which replies
and their associated identities.

The simplest way to send a message is using the `SendMessage` method:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Send a message
err := thin.SendMessage(payload, &serviceIdHash, serviceQueueID)
if err != nil {
    panic(err)
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Send a message
thin_client.send_message(payload, dest_node, dest_queue).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Send a message
thin_client.send_message(payload, dest_node, dest_queue)
{{< /tab >}}
{{< /tabpane >}}



## Pigeonhole Channel API

**NOTE: This section of the document specifies our new Pigeonhole Protocol API which does not exist yet.**

**Also NOTE: everything we send has a QueryID identifier like a 128bit random blob, that lets us uniquely identify the reply message(s).
If a client ever repeats one of these (for something we have in memory) and we are posed with the question of whether we should overwrite something or not, we send an event saying "protocol violation, you done fucked up" and disconnects the thinclient.**

The following function signatures represent the new thinclient API for the Pigeonhole protocol
wherein the function arguments will be composed into a specific thinclient request type.
And the return values will be composed into a specific reply (event) type.


<BR>

* NewKeypair (queryID, seed)
    return queryID, WriteCap, ReadCap, First MessageIndex

<BR>

* EncryptRead(queryID, read cap, message box index) -> 
   - query ID
   - MessageCiphertext
   - next message index ( message box index + 1 // or advanced or whatever)
   - envelope descriptor (private key for this read so we can read replies from SendEncryptedMessage later)
   - envelope hash
   - ReplicaEpoch this was encrypted in
   - or: error

<BR>

* EncryptWrite(
   - plaintext,
   -  write cap,
   - message box index, // where to read/write
    ) ->
    - MessageCiphertext
    - ReplicaEpoch this was encrypted in
    - query ID
    - envelope descriptor (private key for this read so we can read replies from SendEncryptedMessage later)
    - envelope hash
    - or: error

<BR>

* StartResendingEncryptedMessage

Takes a MessageCiphertext destined for two intermediate replicas

Some notes on implementation:
- kpclientd picks DestNode + DestQueue (courier)
- kpclientd puts each SendEncryptedMessage in an in-memory queue and takes responsibility for resending, so the thin client only needs to send SendEncryptedMessage once per session.
- In-memory queue: one per app
- kpclientd samples from the collection of all the app queues and puts the "resending" into the egress queue
- when an app disconnects we delete their queue
- when does it stop resending?
- we want to stop resending writes once the courier acks
- kpclientd should stop resending the corresponding write.
- kpclientd should emit an event to tell the app their write was successful
- we want to keep a cache of EnvelopeHash->event so that if an app restarts it can get replies to stuff it just sent (that was answered successfully)
- maybe rotate couriers every now and then
- we want to stop resending reads once there is a successful read
- we should emit an event on successful read
- with our current bug we need to stop resending as soon as we get an error from a 
- we should emit an event on "box not found"

```
StartResendingEncryptedMessage(

      // Needed in order to decrypt the reply, if any:
      ReadCap, WriteCap, // pass in either ReadCap or WriteCap, never both.
      NextMessageIndex, //
      ReplyIndex, // tells courier which reply we want

      // Needed for the intermediate replicas to understand the query:
      EnvelopeDescriptor,
      MessageCiphertext, // encrypted payload (to the intermediates)
      EnvelopeHash, // persistent identifier
      ReplicaEpoch, // used to see which replicas/keys were used
      QueryID: 128 bit random thing // used by the client to match a reply to this message (kind of like the  ChannelID)
    ) -> (
       Plaintext stuff maybe,
       Timestamp: If you don't have a courier reply by now, resend at this time,
       error
    )
```

* CancelResendingEncryptedMessage(EnvelopeHash, QueryID) -> error:
  
  Cancels a previous StartResendingEncryptedMessage (removes it from the in-memory queue at kpclientd)

### Events:
    - There is a reply to your read: QueryID, EnvelopeHash
      - The reply to your read was successful: Plaintext (message)
      - The reply to your read was unsuccessful (box not found)
    - "Your message has been sent": QueryID, EnvelopeHash
    - "Protocol violation, I'm going to disconnect this app"
    - The replicas your message was encrypted to are (not / no longer) in the PKI: QueryID, EnvelopeHash

### kpclientd queues
- global egress queue going to first mix layer (with decoys interleaved)
- per-app egress queue (unbounded), killed when app disconnects
- success queue: EnvelopeHash -> successful reply, entries are cleaned up after ... 5 minutes?

### we need to solve the "box not found" Negative ACK cache
- replicas need to tell the couriers when the boxes are filled
- so the kpclientd can keep resending the read and eventually get a successful reply
- we need to spec out the on-disk structures on replica+courier to support this

