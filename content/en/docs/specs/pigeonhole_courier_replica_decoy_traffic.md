---
title: ""
linkTitle: "Pigeonhole Courier and Replica Decoy Traffic Design"
description: ""
author: ""
url: ""
date: ""
draft: "false"
slug: "pigeonhole decoys"
layout: ""
type: ""
weight: "41"
version: ""
---

**Abstract**

In this document we describe the traffic shaping and decoy traffic design for the
direct connections among Pigeonhole couriers and storage replicas. These links exist
outside of the mix network proper: couriers maintain persistent connections to every
storage replica, and replicas maintain persistent connections to one another. Because
these connections are direct, they receive none of the protections of the Sphinx
packet format or the mixing strategy, and their traffic patterns must instead be
protected by rate discipline and decoy traffic. This document specifies the send
pacing, the decoy generation rules, the reply scheduling, the link liveness rules,
and the capacity semantics that follow from them. It complements our mix decoy loop
specification and the Pigeonhole protocol specification, and corresponds to §5 of our
paper [Echomix: a Strong Anonymity System with Messaging](https://arxiv.org/abs/2501.02933),
in particular the fixed-throughput connections described there and the reply delays
of §5.4.

## 1. Introduction

Every client interaction with Pigeonhole storage traverses two very different kinds
of network path. The path from the client through the mix network to a courier is
protected by Sphinx packets, per-hop mixing delays, and the client's own Poisson
decoy processes. The onward path from the courier to the storage replicas, and among
the replicas themselves, is a set of plain, long-lived, mutually authenticated PQ
Noise connections. An adversary observing one of these direct links sees neither
box IDs nor payload contents, but without further measures it would see the one
thing we have promised to hide: when, and how much, real work the network is doing.

Our answer is the classic one, applied uniformly: each such link is a
*fixed-throughput* channel. Its send rate is a public constant drawn from the PKI
document, its slots are filled with decoys whenever no real work is queued, and its
observable behavior is therefore independent of client activity. The rest of this
document makes that principle precise, and records the queueing-theoretic reasoning
behind the two mechanisms that implement it: a Poisson send clock on the originator
side of each connection, and independently jittered replies on the responder side.

A guiding rule throughout: **dimensionless ratios may live in code; timescales come
from the PKI document.** Every delay, deadline, and rate in this design is derived
from the consensus parameters, chiefly LambdaR, so that operators tune the network
in one place and every component follows.

## 2. Roles: originator and responder

Each direct connection has exactly one originator and one responder, fixed for the
life of the connection:

* A **courier** is the originator on each of its connections to the R storage
  replicas.
* A **replica** is the originator on each of its connections to its R−1 replica
  peers, used for write replication and proxying.
* The **responder** is whichever party accepted the connection. Replicas respond to
  couriers and to peer replicas.

The two roles have deliberately asymmetric traffic rules, described next. The
asymmetry is not incidental: the originator's job is rate discipline, the
responder's job is unlinkability of replies, and as we show in §4, using the
originator's mechanism on the responder side is not merely unnecessary but
mathematically unsound.

## 3. Originator: the Poisson send clock

The originator paces every transmission on the link, real or decoy, with a single
pseudorandom clock: inter-send intervals are drawn from the exponential
distribution with rate LambdaR (events per millisecond), taken from the PKI
document's Parameters section. Sampled intervals are clamped at the (1 − 10⁻¹²)
quantile of that same distribution, our standard sampling safety cap, so the
realized process is indistinguishable from the unclamped exponential in any honest
measurement window.

In front of the clock sits a FIFO queue of real commands. On each tick the
originator sends the oldest queued real command; if the queue is empty it sends a
decoy command instead. A real message therefore *replaces* a decoy in its slot, and
the wire carries a constant-rate Poisson stream at LambdaR regardless of load. The
responder can distinguish decoys from real commands (it must, to answer them), but
a passive observer of the link cannot, and the link's rate reveals nothing about
how busy the courier or replica is.

Two consequences deserve emphasis:

* **Sends are never gated on replies.** An earlier revision of the courier made
  each send wait for the previous command's reply, as a form of flow control. This
  coupled the link's observable timing to replica processing latency, silenced
  decoy slots exactly when a replica was slow, and head-of-line blocked the link
  behind a single lost reply. It also provided no capacity that the Poisson clock
  does not already provide: LambdaR is a hard, deterministic ceiling on the send
  rate, which is a stronger guarantee against overrunning a replica than any
  reply-coupled scheme. The clock is the sole pacing authority; replies are matched
  to commands by envelope hash and may arrive in any order, at any time.

* **Load shedding is provisioning, not backpressure.** Nothing any client does can
  push a replica beyond (C + R − 1) × LambdaR inbound messages per second, where C
  is the number of couriers and R the number of replicas. Keeping up is therefore
  decided once, when LambdaR is provisioned, not negotiated at runtime. §6 gives
  the arithmetic.

## 4. Responder: one-for-one echo with uniform jitter

The responder never originates traffic. It answers each received command with
exactly one reply: a real reply to a real command, a decoy reply to a decoy
command. Its outbound rate is thus pinned to the originator's LambdaR by one-to-one
correspondence, and the link is symmetric and constant-rate in both directions.

Each reply is held for an independently sampled delay drawn from the uniform
distribution on [0, J], where **J = 1/LambdaR**, one mean link slot, computed from
the PKI document. The delay is drawn from a cryptographic randomness source, since
a predictable jitter defends nothing. Replies wait in a timer queue keyed by their
ready-at time; by Little's Law the expected queue depth is LambdaR × J / 2, which
with J = 1/LambdaR is one half of one reply at any rate.

This generalizes the reply delays of §5.4 of the paper, whose purpose is to prevent
a courier from linking replies that pertain to the same box, and to hide the
processing-time variance that would otherwise distinguish, say, a cheap decoy echo
from a write that waited on a storage compaction.

Two questions about this design have principled answers worth recording:

**Why is the responder not paced by its own Poisson clock, like the originator?**
Because its production rate is pinned at LambdaR by the echo rule, a paced drain at
the same LambdaR would place the reply queue exactly at the M/M/1 boundary,
utilization ρ = 1. A queue at ρ = 1 is null-recurrent: it possesses no stationary
distribution and its depth wanders upward without bound. We observed precisely this
in practice, as sustained per-connection backlogs of fifty to ninety replies, before
replacing the responder's paced sender with the delayed-reply emitter. A paced drain
strictly faster than LambdaR would be sound but pointless, since the output would
simply track the input. There is no rate for a responder-side clock that is both
useful and correct.

**Why uniform jitter rather than exponential?** By the displacement theorem for
Poisson processes, displacing each event of a Poisson stream by an independent,
identically distributed delay yields another Poisson stream of the same rate,
whatever the delay distribution. The reply stream therefore inherits its Poisson
character from the command stream for free, and the jitter distribution influences
only two things: the worst-case added latency, and how thoroughly nearby replies are
decorrelated within that latency budget. Replies sit on an interactive path, so the
budget is a hard cap, and the uniform distribution is the maximum-entropy
distribution under a hard cap. An exponential jitter would buy an unbounded latency
tail and, by the displacement theorem, nothing else.

## 5. Link liveness

A fixed-throughput link doubles as its own failure detector. When decoy traffic is
enabled, inter-arrival gaps on a healthy link are exponential with rate LambdaR, so
we set the wire session's read deadline to the same (1 − 10⁻¹²) quantile used as the
sampling safety cap, roughly 27.6 / LambdaR milliseconds. A peer silent for that
long is dead with overwhelming probability, and the connection is torn down and
redialed. There is no separate keepalive machinery: the decoy stream is the
keepalive.

When decoy traffic is disabled, as in our continuous integration and other testing
postures, an idle link is legitimate and protocol silence implies nothing. No idle
read deadline is imposed at all. Dead peers are instead detected by TCP keepalive at
the kernel, which errors out a blocked read on a vanished peer, and writes remain
bounded by the wire session's write deadline. Disabling decoys trades away the
metadata protections; it does not have to trade away link stability.

## 6. Capacity semantics

LambdaR is not merely a decoy rate; it is the provisioned capacity of every link,
made literal by the design: with decoys on, each link carries exactly LambdaR
messages per second, and real traffic consumes slots that decoys would otherwise
fill.

The stability condition is the elementary single-server queueing bound: the real
offered load on each link must stay below LambdaR, with headroom, because queueing
delay grows as 1/(LambdaR − load) as the load approaches capacity. In terms of
network parameters, with X clients each producing pigeonhole operations at LambdaP,
C couriers, and R replicas:

* Each operation is one courier envelope, dispatched as **two** replica messages,
  one to each client-chosen intermediate replica. Per courier-to-replica link the
  offered load is X × LambdaP × 2 / (C × R), and stability requires this to remain
  below LambdaR.
* Each write additionally causes the intermediate replicas to replicate or proxy
  toward the box's two final shard replicas, costing between one and four messages
  on the replica-to-replica mesh depending on shard coincidences, spread over
  R × (R − 1) directed links, each likewise paced at LambdaR.

The worst-case inbound rate at any single replica is (C + R − 1) × LambdaR, a
quantity fixed entirely by public consensus values. Replicas are sized for it once.

Because a link's rate never varies with demand, capacity planning is deliberately
an *over-provisioning* exercise: LambdaR is chosen for a target user population
comfortably above the expected one. We must never derive LambdaR from measured
load; a demand-adaptive rate would broadcast the network's activity level in the
consensus itself, defeating the purpose of the fixed-throughput design. A future
refinement is to have the directory authorities compute LambdaR at voting time from
a declared target capacity together with the topology, in the same manner that
LambdaG is computed from the Coupon Collector's Bound, so that the provisioning
intent is stated once and the rate follows the topology automatically.

## 7. Summary of parameters and derivations

| Quantity | Value | Source |
|---|---|---|
| Originator send pacing | Exp(LambdaR), safety-capped | PKI document |
| Decoy generation | on tick, when FIFO empty | originator only |
| Reply rate | 1:1 echo of command rate | responder rule |
| Reply jitter bound J | 1/LambdaR (uniform on [0, J]) | PKI document |
| Read deadline, decoys on | SafetyCap(LambdaR) ≈ 27.6/LambdaR | PKI document |
| Read deadline, decoys off | none (TCP keepalive detects dead peers) | posture |
| Worst-case replica ingress | (C + R − 1) × LambdaR | topology + PKI document |

The only constants living in code are dimensionless: the choice of one mean slot
for the jitter bound, and the 10⁻¹² tail probability shared with every other
exponential sampler in Katzenpost.

## Appendix A: the theory, briefly

**Poisson process.** Events occurring independently at a constant average rate λ.
The gaps between events follow the exponential distribution with mean 1/λ, and the
process is memoryless: having waited a while tells you nothing about how much
longer you will wait. This is what makes it the natural shape for traffic that
must reveal nothing.

**M/M/1.** The simplest queue: Poisson arrivals, exponential service times, one
server. Its behavior is governed by the utilization ρ, the arrival rate divided by
the service rate. For ρ < 1 the queue is stable and keeps returning to empty; the
average wait grows as 1/(service − arrival), so it explodes as ρ approaches 1.

**The M/M/1 boundary (ρ = 1).** The server keeps up exactly on average, and
intuition says the queue should hold steady. It does not. At ρ = 1 the queue
length is a fair coin-flip walk with no restoring force; the floor at zero clips
its downward excursions but not its upward ones, so it drifts up roughly like the
square root of elapsed time and never settles. Formally the queue is null
recurrent: it always eventually empties, but the expected time to do so is
infinite. This is why the responder must not pace replies at the same rate they
are produced, and why offered load must sit well below LambdaR.

**Little's Law.** In any stable system, average occupancy equals arrival rate
times average time spent inside: L = λW. With reply jitter uniform on [0, J] the
average wait is J/2, so the emitter's timer queue holds LambdaR × J/2 items, which
for J = 1/LambdaR is one half of one reply at any rate.

**Displacement theorem.** Delay each event of a Poisson stream by an independent
random amount, drawn from any distribution, and the result is again a Poisson
stream at the same rate. Hence reply jitter cannot and need not shape the
aggregate traffic; its only job is to decorrelate individual replies, so we choose
the jitter distribution purely for that.

**Maximum entropy.** Among all distributions confined to [0, J], the uniform is
the least predictable; among all with a fixed mean on unbounded support, the
exponential is. Replies live under a hard latency budget, so uniform is the
correct choice; an exponential jitter would buy an unbounded tail and, by the
displacement theorem, nothing else.

**SafetyCap.** Sampling from an exponential distribution occasionally yields
absurdly long delays, and a real system must bound them, yet any visible
truncation would distort the distribution an adversary observes. SafetyCap(λ)
resolves the tension by capping at the (1 − 10⁻¹²) quantile: solving
e^(−λt) = 10⁻¹² gives t = ln(10¹²)/λ ≈ 27.63/λ. A draw is clamped once per
trillion samples, so the realized traffic is statistically indistinguishable from
the pure exponential, while the system still holds a hard bound. The same number
serves as the dead-peer test on a decoy-bearing link: under the healthy
hypothesis, silence longer than the cap has probability 10⁻¹², so observing it is
overwhelming evidence the peer is gone. One dimensionless constant, two duties,
zero hardcoded timescales.
