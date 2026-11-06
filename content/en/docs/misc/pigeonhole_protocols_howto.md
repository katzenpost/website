---
title:
linkTitle: "Pigeonhole Protocols How-to Guide"
description: "How to build an application protocol or a mixnet service with the pigeonhole_protocols library: plain channels, the group chat protocol, and the service framework"
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
slug: "/pigeonhole_protocols_howto/"
url: "docs/pigeonhole_protocols_howto/"
---

# Pigeonhole Protocols How-to Guide

This guide is for building something new on Pigeonhole with the
[pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols)
library, in Go or in Rust. It assumes you have read
[Understanding Pigeonhole](/docs/pigeonhole_explained/). The
[Thin Client How-to Guide](/docs/thin_client_howto/) covers the layer
below: raw boxes over the client daemon.

The code fragments here teach one task at a time and omit imports and
error handling. The programs and tests they are taken from compile and
run in CI, and are linked at the end of each section; when a fragment
and the code disagree, the code is right.

## Which shape is your protocol?

Decide this first. Pigeonhole protocols come in three shapes, and each
has a different right tool.

**One party writes, another reads, once.** Sending a file, publishing a
feed, handing over a result. You do not need a protocol library: write
the data to a channel and give the other party the read capability out
of band. The thin client does this directly; see
[how to create a channel](/docs/thin_client_howto/#how-to-create-a-pigeonhole-channel)
and [how to read back a multi-box payload](/docs/thin_client_howto/#how-to-read-back-a-multi-box-payload).

**Two or more parties talk for a while and both expect what they send to
arrive.** A bot, a bridge, a fetcher that takes requests and streams back
results, a game, anything with a request and a reply. **Use the group
chat protocol.** This is the recommendation for most protocols, and the
rest of this guide explains why and how.

**Anyone should be able to find you and connect.** A service with a
public identity. Use the service framework to be listed in the
directory and reached through a voucher router, and then, once a client
has reached you, carry on in a group as above.

## Why the group chat protocol

The group chat protocol, `katzenqt1`, is what katzenqt and hushphone
speak. It is a set of members who each write to a stream of their own
and read everyone else's. As a base for your own protocol it gives you,
for free:

- **Reliability in both directions.** Writes that must land are retried
  until they do; members acknowledge what they have read; messages
  longer than a box are split and reassembled; files ride as sealed
  attachments.
- **Crash safety.** Every change is saved to the state directory before
  the network work it leads to starts. A client killed at any moment
  and opened again on the same directory carries on, and sends nothing
  twice.
- **A group of two is just a group.** Your protocol starts as two
  parties and gains a third without redesign.
- **Humans can talk to it.** A service that lives in a group is a
  contact in katzenqt. People can join, read, and type at your bot with
  the app they already have.
- **Two implementations that agree.** Go and Rust run the same
  scenarios and the same conformance traces against katzenqt, so a Go
  client and a Rust service interoperate.

Your protocol is then messages inside a group: text lines for requests
and replies, files for anything large. The transport, retries,
persistence and membership are not your problem.

The service framework's own two-way connection also exists, and the
`motd` and `eliza` services use it directly. It is a pair of streams
with send and receive, enough for a request and a reply, and it is what
you have before a client has joined a group. It does not acknowledge,
and a send interrupted midway can lose the next message to that box.
Treat it as the lobby, and move the conversation into a group.

## How to open the group chat client

A client needs a backend, a state directory and a display name. The
backend is the client daemon through its thin client; for tests, an
in-memory Pigeonhole (see [testing without a mixnet](#how-to-test-without-a-mixnet)).

Go:

```go
backend, _ := thinclient.Dial("@katzenpost", "")   // the daemon's socket, and a log file or ""
defer backend.Close()

c, _ := client.Open(ctx, client.Config{StateDir: "state", Name: "alice", Backend: backend})
defer c.Close()

events := c.Subscribe()   // subscribe before reading state, so nothing falls between
```

Rust:

```rust
let backend = Arc::new(ThinClientBackend::dial("@katzenpost").await?);
let c = Client::open(Config { state_dir: "state".into(), name: "alice".into(), ..Default::default() }, backend).await?;
let mut events = c.subscribe();
```

`Open` loads whatever the state directory holds and resumes any work
left under way, so the same call starts a fresh client and restarts an
old one.

Working code: [`go/examples/chat`](https://github.com/katzenpost/pigeonhole_protocols/tree/main/go/examples/chat),
[`rust/examples/chat.rs`](https://github.com/katzenpost/pigeonhole_protocols/blob/main/rust/examples/chat.rs).

## How to connect two parties

One party founds the group and the other joins it with a contact
voucher. The joiner mints the voucher; its code appears in the group's
view once minted; the founder invites that code. The code travels out
of band: in person, over another messenger, or over a service
connection (below).

Go:

```go
// Founder
id, _ := c.Create("fetcher")

// Joiner
id, _ := c.Join("fetcher")
v, _ := c.Chat(id)        // poll or watch events until v.Code != ""
fmt.Println(v.Code)       // hand this to the founder

// Founder, given the code
c.Invite(id, code)
```

Rust:

```rust
let id = c.create("fetcher").await?;          // founder
let id = c.join("fetcher").await?;            // joiner; c.chat(&id).await?.code is the voucher code
c.invite(&id, &code).await?;                  // founder, given the code
```

The group appears as joined on the joiner's side once the invitation
is read, which on the mixnet takes a few minutes. `ChatView.Joined`
says when.

## How to run your protocol inside the group

Send requests as text and watch events for replies. Each event names a
group and the lines added or changed; ask for the lines and act on the
ones that are not yours.

Go:

```go
c.Send(id, `{"fetch":"https://example.org/"}`)

for ev := range events {
    if ev.Err != nil { return ev.Err }           // the client stopped
    lines, _ := c.Lines(ev.Chat, last)           // lines after the last one handled
    for _, l := range lines {
        last = l.ID
        if l.Mine || l.Notice != nil { continue }
        handle(l.From, l.Text)                   // or l.Attachment, via c.FilePath
    }
}
```

Rust:

```rust
c.send(&id, r#"{"fetch":"https://example.org/"}"#).await?;

while let Some(ev) = events.recv().await {
    if let Some(e) = ev.error { return Err(e.into()); }
    for l in c.lines(&ev.chat, Some(last)).await? {
        last = l.line.id;
        if l.mine || l.line.notice.is_some() { continue; }
        handle(&l.from, &l.line.text);           // or l.line.attachment, via c.read_file
    }
}
```

Three habits make this robust:

- **Keep `last` on disk.** Lines are numbered per group and the store
  keeps them, so after a restart you ask for the lines after the last
  one you handled and nothing is replayed or missed. The zulip bridge
  keeps this mark in a file beside its state.
- **Put large things in files.** `SendFile` seals and chunks a file and
  the other side gets an attachment with a path. A text line is for
  what fits in one box; the client splits longer text, but a file is
  the honest form for a payload.
- **Choose a text encoding and stick to it.** JSON or base64 CBOR in a
  line is fine. Members who are people will see it, so a bot that also
  talks to humans should answer plain text to plain text.

Working code: the zulip bridge,
[`rust/src/services/zulip/mod.rs`](https://github.com/katzenpost/pigeonhole_protocols/blob/main/rust/src/services/zulip/mod.rs)
(`to_zulip` reads the group from a mark; `from_zulip` writes into it).

## How to be a service that clients can find

A service has a NIKE keypair; its ID is the hash of the public key, 64
hex digits, and that is what you publish. On start it registers with
voucher routers and advertises a descriptor naming them in the service
directory. A client looks the descriptor up, mints a voucher, seals it
to the service's key and hands it to one of the routers; the service
inducts it, and the two share a two-way connection. The framework does
all of that; you write the handler.

Go, the service:

```go
ph := common.NewThinPigeonhole(thinClient)
key, _ := ps.LoadServiceKey(dataDir)              // generated on first run
adv, _ := discovery.NewAll(ph, key, pollInterval) // every directory in the PKI

svc, _ := ps.NewService(ps.Config{
    Key: key, DataDir: dataDir, DisplayName: "fetcher",
    Advertiser: adv, PollInterval: pollInterval, Log: logger,
}, ph)
fmt.Println(hex.EncodeToString(svc.ID()[:]))

svc.Run(ctx, ps.HandlerFunc(func(ctx context.Context, s *ps.Session) {
    for {
        msg, err := s.Recv(ctx)
        if err != nil { return }
        s.Send(ctx, reply(msg))
    }
}))
```

Go, the client:

```go
ph := common.NewThinPigeonhole(thinClient)
dir, _ := discovery.NewAll(ph, nil, pollInterval)
d, _ := dir.Lookup(ctx, serviceID)
conn, _ := ps.Dial(ctx, ph, d, "fetcher client", pollInterval)
conn.Send(ctx, request)
raw, _ := conn.Recv(ctx)
```

Rust, the service:

```rust
let backend = Arc::new(ThinClientBackend::dial("@katzenpost").await?);
let key = Keypair::load_or_generate(&*backend, &data_dir, "fetcher").await?;
let mut cfg = Config::new(key, data_dir.join("state"));
cfg.display_name = "fetcher".into();
let svc = Service::new(cfg, backend.clone())?;
log::info!("service id {}", svc.id());
svc.run(|session| async move {
    while let Ok(msg) = session.recv().await {
        if session.send(&reply(&msg)).await.is_err() { return; }
    }
}).await?;
```

Rust, the client:

```rust
let dirs = Directory::all(backend.clone(), None, poll).await?;
let d = dirs[0].lookup(service_id).await?;
let conn = services::dial(backend.clone(), &d, "fetcher client", poll).await?;
conn.send(&request).await?;
let raw = conn.recv().await?;
```

Messages are CBOR by convention; `common.Marshal` and `Unmarshal` in
Go, `services::cbor` in Rust. A message must fit in one box;
`max_message` says how large that is.

Sessions and the service's router links are kept in the data directory
and restored on restart, so a service picks up its open sessions where
it left them. `Session.restored()` in Rust tells a handler it is
resuming one, so it does not greet twice.

Working code: [`go/cmd/motd-service`](https://github.com/katzenpost/pigeonhole_protocols/tree/main/go/cmd/motd-service)
and [`go/cmd/motd`](https://github.com/katzenpost/pigeonhole_protocols/tree/main/go/cmd/motd),
[`rust/src/bin/eliza.rs`](https://github.com/katzenpost/pigeonhole_protocols/blob/main/rust/src/bin/eliza.rs),
and the end-to-end tests in
[`go/pigeonservice/service_test.go`](https://github.com/katzenpost/pigeonhole_protocols/blob/main/go/pigeonservice/service_test.go)
and [`rust/tests/services.rs`](https://github.com/katzenpost/pigeonhole_protocols/blob/main/rust/tests/services.rs).

## How to let chat users reach your service

A katzenqt user adds a contact by pasting a voucher code. A Rust
service can mint such codes itself with `Service::offer`; each is used
once, survives restarts until it is, and the session it opens arrives
through `accept` and `run` like any other. Eliza keeps a few on disk
for its operator to hand out:

```rust
tokio::spawn(eliza::keep_vouchers(svc.clone(), data_dir.join("vouchers"), 3));
```

The Go framework does not offer vouchers yet; a Go service is reached
through the directory.

## How to move a service connection into a group

This is the pattern to copy. The service connection is the lobby: it
tells the client how to join and takes the client's join code. From
then on everything travels in the group, with the group chat protocol's
reliability and persistence, and the lobby connection is left alone.

The zulip bridge does exactly this. It is a member of one group, and
its service handler is a short conversation that ends in an invitation:

```rust
pub async fn join<B: Backend>(&self, session: Session<B>) {
    let max = session.max_message().await?;
    if !session.restored() {
        send(&session, "To join: in your chat app, ask to join a group, and paste the voucher code it shows here.", max).await?;
    }
    loop {
        match recv_text(&session).await {
            Ok(Some(code)) => {
                let reply = match self.client.invite(&self.chat, code.trim()).await {
                    Ok(()) => "Inviting you; the group appears in your app once the invitation is read.",
                    Err(ClientError::NotAVoucher) => "That is not a voucher code.",
                    Err(e) => return log::warn!("{e}"),
                };
                send(&session, reply, max).await?;
            }
            Ok(None) => continue,
            Err(e) => return log::warn!("a session ended: {e}"),
        }
    }
}
```

`self.client` is an ordinary group chat client the service opened at
start, in a group it founded. One service, one group, every client a
member works for a bridge or a broadcast. A fetcher that must keep each
client's requests private founds a fresh group per client instead:
`create` a group in the handler, `invite` the code into it, and serve
that group's lines.

Working code: [`rust/src/services/zulip`](https://github.com/katzenpost/pigeonhole_protocols/tree/main/rust/src/services/zulip)
and its README, and [`rust/tests/services_zulip.rs`](https://github.com/katzenpost/pigeonhole_protocols/blob/main/rust/tests/services_zulip.rs).

## How to test without a mixnet

Everything above takes a `transport.Backend`, and two of them need no
network.

**In-process**, for unit tests: `sim.NewWorld()` in Go and
`transport::sim` in Rust are an in-memory Pigeonhole that follows the
replicas' rules: a box lives for its epoch and the next, a rewrite of
the same bytes succeeds, other bytes are refused. A hook sees every
read and write and can fail it, which is how the crash and
flaky-network tests are written.

**In a process of its own**, for clients that are killed and restarted
or for Go and Rust sharing one Pigeonhole: `pigeonhole-sim` serves the
in-memory backend over a unix socket, and the `remote` backend dials
it.

```
cd go && go run ./cmd/pigeonhole-sim -socket ../pigeonhole.sock
cd go && go run ./examples/chat -name alice -state alice -sim ../pigeonhole.sock
cd rust && cargo run --release --example chat -- -name bob -state bob -sim ../pigeonhole.sock
```

Then against the real thing: `make e2e DAEMON=@katzenpost` runs two
clients over a running client daemon, and `go/services/interop` runs
the services, a router and a directory against katzenpost's localnet or
a live mixnet.

## Where things are

| | Go | Rust |
|---|---|---|
| Group chat client | `go/protocols/katzenqt1/client` | `protocols::katzenqt1::client` |
| Service framework | `go/pigeonservice` | `services` |
| Directory and routers | katzenpost `pigeonservice/discovery`, `pigeonservice/voucher_router` | `services::Directory`, `services::dial` |
| Backends | `go/transport/{thinclient,sim,remote}` | `transport::{thinclient,sim,remote}` |
| Services shipped | `motd` | `eliza`, `zulip-bridge` |

A Python implementation of the group chat client is in `py/`; it has
no service framework yet.
