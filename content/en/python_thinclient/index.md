---
title: "Katzenpost Python Thin Client"
linkTitle: "Katzenpost Python Thin Client"
url: "docs/python_thin_client.html"
description: ""
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
---

<!-- spacer -->

&nbsp;

&nbsp;


## Katzenpost Python Thin Client

This module provides a minimal async Python client for communicating with the
Katzenpost client daemon over an abstract Unix domain socket. It allows
applications to send and receive messages via the mix network by interacting
with the daemon.

The thin client handles:
- Connecting to the local daemon
- Sending messages
- Receiving events and responses from the daemon
- Accessing the current PKI document and service descriptors

All cryptographic operations, including PQ Noise transport, Sphinx
packet construction, and retransmission mechanisms are handled by the
client daemon, and not this thin client library.

For more information, see our client integration guide:
https://katzenpost.network/docs/client_integration/


Usage Example
-------------

```python
import asyncio
from thinclient import ThinClient, Config

def on_message_reply(event):
    print("Got reply:", event)

async def main():
    cfg = Config(on_message_reply=on_message_reply)
    client = ThinClient(cfg)
    loop = asyncio.get_running_loop()
    await client.start(loop)

    service = client.get_service("echo")
    surb_id = client.new_surb_id()
    client.send_message(surb_id, "hello mixnet", *service.to_destination())

    await client.await_message_reply()

asyncio.run(main())
```

<a id="katzenpost_thinclient.ServiceDescriptor"></a>

## ServiceDescriptor Objects

```python
class ServiceDescriptor()
```

ServiceDescriptor describes a mixnet service that you can interact with.

<a id="katzenpost_thinclient.Config"></a>

## Config Objects

```python
class Config()
```

Config is the configuration object for the ThinClient.

<a id="katzenpost_thinclient.ThinClient"></a>

## ThinClient Objects

```python
class ThinClient()
```

Katzenpost thin client knows how to communicate with the Katzenpost client2 daemon
via the abstract unix domain socket.

<a id="katzenpost_thinclient.ThinClient.start"></a>

#### start

```python
async def start(loop)
```

start the thing client, connect to the client daemon,
start our async event processing.

<a id="katzenpost_thinclient.ThinClient.stop"></a>

#### stop

```python
def stop()
```

stop the thin client

<a id="katzenpost_thinclient.ThinClient.pki_document"></a>

#### pki\_document

```python
def pki_document()
```

return our latest copy of the PKI document

<a id="katzenpost_thinclient.ThinClient.get_services"></a>

#### get\_services

```python
def get_services(capability)
```

return a list of services with the given capability string

<a id="katzenpost_thinclient.ThinClient.get_service"></a>

#### get\_service

```python
def get_service(service_name)
```

given a service name, return a service descriptor if one exists.
if more than one service with that name exists then pick one at random.

<a id="katzenpost_thinclient.ThinClient.new_message_id"></a>

#### new\_message\_id

```python
def new_message_id()
```

generate a new message ID

<a id="katzenpost_thinclient.ThinClient.new_surb_id"></a>

#### new\_surb\_id

```python
def new_surb_id()
```

generate a new SURB ID

<a id="katzenpost_thinclient.ThinClient.send_message_without_reply"></a>

#### send\_message\_without\_reply

```python
def send_message_without_reply(payload, dest_node, dest_queue)
```

Send a message without expecting a reply (no SURB).

<a id="katzenpost_thinclient.ThinClient.send_message"></a>

#### send\_message

```python
def send_message(surb_id, payload, dest_node, dest_queue)
```

Send a message with a SURB to allow replies from the recipient.

<a id="katzenpost_thinclient.ThinClient.send_reliable_message"></a>

#### send\_reliable\_message

```python
def send_reliable_message(message_id, payload, dest_node, dest_queue)
```

Send a reliable ARQ message using a message ID to match the reply.

<a id="katzenpost_thinclient.ThinClient.pretty_print_pki_doc"></a>

#### pretty\_print\_pki\_doc

```python
def pretty_print_pki_doc(doc)
```

Pretty-print a parsed PKI document including nodes and topology.

<a id="katzenpost_thinclient.ThinClient.await_message_reply"></a>

#### await\_message\_reply

```python
async def await_message_reply()
```

Wait asynchronously until a message reply is received.

