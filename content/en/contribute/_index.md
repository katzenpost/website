---
title: "Contribute"
draft: false
type: "community"
permalink: "/contribute/"
resources:
---

### Where to Start

We have a lot of repositories! The top-level packages that you'll probably want to look at first are:

* [Katzen](https://github.com/katzenpost/katzen) a cross-platform minimum viable messenger app in purely in Go using Gioui framework that has extended beyond catchat
* [Catshadow](https://github.com/katzenpost/katzenpost/tree/main/catshadow) is a mix network messaging system. This repository contains a client library which can be used with a Katzenpost mix network. It not only uses strong modern end to end encryption (Noise + Double Ratchet), but it is also designed to reduce the amount of metadata leaked onto the network.
* [Client](https://github.com/katzenpost/katzenpost/tree/main/client) is a mixnet client library you can use to write applications that interact with mixnet services.
* [Server](https://github.com/katzenpost/katzenpost/tree/main/server) is the mix and provider daemons that route messages and run services.
* [Authority](https://github.com/katzenpost/katzenpost/tree/main/authority) are the PKI daemons that provide key and service information to the network.
* [Server_Plugins](https://github.com/katzenpost/server_plugins) are examples of a mixnet service plugins written in golang and rust.

Additional things of interest:

- [Dockerized Katzenpost](https://github.com/katzenpost/katzenpost/blob/main/docker/README.rst) build and run a local Katzenpost mixnet for development and research
- [Mixnet Academy](/docs/mixnet-academy/) papers, presentations, and general mixnet research which has influenced Katzenpost

### Project Ideas

- Some of our other longer term projects ideas involving future research are documented here in various [other tickets](https://github.com/katzenpost/mixnet_uprising/issues)
