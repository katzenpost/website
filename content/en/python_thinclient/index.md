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

# Table of Contents

* [katzenpost\_thinclient](#katzenpost_thinclient)
  * [ServiceDescriptor](#katzenpost_thinclient.ServiceDescriptor)
  * [Config](#katzenpost_thinclient.Config)
  * [ThinClient](#katzenpost_thinclient.ThinClient)
    * [start](#katzenpost_thinclient.ThinClient.start)
    * [stop](#katzenpost_thinclient.ThinClient.stop)
    * [pki\_document](#katzenpost_thinclient.ThinClient.pki_document)
    * [get\_services](#katzenpost_thinclient.ThinClient.get_services)
    * [get\_service](#katzenpost_thinclient.ThinClient.get_service)
    * [new\_message\_id](#katzenpost_thinclient.ThinClient.new_message_id)
    * [new\_surb\_id](#katzenpost_thinclient.ThinClient.new_surb_id)
    * [send\_message\_without\_reply](#katzenpost_thinclient.ThinClient.send_message_without_reply)
    * [send\_message](#katzenpost_thinclient.ThinClient.send_message)
    * [send\_reliable\_message](#katzenpost_thinclient.ThinClient.send_reliable_message)
    * [pretty\_print\_pki\_doc](#katzenpost_thinclient.ThinClient.pretty_print_pki_doc)
    * [await\_message\_reply](#katzenpost_thinclient.ThinClient.await_message_reply)

<a id="katzenpost_thinclient"></a>

# katzenpost\_thinclient

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

