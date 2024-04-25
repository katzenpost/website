---
title: "Katzenpost threat model document"
date: 2024-04-25
description: ""
author: "D. Stainton, E. Infeld"
tags: ["research", "design", "threat model", "security", "privacy", "cryptography"]
draft: true
---

Here we present a draft of the Katzenpost mixnet threat model document.
We regard the threat model document as a living document which is frequently
edited and in need of ongoing maintenance as we continue to develop newer
mixnet protocols. Currently it is being organized by mixnet attack category
and we have arrnaged attacks in a table with corresponding attacker
capabilities. Later sections of the document present a deep dive into the core cryptographic
protocols that comprise Katzenpost, namely these three:

1. Katzenpost Directory Authority PKI protocol
2. PQ Noise based wire protocol (on top of TCP or QUIC)
3. Sphinx nested encrypted packet routing protocol

Those are the basics necessary for point to point communications through the mix network.
However mixnet protocols will then add their own cryptographic protocols which simply
make use of the above three protocols in service to their goals of message transportation.

We thank Wau Holland Stiftung for funding this work.

[Threat Model Doc](https://katzenpost.network/research/Threat_Model_Doc.pdf)
