---
title: "Katzenpost Client Integration Guide"
linkTitle: ""
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
and projects to a Katzenpost mixnet.

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
https://katzenpost.network/docs/specs/connector.html

It can be extended to be used by any language that has a CBOR
serialization library and can talk over TCP or UNIX domain
socket. Currently there are three thin client libraries:

{{< tabpane text=true >}}
{{% tab header="**Go**" %}}
**Source code:** https://github.com/katzenpost/katzenpost/tree/main/client2

**API docs:** https://pkg.go.dev/github.com/katzenpost/katzenpost@v0.0.46/client2/thin

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


**NOTE**: *It might be helpful to new users to use a mixnet that already exists instead of trying to create your own. Please see:*
[How to Use Namenlos Mixnet](/docs/howto_use_namenlos_mixnet/).


## Thin client configuration

The thin client configuration has at most two sections:

1. Callbacks for handling received events.
2. Sphinx Geometry for determining the maximum size of usable payload
   in a Sphinx packet.

NOTE: currently only the golang thin client has the Sphinx geometry in
it's configuration. The other implementations are configured with only
callbacks.

The only use the thin client or application would have for the Sphinx
geometry is to learn the application's maximum payload capacity which
is not the same as the Sphinx packet payload size because of the SURB
which is stored in the payload so that a reply can be received.



## Getting the PKI document from your app

You'll need a view of the mix network in order to send packets. The
PKI (public key infrastructure) document is published by the mix
network's set of directory authorities, and you fetch it from one of
the gateways. This is not unlike <i>Tor</i> and <i>mixminion</i>. The
PKI document updates every epoch, which currenttly is 20 minutes.

The setup process as in the example above will fetch your first
network config and PKI document so you can start interacting with the
network, but you need your client to update the doc as needed.

You can obtain a PKI document using the thin client API:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
import (
    cpki "github.com/katzenpost/katzenpost/core/pki"
)

// PKIDocument returns the current PKI document
func (t *ThinClient) PKIDocument() *cpki.Document {}

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

When creating an app that works over a mixnet, you will need to
interact with <i>mixnet services</i> that are listed in the PKI
document. For example, our mixnet ping CLI tool gets a random echo
service from the PKI document and handles its business using
that information:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
thin := thin.NewThinClient(cfg)
err = thin.Dial()
if err != nil {
    panic(err)
}

desc, err := thin.GetService("echo")
if err != nil {
    panic(err)
}

// handle business here
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
let service_desc = thin_client.get_service(service_name).await?;
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
service_descriptor = thin_client.get_service(doc, service_name)
{{< /tab >}}
{{< /tabpane >}}

The `GetService` is a convenient helper method which searches the PKI
document for the the service name we give it and then selects a random
entry from that set. I don't care which XYZ service I talk to just so
long as I can talk to one of them.

```golang
// ServiceDescriptor describe a mixnet Gateway-side service.
type ServiceDescriptor struct {
	// RecipientQueueID is the service name or queue ID.
	RecipientQueueID []byte
	// Gateway name.
	MixDescriptor *cpki.MixDescriptor
}
```

The result is that you procure a destination mix identity hash and a
destination queue ID so that the mix node routes the message to the
service.

The hash algorithm used is provided by "github.com/katzenpost/hpqc"
("golang.org/x/crypto/blake2b.Sum256")

```golang
func Sum256(data []byte) [blake2b.Size256]byte {}
```

For example:

```golang
    import (
        "github.com/katzenpost/hpqc/hash"
        "github.com/katzenpost/katzenpost/thin"
    )

	thin := thin.NewThinClient(cfg)
	err = thin.Dial()
	if err != nil {
		panic(err)
	}

	desc, err := thin.GetService("echo")
	if err != nil {
		panic(err)
	}
    serviceIdHash := hash.Sum256(desc.MixDescriptor.IdentityKey)
    serviceQueueID := desc.RecipientQueueID
```

As a client you need to be able to gather PKI documents for each epoch
that your packets will be used in. This is important for our Sphinx
based routing protocol because the mix keys used for the mix node's
Sphinx packet decryption are used only for one Epoch and then they
expire. Our PKI document publishes several Epochs worth of future mix
keys so that the upcoming Epoch boundary will not cause any
transmission failures.

## Sending a message

Each send operation that a thin client can do requires you to specify
the payload to be sent and the destination mix node identity hash and
the destination recipient queue identity.

The API by design lets you specify either a SURB ID or a message ID
for the sent message depending on if it's using an ARQ to send
reliably or not. This implies that the application using the thin
client must do it's own book keeping to keep track of which replies
and their associated identities.

The simplest way to send a message is using the `SendMessageWithoutReply` method:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// SendMessageWithoutReply sends a message encapsulated in a Sphinx packet, without any SURB.
// No reply will be possible.
func (t *ThinClient) SendMessageWithoutReply(payload []byte, destNode *[32]byte, destQueue []byte) error

// Example usage:
err := thin.SendMessageWithoutReply(payload, &serviceIdHash, serviceQueueID)
if err != nil {
    panic(err)
}
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
// Send a message without expecting a reply
thin_client.send_message_without_reply(payload, dest_node, dest_queue).await?;
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Send a message without expecting a reply
thin_client.send_message_without_reply(payload, dest_node, dest_queue)
{{< /tab >}}
{{< /tabpane >}}

This method sends a Sphinx packet encapsulating the given payload to
the given destination. No SURB is sent, so no reply can ever be
received. This is a one-way message.

The rest of the message sending methods of the thin client are
variations of this basic send but with some more complexity added. For
example, you can choose to send a message with or without the help of
an ARQ error correction scheme where retransmissions are automatically
sent when the other party doesn't receive your message. Or keep it
minimal and send a message with a SURB in the payload so that the
service can send you a reply. Also as a convenience, our Go API has
blocking and non-blocking method calls for these operations.

The Rust and Python thin client APIs are very similar. Knowledge of
one is easily transferable to another implementation.



## Receiving events and messages

It's worth noting that our Go thin client implementation gives you
an events channel for receiving events from the client daemon, whereas
the Python and Rust thin clients allow you to specify callbacks for
each event type. Both approaches are equivalent to each other.

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
receive:

* ShutdownEvent: This event tells your application that the Katzenpost
  client daemon is shutting down.

* ConnectionStatusEvent: This event notifies your app of a network
  connectvity status change, which is either connected or not
  connected.

* NewPKIDocumentEvent: This event tells encapsulates the new PKI
  document, a view of the network, including a list of network
  services.

* MessageSentEvent: This event tells your app that it's message was
  successfully sent to a gateway node on the mix network.

* MessageReplyEvent: This event encapsulates a reply from a service on
  the mixnet.

* MessageIDGarbageCollected: This event is an ARQ garbage collecton
  event which is used to notify clients so that they can clean up
  their ARQ specific book keeping, if any.



## Conclusion

This is a guide to performing very low level and basic interactions
with mixnet services. Send a message to a mixnet service and receive a
reply. Very basic but also a powerful building block.

In the future we plan on:

* writing various messaging systems and making their client controls
  exposed to the thin client

* writing higher level protocol additions to this thin client API that
  would allow clients to send and receive streams of data. Streaming
  data is useful for a variety of applications where strict datagrams
  may not be as easily useful.
