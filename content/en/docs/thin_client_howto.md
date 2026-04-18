---
title:
linkTitle: "Thin Client How-to Guide"
description: "Task-oriented guides for using the Katzenpost thin client API"
categories: [""]
tags: [""]
author: []
version: 0
draft: false
slug: "/thin_client_howto/"
---

# Thin Client How-to Guide

This guide shows how to accomplish specific tasks with the Katzenpost
thin client. Each section is self-contained: find the task you need
and follow the steps.

For the complete API reference, see
[Thin Client API Reference](/docs/thin_client_api_reference/).
For conceptual background on Pigeonhole, see
[Understanding Pigeonhole](/docs/pigeonhole_explained/).

### Table of Contents

| Section | Description |
|---------|-------------|
| [Connect to the daemon and handle events](#how-to-connect-to-the-daemon-and-handle-events) | Establish a connection and process events |
| [Discover network services](#how-to-discover-network-services-via-the-pki-document) | Find services in the PKI document |
| [Send a message to a mixnet service](#how-to-send-a-message-to-a-mixnet-service) | Echo ping and other non-Pigeonhole services |
| [Create a Pigeonhole channel](#how-to-create-a-pigeonhole-channel) | Generate a stream with write/read capabilities |
| [Write a message](#how-to-write-a-message-to-a-pigeonhole-channel) | Encrypt and send a write to a stream |
| [Read a message](#how-to-read-a-message-from-a-pigeonhole-channel) | Retrieve and decrypt a message from a stream |
| [Delete messages with tombstones](#how-to-delete-messages-with-tombstones) | Tombstone one or more boxes |
| [Send to one channel atomically](#how-to-send-to-one-channel-atomically-via-copy-command) | Single-destination copy command |
| [Send to multiple channels atomically](#how-to-send-to-multiple-channels-atomically) | Multi-destination copy command |
| [Multi-call buffer passing](#how-to-handle-multi-call-buffer-passing-for-large-copy-streams) | Incremental copy streams with crash recovery |
| [Tombstone a range via copy stream](#how-to-tombstone-a-range-via-copy-stream) | Atomic tombstoning through a courier |
| [Cancel in-flight operations](#how-to-cancel-in-flight-operations) | Cancel individual operations or stop all at once |
| [Handle daemon disconnects](#how-to-handle-daemon-disconnects-and-restarts) | Automatic reconnection and request replay |

---

## How to connect to the daemon and handle events

Connect to the kpclientd daemon and set up event handling:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
cfg, err := thin.LoadFile("thinclient.toml")
if err != nil {
    log.Fatal(err)
}

logging := &config.Logging{Level: "INFO"}
client := thin.NewThinClient(cfg, logging)

err = client.Dial()
if err != nil {
    log.Fatal(err)
}
defer client.Close()

// Listen for events
eventCh := client.EventSink()
defer client.StopEventSink(eventCh)

for ev := range eventCh {
    switch v := ev.(type) {
    case *thin.ConnectionStatusEvent:
        fmt.Printf("Connected: %v\n", v.IsConnected)
    case *thin.NewDocumentEvent:
        fmt.Println("New PKI document received")
    case *thin.MessageReplyEvent:
        fmt.Printf("Reply received for SURB %x\n", v.SURBID)
    }
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let config = Config::new("thinclient.toml")?;
let client = ThinClient::new(config).await?;

// Listen for events
let mut event_rx = client.event_sink();
tokio::spawn(async move {
    while let Some(event) = event_rx.recv().await {
        // Process events
        println!("Event: {:?}", event);
    }
});

// ... do work ...

client.stop().await;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def on_connection_status(event):
    print(f"Connected: {event.get('is_connected')}")

async def on_new_document(event):
    print("New PKI document received")

async def on_message_reply(event):
    print(f"Reply received")

config = Config("thinclient.toml")
config.on_connection_status = on_connection_status
config.on_new_pki_document = on_new_document
config.on_message_reply = on_message_reply

client = ThinClient(config)
loop = asyncio.get_running_loop()
await client.start(loop)

# ... do work ...

client.stop()
{{< /tab >}}
{{< /tabpane >}}

---

## How to discover network services via the PKI document

**NOTE** that this isn't necessary for using the Pigeonhole protocol
because `kpclientd` does `courier` service discovery automatically.

The PKI document lists all available mixnet services. Use
`GetService` to get a random instance of a named service:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
doc := client.PKIDocument()
if doc == nil {
    log.Fatal("No PKI document available")
}

// Get a random echo service
desc, err := client.GetService("echo")
if err != nil {
    log.Fatal(err)
}

// Use desc.MixDescriptor.IdentityKey and desc.RecipientQueueID
// as the destination for SendMessage
destNode, destQueue := desc.ToDestination()
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let doc = client.pki_document().await?;

// Get a random echo service
let desc = client.get_service("echo").await?;

// Use the destination for send_message
let (dest_node, dest_queue) = desc.to_destination();
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
doc = client.pki_document()
if doc is None:
    raise Exception("No PKI document available")

# Get a random echo service
desc = client.get_service("echo")

# Use the destination for send_message
dest_node, dest_queue = desc.to_destination()
{{< /tab >}}
{{< /tabpane >}}

---

## How to send a message to a mixnet service

**NOTE** that this API call is NOT used with the Pigeonhole protocol.
However it is still useful for writing other protocols and proving the
`echo` service.


Use `BlockingSendMessage` for simple request-response interactions
with non-Pigeonhole services (like the echo service):

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
desc, err := client.GetService("echo")
if err != nil {
    log.Fatal(err)
}

destNode, destQueue := desc.ToDestination()

ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

reply, err := client.BlockingSendMessage(ctx, []byte("hello mixnet"), destNode, destQueue)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Reply: %s\n", reply)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let desc = client.get_service("echo").await?;
let (dest_node, dest_queue) = desc.to_destination();

let reply = client.blocking_send_message(
    b"hello mixnet",
    dest_node,
    dest_queue,
    std::time::Duration::from_secs(30),
).await?;
println!("Reply: {:?}", reply);
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
desc = client.get_service("echo")
dest_node, dest_queue = desc.to_destination()

reply = await client.blocking_send_message(
    b"hello mixnet", dest_node, dest_queue, timeout_seconds=30.0
)
print(f"Reply: {reply}")
{{< /tab >}}
{{< /tabpane >}}

---

## How to create a Pigeonhole channel

*NOTE* that this does NOT produce any network traffic.
It's a local cryptographic operation only.

A Pigeonhole channel (stream) is created from a 32-byte random seed.
The writer keeps the write cap; the reader receives the read cap and
first index out-of-band.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
seed := make([]byte, 32)
_, err := rand.Reader.Read(seed)
if err != nil {
    log.Fatal(err)
}

writeCap, readCap, firstIndex, err := client.NewKeypair(seed)
if err != nil {
    log.Fatal(err)
}

// Writer keeps: writeCap, firstIndex
// Share with reader out-of-band: readCap, firstIndex
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let seed: [u8; 32] = rand::random();
let result = client.new_keypair(&seed).await?;

// Writer keeps: result.write_cap, result.first_index
// Share with reader out-of-band: result.read_cap, result.first_index
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
import os
seed = os.urandom(32)
result = await client.new_keypair(seed)

# Writer keeps: result.write_cap, result.first_index
# Share with reader out-of-band: result.read_cap, result.first_index
{{< /tab >}}
{{< /tabpane >}}

---

## How to write a message to a Pigeonhole channel

Writing is a two-step process: encrypt the message, then send it via
ARQ.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Encrypt the message
ciphertext, envDesc, envHash, nextIndex, err := client.EncryptWrite(
    []byte("hello"), writeCap, currentIndex,
)
if err != nil {
    log.Fatal(err)
}

// Send via ARQ (blocks until acknowledged)
_, err = client.StartResendingEncryptedMessage(
    nil,       // readCap (nil for writes)
    writeCap,
    nil,       // messageBoxIndex (nil for writes)
    nil,       // replyIndex
    envDesc,
    ciphertext,
    envHash,
)
if err != nil {
    log.Fatal(err)
}

// Advance the index for the next write
currentIndex = nextIndex
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Encrypt the message
let result = client.encrypt_write(
    b"hello", &write_cap, &current_index,
).await?;

// Send via ARQ (blocks until acknowledged)
client.start_resending_encrypted_message(
    None,                           // read_cap (None for writes)
    Some(&write_cap),
    None,                           // message_box_index
    None,                           // reply_index
    &result.envelope_descriptor,
    &result.message_ciphertext,
    &result.envelope_hash,
).await?;

// Advance the index for the next write
current_index = result.next_message_box_index;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Encrypt the message
result = await client.encrypt_write(b"hello", write_cap, current_index)

# Send via ARQ (blocks until acknowledged)
await client.start_resending_encrypted_message(
    read_cap=None,
    write_cap=write_cap,
    next_message_index=None,
    reply_index=None,
    envelope_descriptor=result.envelope_descriptor,
    message_ciphertext=result.message_ciphertext,
    envelope_hash=result.envelope_hash,
)

# Advance the index for the next write
current_index = result.next_message_box_index
{{< /tab >}}
{{< /tabpane >}}

---

## How to read a message from a Pigeonhole channel

Reading is also two steps: encrypt a read request, then send it via
ARQ. The reply contains the plaintext.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Encrypt a read request
ciphertext, envDesc, envHash, nextIndex, err := client.EncryptRead(
    readCap, currentIndex,
)
if err != nil {
    log.Fatal(err)
}

// Send via ARQ (blocks until the message is retrieved)
result, err := client.StartResendingEncryptedMessage(
    readCap,
    nil,       // writeCap (nil for reads)
    nil,       // messageBoxIndex
    nil,       // replyIndex
    envDesc,
    ciphertext,
    envHash,
)
if err != nil {
    log.Fatal(err)
}

plaintext := result.Plaintext
// Advance the index for the next read
currentIndex = nextIndex
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Encrypt a read request
let read_result = client.encrypt_read(&read_cap, &current_index).await?;

// Send via ARQ (blocks until the message is retrieved)
let result = client.start_resending_encrypted_message(
    Some(&read_cap),
    None,                                    // write_cap (None for reads)
    None,                                    // message_box_index
    None,                                    // reply_index
    &read_result.envelope_descriptor,
    &read_result.message_ciphertext,
    &read_result.envelope_hash,
).await?;

let plaintext = result.plaintext;
// Advance the index for the next read
current_index = read_result.next_message_box_index;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Encrypt a read request
read_result = await client.encrypt_read(read_cap, current_index)

# Send via ARQ (blocks until the message is retrieved)
plaintext = await client.start_resending_encrypted_message(
    read_cap=read_cap,
    write_cap=None,
    next_message_index=None,
    reply_index=None,
    envelope_descriptor=read_result.envelope_descriptor,
    message_ciphertext=read_result.message_ciphertext,
    envelope_hash=read_result.envelope_hash,
)

# Advance the index for the next read
current_index = read_result.next_message_box_index
{{< /tab >}}
{{< /tabpane >}}

---

## How to delete messages with tombstones

Use `TombstoneRange` to create tombstone envelopes, then send each
one via `StartResendingEncryptedMessage`. To tombstone a single box,
use `maxCount=1`.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Create tombstone envelopes for 5 boxes
result, err := client.TombstoneRange(writeCap, startIndex, 5)
if err != nil {
    log.Fatal(err)
}

// Send each tombstone
for _, envelope := range result.Envelopes {
    _, err = client.StartResendingEncryptedMessage(
        nil, writeCap, nil, nil,
        envelope.EnvelopeDescriptor,
        envelope.MessageCiphertext,
        envelope.EnvelopeHash,
    )
    if err != nil {
        log.Fatal(err)
    }
}
// result.Next is the index after the last tombstoned box
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create tombstone envelopes for 5 boxes
let result = client.tombstone_range(&write_cap, &start_index, 5).await;

// Send each tombstone
for envelope in &result.envelopes {
    client.start_resending_encrypted_message(
        None,
        Some(&write_cap),
        None,
        None,
        &envelope.envelope_descriptor,
        &envelope.message_ciphertext,
        &envelope.envelope_hash,
    ).await?;
}
// result.next is the index after the last tombstoned box
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Create tombstone envelopes for 5 boxes
result = await client.tombstone_range(write_cap, start_index, 5)

# Send each tombstone
for envelope in result.envelopes:
    await client.start_resending_encrypted_message(
        read_cap=None,
        write_cap=write_cap,
        next_message_index=None,
        reply_index=None,
        envelope_descriptor=envelope.envelope_descriptor,
        message_ciphertext=envelope.message_ciphertext,
        envelope_hash=envelope.envelope_hash,
    )
# result.next is the index after the last tombstoned box
{{< /tab >}}
{{< /tabpane >}}

---

## How to send to one channel atomically via copy command

A copy command writes data to a destination channel atomically via a
courier. The steps are:

1. Create a temporary channel and a destination channel.
2. Pack the payload into copy stream elements.
3. Write each element to the temporary channel.
4. Send a copy command referencing the temporary channel.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Create destination channel
destSeed := make([]byte, 32)
rand.Reader.Read(destSeed)
destWriteCap, destReadCap, destFirstIndex, err := client.NewKeypair(destSeed)
if err != nil {
    log.Fatal(err)
}

// Create temporary channel
tempSeed := make([]byte, 32)
rand.Reader.Read(tempSeed)
tempWriteCap, _, tempFirstIndex, err := client.NewKeypair(tempSeed)
if err != nil {
    log.Fatal(err)
}

// Pack payload into copy stream elements
envelopes, _, err := client.CreateCourierEnvelopesFromPayload(
    payload, destWriteCap, destFirstIndex,
    true,  // isStart
    true,  // isLast
)
if err != nil {
    log.Fatal(err)
}

// Write each element to the temporary channel
tempIndex := tempFirstIndex
for _, chunk := range envelopes {
    ciphertext, envDesc, envHash, nextIdx, err := client.EncryptWrite(
        chunk, tempWriteCap, tempIndex,
    )
    if err != nil {
        log.Fatal(err)
    }
    _, err = client.StartResendingEncryptedMessage(
        nil, tempWriteCap, nil, nil, envDesc, ciphertext, envHash,
    )
    if err != nil {
        log.Fatal(err)
    }
    tempIndex = nextIdx
}

// Send the copy command (blocks until courier acknowledges)
err = client.StartResendingCopyCommand(tempWriteCap)
if err != nil {
    log.Fatal(err)
}

// Share destReadCap and destFirstIndex with the reader
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create destination channel
let dest_seed: [u8; 32] = rand::random();
let dest = client.new_keypair(&dest_seed).await?;

// Create temporary channel
let temp_seed: [u8; 32] = rand::random();
let temp = client.new_keypair(&temp_seed).await?;

// Pack payload into copy stream elements
let envelopes_result = client.create_courier_envelopes_from_payload(
    &payload, &dest.write_cap, &dest.first_index,
    true,  // is_start
    true,  // is_last
).await?;

// Write each element to the temporary channel
let mut temp_index = temp.first_index.clone();
for chunk in &envelopes_result.envelopes {
    let write_result = client.encrypt_write(
        chunk, &temp.write_cap, &temp_index,
    ).await?;
    client.start_resending_encrypted_message(
        None, Some(&temp.write_cap), None, None,
        &write_result.envelope_descriptor,
        &write_result.message_ciphertext,
        &write_result.envelope_hash,
    ).await?;
    temp_index = write_result.next_message_box_index;
}

// Send the copy command (blocks until courier acknowledges)
client.start_resending_copy_command(&temp.write_cap, None, None).await?;

// Share dest.read_cap and dest.first_index with the reader
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
import os

# Create destination channel
dest_seed = os.urandom(32)
dest = await client.new_keypair(dest_seed)

# Create temporary channel
temp_seed = os.urandom(32)
temp = await client.new_keypair(temp_seed)

# Pack payload into copy stream elements
envelopes_result = await client.create_courier_envelopes_from_payload(
    payload, dest.write_cap, dest.first_index,
    is_start=True,
    is_last=True,
)

# Write each element to the temporary channel
temp_index = temp.first_index
for chunk in envelopes_result.envelopes:
    write_result = await client.encrypt_write(chunk, temp.write_cap, temp_index)
    await client.start_resending_encrypted_message(
        read_cap=None, write_cap=temp.write_cap,
        next_message_index=None, reply_index=None,
        envelope_descriptor=write_result.envelope_descriptor,
        message_ciphertext=write_result.message_ciphertext,
        envelope_hash=write_result.envelope_hash,
    )
    temp_index = write_result.next_message_box_index

# Send the copy command (blocks until courier acknowledges)
await client.start_resending_copy_command(temp.write_cap)

# Share dest.read_cap and dest.first_index with the reader
{{< /tab >}}
{{< /tabpane >}}

---

## How to send to multiple channels atomically

Use `CreateCourierEnvelopesFromMultiPayload` to pack payloads for
different destinations into a single copy stream efficiently:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Create destination channels
dest1WriteCap, dest1ReadCap, dest1Index, _ := client.NewKeypair(seed1)
dest2WriteCap, dest2ReadCap, dest2Index, _ := client.NewKeypair(seed2)

// Create temporary channel
tempWriteCap, _, tempFirstIndex, _ := client.NewKeypair(tempSeed)

// Pack multiple payloads
destinations := []thin.DestinationPayload{
    {Payload: payload1, WriteCap: dest1WriteCap, StartIndex: dest1Index},
    {Payload: payload2, WriteCap: dest2WriteCap, StartIndex: dest2Index},
}

result, err := client.CreateCourierEnvelopesFromMultiPayload(
    destinations,
    true,  // isStart
    true,  // isLast
    nil,   // buffer (nil for first call)
)
if err != nil {
    log.Fatal(err)
}

// Write envelopes to temporary channel
tempIndex := tempFirstIndex
for _, chunk := range result.Envelopes {
    ciphertext, envDesc, envHash, nextIdx, err := client.EncryptWrite(
        chunk, tempWriteCap, tempIndex,
    )
    if err != nil {
        log.Fatal(err)
    }
    _, err = client.StartResendingEncryptedMessage(
        nil, tempWriteCap, nil, nil, envDesc, ciphertext, envHash,
    )
    if err != nil {
        log.Fatal(err)
    }
    tempIndex = nextIdx
}

// Send copy command
err = client.StartResendingCopyCommand(tempWriteCap)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create destination channels
let dest1 = client.new_keypair(&seed1).await?;
let dest2 = client.new_keypair(&seed2).await?;

// Create temporary channel
let temp = client.new_keypair(&temp_seed).await?;

// Pack multiple payloads
let destinations = vec![
    (&payload1[..], &dest1.write_cap[..], &dest1.first_index[..]),
    (&payload2[..], &dest2.write_cap[..], &dest2.first_index[..]),
];

let result = client.create_courier_envelopes_from_multi_payload(
    destinations,
    true,  // is_start
    true,  // is_last
    None,  // buffer (None for first call)
).await?;

// Write envelopes to temporary channel
let mut temp_index = temp.first_index.clone();
for chunk in &result.envelopes {
    let write_result = client.encrypt_write(
        chunk, &temp.write_cap, &temp_index,
    ).await?;
    client.start_resending_encrypted_message(
        None, Some(&temp.write_cap), None, None,
        &write_result.envelope_descriptor,
        &write_result.message_ciphertext,
        &write_result.envelope_hash,
    ).await?;
    temp_index = write_result.next_message_box_index;
}

// Send copy command
client.start_resending_copy_command(&temp.write_cap, None, None).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Create destination channels
dest1 = await client.new_keypair(seed1)
dest2 = await client.new_keypair(seed2)

# Create temporary channel
temp = await client.new_keypair(temp_seed)

# Pack multiple payloads
destinations = [
    {"payload": payload1, "write_cap": dest1.write_cap, "start_index": dest1.first_index},
    {"payload": payload2, "write_cap": dest2.write_cap, "start_index": dest2.first_index},
]

result = await client.create_courier_envelopes_from_multi_payload(
    destinations,
    is_start=True,
    is_last=True,
    buffer=None,
)

# Write envelopes to temporary channel
temp_index = temp.first_index
for chunk in result.envelopes:
    write_result = await client.encrypt_write(chunk, temp.write_cap, temp_index)
    await client.start_resending_encrypted_message(
        read_cap=None, write_cap=temp.write_cap,
        next_message_index=None, reply_index=None,
        envelope_descriptor=write_result.envelope_descriptor,
        message_ciphertext=write_result.message_ciphertext,
        envelope_hash=write_result.envelope_hash,
    )
    temp_index = write_result.next_message_box_index

# Send copy command
await client.start_resending_copy_command(temp.write_cap)
{{< /tab >}}
{{< /tabpane >}}

---

## How to handle multi-call buffer passing for large copy streams

When building a copy stream across multiple calls (because you have
more data than fits in a single call, or data arrives incrementally),
pass the buffer from each result to the next call:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
var buffer []byte // nil on first call

// First batch of destinations
result1, err := client.CreateCourierEnvelopesFromMultiPayload(
    batch1Destinations,
    true,   // isStart (first call)
    false,  // isLast (more calls coming)
    buffer,
)
if err != nil {
    log.Fatal(err)
}
// Write result1.Envelopes to temp channel...
buffer = result1.Buffer // save for next call

// Persist buffer to disk for crash recovery
saveState(buffer)

// Second batch (final)
result2, err := client.CreateCourierEnvelopesFromMultiPayload(
    batch2Destinations,
    false,  // isStart (not the first call)
    true,   // isLast (final call)
    buffer,
)
if err != nil {
    log.Fatal(err)
}
// Write result2.Envelopes to temp channel...

// On crash recovery, reload buffer from disk and continue
// with isStart=false
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let mut buffer: Option<Vec<u8>> = None; // None on first call

// First batch
let result1 = client.create_courier_envelopes_from_multi_payload(
    batch1_destinations,
    true,   // is_start
    false,  // is_last
    buffer,
).await?;
// Write result1.envelopes to temp channel...
buffer = result1.buffer; // save for next call

// Persist buffer to disk for crash recovery
save_state(&buffer);

// Second batch (final)
let result2 = client.create_courier_envelopes_from_multi_payload(
    batch2_destinations,
    false,  // is_start
    true,   // is_last
    buffer,
).await?;
// Write result2.envelopes to temp channel...
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
buffer = None  # None on first call

# First batch
result1 = await client.create_courier_envelopes_from_multi_payload(
    batch1_destinations,
    is_start=True,   # first call
    is_last=False,   # more calls coming
    buffer=buffer,
)
# Write result1.envelopes to temp channel...
buffer = result1.buffer  # save for next call

# Persist buffer to disk for crash recovery
save_state(buffer)

# Second batch (final)
result2 = await client.create_courier_envelopes_from_multi_payload(
    batch2_destinations,
    is_start=False,  # not the first call
    is_last=True,    # final call
    buffer=buffer,
)
# Write result2.envelopes to temp channel...
{{< /tab >}}
{{< /tabpane >}}

---

## How to tombstone a range via copy stream

Use `CreateCourierEnvelopesFromTombstoneRange` to atomically
tombstone boxes as part of a copy command. The courier performs the
tombstoning, so it either all succeeds or none of it is visible.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
tempWriteCap, _, tempFirstIndex, _ := client.NewKeypair(tempSeed)

// Create tombstone copy stream elements
envelopes, nextBuffer, nextDestIndex, err := client.CreateCourierEnvelopesFromTombstoneRange(
    destWriteCap,
    destStartIndex,
    10,     // tombstone 10 boxes
    true,   // isStart
    true,   // isLast
    nil,    // buffer
)
if err != nil {
    log.Fatal(err)
}

// Write to temporary channel
tempIndex := tempFirstIndex
for _, chunk := range envelopes {
    ciphertext, envDesc, envHash, nextIdx, err := client.EncryptWrite(
        chunk, tempWriteCap, tempIndex,
    )
    if err != nil {
        log.Fatal(err)
    }
    _, err = client.StartResendingEncryptedMessage(
        nil, tempWriteCap, nil, nil, envDesc, ciphertext, envHash,
    )
    if err != nil {
        log.Fatal(err)
    }
    tempIndex = nextIdx
}

// Send copy command
err = client.StartResendingCopyCommand(tempWriteCap)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let temp = client.new_keypair(&temp_seed).await?;

// Create tombstone copy stream elements
let result = client.create_courier_envelopes_from_tombstone_range(
    &dest_write_cap,
    &dest_start_index,
    10,     // tombstone 10 boxes
    true,   // is_start
    true,   // is_last
    None,   // buffer
).await?;

// Write to temporary channel
let mut temp_index = temp.first_index.clone();
for chunk in &result.envelopes {
    let write_result = client.encrypt_write(
        chunk, &temp.write_cap, &temp_index,
    ).await?;
    client.start_resending_encrypted_message(
        None, Some(&temp.write_cap), None, None,
        &write_result.envelope_descriptor,
        &write_result.message_ciphertext,
        &write_result.envelope_hash,
    ).await?;
    temp_index = write_result.next_message_box_index;
}

// Send copy command
client.start_resending_copy_command(&temp.write_cap, None, None).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
temp = await client.new_keypair(temp_seed)

# Create tombstone copy stream elements
result = await client.create_courier_envelopes_from_tombstone_range(
    dest_write_cap,
    dest_start_index,
    10,              # tombstone 10 boxes
    is_start=True,
    is_last=True,
    buffer=None,
)

# Write to temporary channel
temp_index = temp.first_index
for chunk in result.envelopes:
    write_result = await client.encrypt_write(chunk, temp.write_cap, temp_index)
    await client.start_resending_encrypted_message(
        read_cap=None, write_cap=temp.write_cap,
        next_message_index=None, reply_index=None,
        envelope_descriptor=write_result.envelope_descriptor,
        message_ciphertext=write_result.message_ciphertext,
        envelope_hash=write_result.envelope_hash,
    )
    temp_index = write_result.next_message_box_index

# Send copy command
await client.start_resending_copy_command(temp.write_cap)
{{< /tab >}}
{{< /tabpane >}}

---

## How to cancel in-flight operations

Both `StartResendingEncryptedMessage` and `StartResendingCopyCommand`
block until completion. You can cancel them individually, or stop
everything at once by closing the thin client.

**To cancel a specific operation**, call the corresponding cancel
method from another thread/task:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Cancel an encrypted message operation
err := client.CancelResendingEncryptedMessage(envelopeHash)

// Cancel a copy command (needs blake2b-256 hash of the write cap)
writeCapBytes, _ := tempWriteCap.MarshalBinary()
writeCapHash := blake2b.Sum256(writeCapBytes)
err = client.CancelResendingCopyCommand(&writeCapHash)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Cancel an encrypted message operation
client.cancel_resending_encrypted_message(&envelope_hash).await?;

// Cancel a copy command
use blake2::{Blake2b, Digest};
use digest::consts::U32;
let write_cap_hash: [u8; 32] = Blake2b::<U32>::digest(&temp_write_cap).into();
client.cancel_resending_copy_command(&write_cap_hash).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Cancel an encrypted message operation
await client.cancel_resending_encrypted_message(envelope_hash)

# Cancel a copy command
from hashlib import blake2b
write_cap_hash = blake2b(temp_write_cap, digest_size=32).digest()
await client.cancel_resending_copy_command(write_cap_hash)
{{< /tab >}}
{{< /tabpane >}}

**To stop all in-flight operations at once**, call `Close()` (Go),
`stop()` (Rust), or `stop()` (Python). This shuts down the thin
client entirely -- all blocked callers receive an error, and the
daemon stops all ARQ retransmission loops for this client. This is
useful when your application is shutting down or when you want to
abandon all pending work without cancelling each operation
individually.

---

## How to handle daemon disconnects and restarts

The thin client automatically reconnects when the daemon connection
is lost. It uses an instance token to detect whether it reconnected
to the same daemon or a new one:

- **Same instance token**: The daemon still has its state. No action
  needed.

- **Different instance token**: The daemon is a new process. The thin
  client automatically replays all in-flight
  `StartResendingEncryptedMessage` and `StartResendingCopyCommand`
  operations. Callers blocked on these methods are unaware of the
  disconnect.

Applications do not need to manage reconnection or replay. You can
observe disconnect events to log or update UI state:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
eventCh := client.EventSink()
defer client.StopEventSink(eventCh)

for ev := range eventCh {
    switch v := ev.(type) {
    case *thin.DaemonDisconnectedEvent:
        if v.IsGraceful {
            fmt.Println("Daemon shut down gracefully")
        } else {
            fmt.Printf("Daemon connection lost: %v\n", v.Err)
        }
        // No action needed -- thin client reconnects automatically
        // and replays in-flight requests if the daemon instance changed.
    case *thin.ConnectionStatusEvent:
        fmt.Printf("Connected: %v\n", v.IsConnected)
        // v.InstanceToken identifies the daemon process.
        // The thin client compares this internally on reconnect.
    }
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let config = Config::new("thinclient.toml")?;
// Set disconnect callback during config
config.on_daemon_disconnected = Some(Box::new(|graceful, err_msg| {
    if graceful {
        println!("Daemon shut down gracefully");
    } else {
        println!("Daemon connection lost: {:?}", err_msg);
    }
    // No action needed -- thin client reconnects automatically
    // and replays in-flight requests if the daemon instance changed.
}));
let client = ThinClient::new(config).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def on_daemon_disconnected(event):
    if event.get("is_graceful"):
        print("Daemon shut down gracefully")
    else:
        print(f"Daemon connection lost: {event.get('error')}")
    # No action needed -- thin client reconnects automatically
    # and replays in-flight requests if the daemon instance changed.

async def on_connection_status(event):
    print(f"Connected: {event['is_connected']}")
    # event contains 'instance_token' identifying the daemon process.
    # The thin client compares this internally on reconnect.

config = Config(
    "thinclient.toml",
    on_daemon_disconnected=on_daemon_disconnected,
    on_connection_status=on_connection_status,
)
client = ThinClient(config)
{{< /tab >}}
{{< /tabpane >}}

If the thin client is disconnected when you cancel an operation, the
cancel just removes it from in-flight tracking -- it will not be
replayed on reconnect:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Safe to call while disconnected -- removes from tracking,
// no message sent to daemon since there is no connection.
err := client.CancelResendingEncryptedMessage(envelopeHash)
err = client.CancelResendingCopyCommand(&writeCapHash)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Safe to call while disconnected -- removes from tracking,
// no message sent to daemon since there is no connection.
client.cancel_resending_encrypted_message(&envelope_hash).await?;
client.cancel_resending_copy_command(&write_cap_hash).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Safe to call while disconnected -- removes from tracking,
# no message sent to daemon since there is no connection.
await client.cancel_resending_encrypted_message(envelope_hash)
await client.cancel_resending_copy_command(write_cap_hash)
{{< /tab >}}
{{< /tabpane >}}

To terminate the thin client entirely (all blocked callers receive an
error, daemon disconnects never kill the thin client):

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
err := client.Close()
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
client.stop().await;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
client.stop()
{{< /tab >}}
{{< /tabpane >}}
