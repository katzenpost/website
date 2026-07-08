The Pigeonhole API is the message-passing layer of the thin client:
applications write to and read from BACAP-encrypted storage streams
held on the mixnet's storage replicas, reached through couriers.
Much of this API wraps the
[BACAP](https://pkg.go.dev/github.com/katzenpost/hpqc/bacap) scheme,
with the daemon performing all BACAP operations on the
application's behalf. For conceptual background, see
[Understanding Pigeonhole](/docs/pigeonhole_explained/); for worked
examples in all three languages, see the
[Thin Client How-to Guide](/docs/thin_client_howto/).

> **Most Pigeonhole methods cause no mixnet traffic.** Only
> `StartResendingEncryptedMessage` (and its two variants) and
> `StartResendingCopyCommand` put traffic on the mixnet; they are
> marked **Sends mixnet traffic** below and deliver through the
> daemon's stop-and-wait ARQ, described in
> [The Pigeonhole ARQ](/docs/pigeonhole_explained/#the-pigeonhole-arq).
> The `Cancel*` methods are local control operations, and everything
> else is a local computation performed by the daemon over the local
> socket.

<!-- METHOD_TOC -->
