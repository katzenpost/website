The Pigeonhole API is the message-passing layer of the thin client:
applications write to and read from BACAP-encrypted storage streams
held on the mixnet's storage replicas, reached through couriers. For
conceptual background, see
[Understanding Pigeonhole](/docs/pigeonhole_explained/); for worked
examples in all three languages, see the
[Thin Client How-to Guide](/docs/thin_client_howto/).

> **Most Pigeonhole methods cause no mixnet traffic.** Only
> `StartResendingEncryptedMessage` (and its two variants) and
> `StartResendingCopyCommand` put traffic on the mixnet; they are
> marked **Sends mixnet traffic** below. The `Cancel*` methods are
> local control operations, and everything else is a local
> computation performed by the daemon over the local socket.

<!-- METHOD_TOC -->
