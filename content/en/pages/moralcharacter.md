---
title: "Katzenpost Politics and Values"
linkTitle: "Values"
description: "Why we started creating Katzenpost and what principles guide us."
draft: false
menu: {main: {weight: 10}}
type: "pages"
slug: "/moral-character/"
aliases:
  - "/moralcharacter.html"
---


## Our position

Never before in human history have we been under as much surveillance as today by governments and corporations. Our current situation came about gradually, the result of computer scientists and software engineers who were "just doing their jobs", what Hannah Arendt called the [banality of evil](https://en.wikipedia.org/wiki/Banality_of_evil). They turned the Internet into an instrument of total surveillance without considering the moral character of their work.

We assert that privacy is important for both the individual and the collective good. The benefit to the individual is obvious. The benefit to the collective is less so, but empirical studies confirm that people modify their behaviour when they know they are surveilled, a form of self-censorship ([Penney 2016](https://btlj.org/data/articles2016/vol31/31_1/0117_0182_Penney_ChillingEffects_WEB.pdf); [Stoycheff 2016](https://journals.sagepub.com/doi/abs/10.1177/1077699016630255)). When this happens during collective decision-making, minority views are less likely to be voiced. Mass surveillance makes people shallow and compliant, and thwarts collective social progress.

There are many forms of online surveillance and we are not trying to fix them all. Our focus is the *traffic analysis* problem: current best practice for messaging encryption does not defend against an adversary who can observe encrypted traffic and extract metadata such as geographical location, position on the network, the social graph, message sizes, message timing, and the rate and frequency of communication. The "secure messaging" problem, in its full traffic-analysis-resistant form, has not been solved at scale.

Katzenpost is a *mix network*: an anonymous communication network designed to reduce the metadata that leaks from a conversation. It is designed to allow people to communicate without leaking the fact that they are communicating with one another. It is a joint effort between cryptographers, computer scientists, mathematicians and software engineers.

There is one further observation worth making. We assume that nation-state military and intelligence groups already use mix networks or similar techniques to protect their own communications metadata as routine operational security. But if every user of such a network is a high-value target, then much of the leaked metadata is still useful to an adversary. *[Anonymity Loves Company](https://www.freehaven.net/anonbib/cache/usability:weis2006.pdf)*: the network needs a varied user base spanning the full range of adversary interest, so that the ordinary users provide cover traffic for the high-risk users who are themselves the targets of surveillance.

It is our view that strong anonymous communication networks should not remain the privilege of secret groups within nation states; their use is a mode of self-defence and should be available to all. You may point out that Tor is widely used and is the most successful publicly deployed anonymous communication network in the world. That is correct. However, Tor does not defend against a global passive adversary ([Tor's own threat model](https://www.freehaven.net/anonbib/cache/tor-design.pdf) says so explicitly), whereas mix networks do. Tor is not considered to provide *strong anonymity*; this is well established in the published academic literature, for example the [Anonymity Trilemma](https://eprint.iacr.org/2017/954).

We build Katzenpost for ourselves and for others. We do not directly control who benefits from our mix network. It may be of use to law enforcement, military and intelligence groups; it may equally benefit journalists, whistleblowers and political activists. The law-enforcement counter-argument, that anonymous communication networks help terrorists and human traffickers, is not factually wrong, but it is a manipulative one-sided argument that ignores all of human history and the collective harm of mass surveillance.


## Two framings of mass surveillance

The two tables below are reproduced from [Phil Rogaway's slides](https://web.cs.ucdavis.edu/~rogaway/papers/moral.html) for *The Moral Character of Cryptographic Work* (IACR Distinguished Lecture, Asiacrypt 2015).

<table class="framing-table td-initial">
  <caption>
    Law-Enforcement Framing
    <span class="caption-source">Ascribed to U.S. FBI Director James Comey.</span>
  </caption>
  <tr>
    <td>Privacy is a <strong>personal good</strong></td>
    <td>Security is a <strong>collective good</strong></td>
  </tr>
  <tr>
    <td>Inherently in <strong>conflict</strong></td>
    <td>Encryption has destroyed the <strong>balance</strong>. Privacy wins</td>
  </tr>
  <tr>
    <td>The <strong>bad guys</strong> may win</td>
    <td>Risk of <strong>Going Dark</strong></td>
  </tr>
</table>

<table class="framing-table td-initial">
  <caption>Surveillance-Studies Framing</caption>
  <tr>
    <td>Surveillance is an <strong>instrument of power</strong></td>
    <td>Technology makes it <strong>cheap</strong></td>
  </tr>
  <tr>
    <td>Tied to <strong>cyberwar</strong> and <strong>assassinations</strong></td>
    <td>Privacy and security usually <strong>not</strong> in conflict</td>
  </tr>
  <tr>
    <td>Makes people <strong>conformant, fearful, boring</strong>. Stifles <strong>dissent</strong></td>
    <td>Hard to stop. <strong>Cryptography</strong> offers hope</td>
  </tr>
</table>


## Further reading

### Anonymous communication research

- Chaum, D. (1981). [*Untraceable Electronic Mail, Return Addresses, and Digital Pseudonyms*](https://bib.mixnetworks.org/#chaum-mix). Communications of the ACM 24(2).
- Dingledine, R., Mathewson, N. & Syverson, P. (2004). [*Tor: The Second-Generation Onion Router*](https://www.freehaven.net/anonbib/cache/tor-design.pdf). USENIX Security.
- Dingledine, R. & Mathewson, N. (2006). [*Anonymity Loves Company: Usability and the Network Effect*](https://www.freehaven.net/anonbib/cache/usability:weis2006.pdf). Workshop on the Economics of Information Security (WEIS).
- Unger, N. et al. (2015). [*SoK: Secure Messaging*](https://ieeexplore.ieee.org/document/7163029). IEEE Symposium on Security and Privacy.
- Das, D., Meiser, S., Mohammadi, E. & Kate, A. (2018). [*Anonymity Trilemma: Strong Anonymity, Low Bandwidth Overhead, Low Latency, Choose Two*](https://eprint.iacr.org/2017/954). IEEE Symposium on Security and Privacy.

### Surveillance, politics, philosophy

- Arendt, H. (1958). [*The Human Condition*](https://en.wikipedia.org/wiki/The_Human_Condition_(book)).
- Bankston, K. & Soltani, A. (2014). [*Tiny Constables and the Cost of Surveillance: Making Cents Out of United States v. Jones*](https://www.yalelawjournal.org/forum/tiny-constables-and-the-cost-of-surveillance-making-cents-out-of-united-states-v-jones). Yale Law Journal Forum 123.
- Rogaway, P. (2015). [*The Moral Character of Cryptographic Work*](https://web.cs.ucdavis.edu/~rogaway/papers/moral.html). IACR Distinguished Lecture, Asiacrypt 2015. ([USENIX Security 2016 video](https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/rogaway))

### Empirical evidence on chilling effects

- Penney, J. (2016). [*Chilling Effects: Online Surveillance and Wikipedia Use*](https://btlj.org/data/articles2016/vol31/31_1/0117_0182_Penney_ChillingEffects_WEB.pdf). Berkeley Technology Law Journal 31(1).
- Stoycheff, E. (2016). [*Under Surveillance: Examining Facebook's Spiral of Silence Effects in the Wake of NSA Internet Monitoring*](https://journals.sagepub.com/doi/abs/10.1177/1077699016630255). Journalism & Mass Communication Quarterly 93(2).

### Further bibliography

- [*Selected Papers in Anonymity*](https://www.freehaven.net/anonbib/), Free Haven's curated bibliography of academic work on anonymity and privacy.
