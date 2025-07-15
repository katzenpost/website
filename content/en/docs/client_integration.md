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
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Trivial Example: Alice sends Bob a message](#trivial-example-alice-sends-bob-a-message) | Basic channel communication workflow |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Reading From Both Storage Replicas](#reading-from-both-storage-replicas) | Accessing redundant message storage |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Channel Resumptions](#channel-resumptions) | Crash fault tolerance and state recovery |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• [Trivial Write Channel Resumption Work Flow](#trivial-write-channel-resumption-work-flow) | Resuming unused write channels |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• [Trivial Read Channel Resumption Work Flow](#trivial-read-channel-resumption-work-flow) | Resuming unused read channels |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• [Write Channel Resumption After Sending A Query](#write-channel-resumption-after-sending-a-query) | Resuming write channels after network operations |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• [Read Channel Resumption After Sending A Query](#read-channel-resumption-after-sending-a-query) | Resuming read channels after network operations |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• [Write Channel Resumption After Preparing an Unsent Write Query](#write-channel-resumption-after-preparing-an-unsent-write-query) | Resuming channels with prepared but unsent queries |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• [Read Channel Resumption After Preparing an Unsent Read Query](#read-channel-resumption-after-preparing-an-unsent-read-query) | Resuming read channels with prepared but unsent queries |


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

The Pigeonhole channel API implements a low level channel oriented API
which provides reliable, ordered, persistent, replicated communication
in addition to being resistant to active and passive attacks.

The details of the Pigeonhole protocol are described in our paper:
[Echomix: a Strong Anonymity System with Messaging](https://arxiv.org/abs/2501.02933)

NOTE that just like the core and legacy thin client API, this is a
request/response protocol and our so called "commands" are embedded
in our `Request` type which thin clients send to the kpclientd daemon,
and events our embedded in our `Response` type which the daemon sends
to thin clients.

Our new Pigeonhole Channel API has the following Thinclient commands:

* `create_write_channel`
* `create_read_channel`
* `close_channel`
* `write_channel`
* `read_channel`
* `resume_write_channel`
* `resume_read_channel`
* `resume_write_channel_query`
* `resume_read_channel_query`
* `send_channel_query`

Only the `send_channel_query` command causes network traffic. The other
commands are used to prepare our cryptographic state and our query payloads
which can be sent via the `send_channel_query` command. This is a crash fault
tolerant API and thus each of the reply event types are used for transmitting
cryptographic state information so that if there's a crash the application
can resume where it left off.

The following are the events that are specific to the pigeonhole channel API:

* `create_write_channel_reply`
* `create_read_channel_reply`
* `close_channel_reply`
* `write_channel_reply`
* `read_channel_reply`
* `resume_write_channel_reply`
* `resume_read_channel_reply`
* `resume_write_channel_query_reply`
* `resume_read_channel_query_reply`
* `channel_query_sent_event`
* `channel_query_reply_event`

Please refer to our API documentation for more information about the above commands and events.

**WARNING: The Pigeonhole Channel API has not yet been implemented in the Rust and Python thin clients.**

{{< tabpane text=true >}}
{{% tab header="**Go**" %}}
**Source code:** https://github.com/katzenpost/katzenpost/tree/main/client2

**API docs:** https://pkg.go.dev/github.com/katzenpost/katzenpost/client2/thin

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



### Trivial Example: Alice sends Bob a message

This demonstrates Alice sending a message to Bob using the Pigeonhole Channel API:
1. Alice creates a write channel
2. Alice prepares her message for transmission
3. Alice gets courier destination and sends the message
4. Alice sends the query and waits for confirmation the message was stored
5. Bob creates a read channel using Alice's read capability
6. Bob creates a read query
7. Bob sends the read queries until a reply is received
8. Bob verifies he received Alice's original message

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// 1. Alice creates a write channel
aliceChannelID, readCap, writeCap, err := aliceThinClient.CreateWriteChannel(ctx)

// 2. Alice prepares her message for transmission
aliceMessage := []byte("Hello Bob!")
writeReply, err := aliceThinClient.WriteChannel(ctx, aliceChannelID, aliceMessage)

// 3. Alice gets courier destination and sends the message
destNode, destQueue, err := aliceThinClient.GetCourierDestination()
aliceMessageID := aliceThinClient.NewMessageID()

// 4. Alice sends the query and waits for confirmation the message was stored
_, err = aliceThinClient.SendChannelQueryAwaitReply(ctx, aliceChannelID,
    writeReply.SendMessagePayload, destNode, destQueue, aliceMessageID)

// 5. Bob creates a read channel using Alice's read capability
bobChannelID, err := bobThinClient.CreateReadChannel(ctx, readCap)

// 6. Bob creates a read query
readReply1, err := bobThinClient.ReadChannel(ctx, bobChannelID, nil, nil)

// 7. Bob sends the read queries until a reply is received
bobMessageID1 := bobThinClient.NewMessageID()
var bobReceivedMessage []byte
for i := 0; i < 10; i++ {
	bobReceivedMessage, err = bobThinClient.SendChannelQueryAwaitReply(
        ctx,
        bobChannelID,
        readReply1.SendMessagePayload,
        destNode,
        destQueue,
        bobMessageID1)
	assert.NoError(t, err)
	if len(bobReceivedMessage) > 0 {
		break
	}
}

// 8. Bob verifies he received Alice's original message
if bytes.Equal(aliceMessage, bobReceivedMessage) {
    log.Println("Bob successfully received Alice's message!")
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
{{< /tab >}}
{{< /tabpane >}}


### Reading From Both Storage Replicas

Pigeonhole protocols uses a hash based sharding scheme to scatter messages
around the mixnet. This means that each message is stored in two
different storage replicas. The read query will only return a message if
it is found in the first storage replica that is queried. If the message
is not found in the first storage replica, the read query will return an
empty message.

It is up to the application to decide whether to retry the read query
with the second storage replica. Reading the second storage replica's
copy of our message requires using the last two arguments of the `ReadChannel` method,
like so:

1. Alice creates a write channel
2. Alice prepares a write query
3. Alice sends the write query
4. Bob creates a read channel with the readcap from Alice
5. Bob prepares his first read query
6. Bob sends his first read query and waits for reply
7. Bob prepares his second read query, specifying the next message index and reply index
8. Bob sends his second read query and waits for reply

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// 1. Alice creates a write channel
aliceChannelID, readCap, writeCap, nextMessageIndex, err := aliceThinClient.CreateWriteChannel(ctx)

// 2. Alice prepares a write queryaliceMessage := []byte("Message from Alice")
writeReply, err := aliceThinClient.WriteChannel(ctx, aliceChannelID, aliceMessage)
if err != nil {
    log.Fatal("Failed to write message:", err)
}

// 3. Alice sends the write query
destNode, destQueue, err := aliceThinClient.GetCourierDestination()
if err != nil {
    log.Fatal("Failed to get courier destination:", err)
}
messageID := aliceThinClient.NewMessageID()
_, err = aliceThinClient.SendChannelQueryAwaitReply(ctx, aliceChannelID,
    writeReply.SendMessagePayload, destNode, destQueue, messageID)
if err != nil {
    log.Fatal("Failed to send message:", err)
}

// 4. Bob creates a read channel with the readcap from Alice
bobChannelID, err := bobThinClient.CreateReadChannel(ctx, readCap)
if err != nil {
    log.Fatal("Failed to create read channel:", err)
}

// 5. Bob prepares his first read query
readReply1, err := bobThinClient.ReadChannel(ctx, bobChannelID, nil, nil)
if err != nil {
    log.Fatal("Failed to prepare read:", err)
}

// 6. Bob sends his first read query and waits for reply
bobMessageID := bobThinClient.NewMessageID()
var bobReceivedMessage []byte
for i := 0; i < 10; i++ {
	bobReceivedMessage, err = bobThinClient.SendChannelQueryAwaitReply(
        ctx,
        bobChannelID,
        readReply1.SendMessagePayload,
        destNode,
        destQueue,
        bobMessageID)
	assert.NoError(t, err)
	if len(bobReceivedMessage) > 0 {
		break
	}
}

// 7. Bob prepares his second read query, specifying the next message index and reply index
readReply2, err = bobThinClient.ReadChannel(ctx, bobChannelID, nextMessageIndex, readReply.ReplyIndex)
if err != nil {
    log.Fatal("Failed to prepare read:", err)
}

// 8. Bob sends his second read query and waits for reply
for i := 0; i < 10; i++ {
	bobReceivedMessage, err = bobThinClient.SendChannelQueryAwaitReply(
        ctx,
        bobChannelID,
        readReply2.SendMessagePayload,
        destNode,
        destQueue,
        bobMessageID)
	assert.NoError(t, err)
	if len(bobReceivedMessage) > 0 {
		break
	}
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
{{< /tab >}}
{{< /tabpane >}}


### Channel Resumptions

This is a crash fault tolerant API and thus each of the reply event types are used for transmitting cryptographic state information so that if there's a crash the application can resume where it left off. BEWARE that channel IDs are ephemeral and are not to be
persisted.

There are exactly 6 types of channel resumptions:

| Type | Channel | State | Description |
|------|---------|-------|-------------|
| 1 | Write | Never written to | [Resume a write channel that was never written to](#trivial-write-channel-resumption-work-flow) |
| 2 | Read | Never read from | [Resume a read channel that was never read from](#trivial-read-channel-resumption-work-flow) |
| 3 | Write | Query sent | [Resume a write channel that was used to create a write query which was sent](#write-channel-resumption-after-sending-a-query) |
| 4 | Read | Query sent | [Resume a read channel that was used to create a read query which was sent](#read-channel-resumption-after-sending-a-query) |
| 5 | Write | Query not sent | [Resume a write channel that was used to create a write query which was not sent](#write-channel-resumption-after-preparing-an-unsent-write-query) |
| 6 | Read | Query not sent | [Resume a read channel that was used to create a read query which was not sent](#read-channel-resumption-after-preparing-an-unsent-read-query) |

#### Trivial Write Channel Resumption Work Flow

1. Alice creates a write channel
2. Alice closes the write channel
3. Alice resumes the write channel


{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// 1. Alice creates a write channel
aliceChannelID, readCap, writeCap, err := aliceThinClient.CreateWriteChannel(ctx)

// 2. Alice closes the write channel
aliceThinClient.CloseChannel(ctx, aliceChannelID)

// 3. Alice resumes the write channel
aliceThinClient.ResumeWriteChannel(ctx, writeCap, nil)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
{{< /tab >}}
{{< /tabpane >}}


#### Trivial Read Channel Resumption Work Flow

1. Alice creates a write channel
2. Bob creates a read channel using Alice's read capability
3. Bob closes the read channel
4. Bob resumes the read channel

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// 1. Alice creates a write channel
aliceChannelID, readCap, writeCap, err := aliceThinClient.CreateWriteChannel(ctx)

// 2. Bob creates a read channel using Alice's read capability
bobChannelID, err := bobThinClient.CreateReadChannel(ctx, readCap)

// 3. Bob closes the read channel
bobThinClient.CloseChannel(ctx, bobChannelID)

// 4. Bob resumes the read channel
bobThinClient.ResumeReadChannel(ctx, readCap, nil, nil)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
{{< /tab >}}
{{< /tabpane >}}


#### Write Channel Resumption After Sending A Query

1. Alice creates a write channel
2. Alice prepares her write query
3. Alice sends the write query
4. Alice closes the write channel
5. Alice resumes the write channel
6. Alice sends a second write query
7. Bob creates a read channel
8. Bob reads the first message from the channel
9. Bob reads the second message from the channel

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// 1. Alice creates a write channel
aliceChannelID, readCap, writeCap, nextMessageIndex, err := aliceThinClient.CreateWriteChannel(ctx)
if err != nil {
    log.Fatal("Failed to create write channel:", err)
}

// 2. Alice prepares her write query
aliceMessage1 := []byte("First message from Alice")
writeReply1, err := aliceThinClient.WriteChannel(ctx, aliceChannelID, aliceMessage1)
if err != nil {
    log.Fatal("Failed to prepare first write:", err)
}

// 3. Alice sends the write query
destNode, destQueue, err := aliceThinClient.GetCourierDestination()
if err != nil {
    log.Fatal("Failed to get courier destination:", err)
}

messageID1 := aliceThinClient.NewMessageID()
_, err = aliceThinClient.SendChannelQueryAwaitReply(ctx, aliceChannelID,
    writeReply1.SendMessagePayload, destNode, destQueue, messageID1)
if err != nil {
    log.Fatal("Failed to send first message:", err)
}

// 4. Alice closes the write channel
err = aliceThinClient.CloseChannel(ctx, aliceChannelID)
if err != nil {
    log.Fatal("Failed to close channel:", err)
}

// 5. Alice resumes the write channel
resumedChannelID, err := aliceThinClient.ResumeWriteChannel(ctx, writeCap, writeReply1.NextMessageIndex)
if err != nil {
    log.Fatal("Failed to resume write channel:", err)
}

// 6. Alice sends a second write query
aliceMessage2 := []byte("Second message from Alice")
writeReply2, err := aliceThinClient.WriteChannel(ctx, resumedChannelID, aliceMessage2)
if err != nil {
    log.Fatal("Failed to prepare second write:", err)
}

messageID2 := aliceThinClient.NewMessageID()
_, err = aliceThinClient.SendChannelQueryAwaitReply(ctx, resumedChannelID,
    writeReply2.SendMessagePayload, destNode, destQueue, messageID2)
if err != nil {
    log.Fatal("Failed to send second message:", err)
}

// 7. Bob creates a read channel
bobChannelID, err := bobThinClient.CreateReadChannel(ctx, readCap)
if err != nil {
    log.Fatal("Failed to create read channel:", err)
}

// 8. Bob reads the first message from the channel
readReply1, err := bobThinClient.ReadChannel(ctx, bobChannelID, nil, nil)
if err != nil {
    log.Fatal("Failed to read first message:", err)
}

// Send the read query to retrieve the first message
bobMessageID1 := bobThinClient.NewMessageID()
firstMessagePayload, err := bobThinClient.SendChannelQueryAwaitReply(ctx, bobChannelID,
    readReply1.SendMessagePayload, destNode, destQueue, bobMessageID1)
if err != nil {
    log.Fatal("Failed to retrieve first message:", err)
}

// 9. Bob reads the second message from the channel
readReply2, err := bobThinClient.ReadChannel(ctx, bobChannelID, readReply1.NextMessageIndex, nil)
if err != nil {
    log.Fatal("Failed to read second message:", err)
}

bobMessageID2 := bobThinClient.NewMessageID()
secondMessagePayload, err := bobThinClient.SendChannelQueryAwaitReply(ctx, bobChannelID,
    readReply2.SendMessagePayload, destNode, destQueue, bobMessageID2)
if err != nil {
    log.Fatal("Failed to retrieve second message:", err)
}

// Verify messages were received correctly
if bytes.Equal(aliceMessage1, firstMessagePayload) {
    log.Println("Bob successfully received Alice's first message!")
}
if bytes.Equal(aliceMessage2, secondMessagePayload) {
    log.Println("Bob successfully received Alice's second message!")
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
{{< /tab >}}
{{< /tabpane >}}

#### Read Channel Resumption After Sending A Query

1. Alice creates a write channel
2. Alice writes the first message to the channel
3. Alice writes the second message to the channel
3. Bob creates a read channel with the readcap from Alice
4. Bob reads the first message from the channel
5. Bob closes the read channel
6. Bob resumes the read channel
7. Bob reads the second message from the channel

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// 1. Alice creates a write channel
aliceChannelID, readCap, writeCap, nextMessageIndex, err := aliceThinClient.CreateWriteChannel(ctx)
if err != nil {
    log.Fatal("Failed to create write channel:", err)
}

// 2. Alice writes the first message to the channel
aliceMessage1 := []byte("First message from Alice")
writeReply1, err := aliceThinClient.WriteChannel(ctx, aliceChannelID, aliceMessage1)
if err != nil {
    log.Fatal("Failed to write first message:", err)
}
_, err = aliceThinClient.SendChannelQueryAwaitReply(ctx, aliceChannelID, writeReply1.SendMessagePayload, destNode, destQueue, aliceChannelID)
if err != nil {
    log.Fatal("Failed to send first message:", err)
}

// 3. Alice writes the second message to the channel
aliceMessage2 := []byte("Second message from Alice")
writeReply2, err := aliceThinClient.WriteChannel(ctx, aliceChannelID, aliceMessage2)
if err != nil {
    log.Fatal("Failed to write second message:", err)
}
_, err = aliceThinClient.SendChannelQueryAwaitReply(ctx, aliceChannelID, writeReply2.SendMessagePayload, destNode, destQueue, aliceChannelID)
if err != nil {
    log.Fatal("Failed to send first message:", err)
}

// 4. Bob creates a read channel with the readcap from Alice
bobChannelID, err := bobThinClient.CreateReadChannel(ctx, readCap)
if err != nil {
    log.Fatal("Failed to create read channel:", err)
}

// 5. Bob reads the first message from the channel
readReply1, err := bobThinClient.ReadChannel(ctx, bobChannelID, nil, nil)
if err != nil {
    log.Fatal("Failed to read first message:", err)
}
_, err = bobThinClient.SendChannelQueryAwaitReply(ctx, bobChannelID, readReply1.SendMessagePayload, destNode, destQueue, bobChannelID)
if err != nil {
    log.Fatal("Failed to send first message:", err)
}

// 6. Bob closes the read channel
err = bobThinClient.CloseChannel(ctx, bobChannelID)
if err != nil {
    log.Fatal("Failed to close channel:", err)
}

// 7. Bob resumes the read channel
resumedBobChannelID, err := bobThinClient.ResumeReadChannel(ctx, readCap, readReply1.NextMessageIndex, readReply1.ReplyIndex)
if err != nil {
    log.Fatal("Failed to resume read channel:", err)
}

// 8. Bob reads the second message from the channel
readReply2, err := bobThinClient.ReadChannel(ctx, resumedBobChannelID, nil, nil)
if err != nil {
    log.Fatal("Failed to read second message:", err)
}
_, err = bobThinClient.SendChannelQueryAwaitReply(ctx, resumedBobChannelID, readReply2.SendMessagePayload, destNode, destQueue, bobChannelID)
if err != nil {
    log.Fatal("Failed to send second message:", err)
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
{{< /tab >}}
{{< /tabpane >}}


#### Write Channel Resumption After Preparing an Unsent Write Query

1. Alice creates a write channel
2. Alice prepares her write query
3. Alice closes the write channel
4. Alice resumes the write channel
5. Alice sends the write query
6. Bob creates a read channel
7. Bob reads the message from the channel

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// 1. Alice creates a write channel
aliceChannelID, readCap, writeCap, nextMessageIndex, err :=
    aliceThinClient.CreateWriteChannel(ctx)
if err != nil {
    log.Fatal("Failed to create write channel:", err)
}

// 2. Alice prepares her write query
aliceMessage := []byte("Message from Alice")
writeReply, err := aliceThinClient.WriteChannel(ctx, aliceChannelID, aliceMessage)
if err != nil {
    log.Fatal("Failed to prepare write:", err)
}

// 3. Alice closes the write channel
err = aliceThinClient.CloseChannel(ctx, aliceChannelID)
if err != nil {
    log.Fatal("Failed to close channel:", err)
}

// 4. Alice resumes the write channel
resumedChannelID, err := aliceThinClient.ResumeWriteChannel(ctx, writeCap, writeReply.NextMessageIndex)
if err != nil {
    log.Fatal("Failed to resume write channel:", err)
}

// 5. Alice sends the write query
destNode, destQueue, err := aliceThinClient.GetCourierDestination()
if err != nil {
    log.Fatal("Failed to get courier destination:", err)
}
messageID := aliceThinClient.NewMessageID()
_, err = aliceThinClient.SendChannelQueryAwaitReply(ctx, resumedChannelID,
    writeReply.SendMessagePayload, destNode, destQueue, messageID)
if err != nil {
    log.Fatal("Failed to send message:", err)
}

// 6. Bob creates a read channel
bobChannelID, err := bobThinClient.CreateReadChannel(ctx, readCap)
if err != nil {
    log.Fatal("Failed to create read channel:", err)
}

// 7. Bob reads the message from the channel
readReply, err := bobThinClient.ReadChannel(ctx, bobChannelID, nil, nil)
if err != nil {
    log.Fatal("Failed to read message:", err)
}

bobMessageID := bobThinClient.NewMessageID()
readPayload, err := bobThinClient.SendChannelQueryAwaitReply(ctx, bobChannelID,
    readReply.SendMessagePayload, destNode, destQueue, bobMessageID)
if err != nil {
    log.Fatal("Failed to retrieve message:", err)
}

// Verify the message content matches
if bytes.Equal(aliceMessage, readPayload) {
    log.Println("Bob: Successfully received and verified message")
}

// Clean up channels
err = aliceThinClient.CloseChannel(ctx, resumedChannelID)
if err != nil {
    log.Fatal("Failed to close channel:", err)
}

err = bobThinClient.CloseChannel(ctx, bobChannelID)
if err != nil {
    log.Fatal("Failed to close channel:", err)
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
{{< /tab >}}
{{< /tabpane >}}

#### Read Channel Resumption After Preparing an Unsent Read Query

1. Alice creates a write channel
2. Alice writes the first message to the channel
3. Bob creates a read channel with the readcap from Alice
4. Bob prepares his read query
5. Bob closes the read channel
6. Bob resumes the read channel
7. Bob sends the read query and await reply

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// 1. Alice creates a write channel
aliceChannelID, readCap, writeCap, nextMessageIndex, err := aliceThinClient.CreateWriteChannel(ctx)
if err != nil {
    log.Fatal("Failed to create write channel:", err)
}

// 2. Alice writes the first message to the channel
aliceMessage := []byte("Message from Alice")
writeReply, err := aliceThinClient.WriteChannel(ctx, aliceChannelID, aliceMessage)
if err != nil {
    log.Fatal("Failed to write message:", err)
}
_, err = aliceThinClient.SendChannelQueryAwaitReply(ctx, aliceChannelID, writeReply.SendMessagePayload, destNode, destQueue, aliceChannelID)
if err != nil {
    log.Fatal("Failed to send message:", err)
}

// 3. Bob creates a read channel with the readcap from Alice
bobChannelID, err := bobThinClient.CreateReadChannel(ctx, readCap)
if err != nil {
    log.Fatal("Failed to create read channel:", err)
}

// 4. Bob prepares his read query
readReply, err := bobThinClient.ReadChannel(ctx, bobChannelID, nil, nil)
if err != nil {
    log.Fatal("Failed to prepare read:", err)
}

// 5. Bob closes the read channel
err = bobThinClient.CloseChannel(ctx, bobChannelID)
if err != nil {
    log.Fatal("Failed to close channel:", err)
}

// 6. Bob resumes the read channel
resumedBobChannelID, err := bobThinClient.ResumeReadChannel(ctx, readCap, readReply.NextMessageIndex, readReply.ReplyIndex)
if err != nil {
    log.Fatal("Failed to resume read channel:", err)
}

// 7. Bob sends the read query and await reply
readPayload, err := bobThinClient.SendChannelQueryAwaitReply(ctx, resumedBobChannelID, readReply.SendMessagePayload, destNode, destQueue, bobMessageID)
if err != nil {
    log.Fatal("Failed to retrieve message:", err)
}

// Verify the message content matches
if bytes.Equal(aliceMessage, readPayload) {
    log.Println("Bob: Successfully received and verified message")
}

// Clean up channels
err = aliceThinClient.CloseChannel(ctx, aliceChannelID)
if err != nil {
    log.Fatal("Failed to close channel:", err)
}

err = bobThinClient.CloseChannel(ctx, resumedBobChannelID)
if err != nil {
    log.Fatal("Failed to close channel:", err)
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
{{< /tab >}}
{{< /tabpane >}}
