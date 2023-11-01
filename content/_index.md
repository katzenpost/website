---
title: "Katzenpost ¶" 
draft: false
type: home
permalink: "#"
---

> "An especially problematic excision of the political is the marginalization
>  within the cryptographic community of the secure-messaging problem, an
>  instance of which was the problem addressed by [David Chaum](https://bib.mixnetworks.org/#chaum-mix). Secure-messaging
>  is the most fundamental privacy problem in cryptography: how can parties
>  communicate in such a way that nobody knows who said what. More than a
>  decade after the problem was introduced, [Rackoff and Simon](http://sci-hub.tw/10.1145/167088.167260) would comment on
>  the near-absence of attention being paid to the it." [Phillip Rogaway, The Moral Character of Cryptographic Work](moralcharacter.html) 

![](/images/katzenpost-overview.jpg)

The Katzenpost Free Software Project
====================================

Katzenpost is a free software project. We write mix network protocol
libraries.  What is a mix network? It is an anonymous communications
system... however the word anonymous is problematic because some
government authorities equate anonymity with terrorism. We prefer to
instead call it "network security" because you can feel more secure
when you communicate using traffic analysis resistant communications
protocols.

However we realize we cannot simply write a mix network and core
protocol libraries and expect people to use them. Therefore we are
working towards a demonstration encrypted chat client which will
communicate over our mix network.

Traffic analysis helps governments, corporations and Internet service
providers learn more information about the communication even if it is
encrypted. The goal of protecting the confidentiality of messages is
in fact an orthogonal concern to that of resisting traffic
analysis. In particular we are interested in developing mix network
based communications systems that can be used by everyone to hide
these kinds of communications metadata:

- geographic location
- message sender
- message receiver
- message sent time
- message receive time
- message size
- ordering of messages
- frequency of sent messages
- frequency of received messages

There are many message oriented applications and protocols that could
benefit from using our mix network. For example our mix network is not
only good for chat clients but also other types of applications:

- transporting interactions between CRDTs
- transporting interactions to DHTs
- database transaction anonymization
- 'crypto currency' anonymization