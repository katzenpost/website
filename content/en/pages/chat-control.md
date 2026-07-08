---
title: "Chat Control, Thursday: you are about to outlaw what you paid us to build"
linkTitle: "Chat Control Letter"
description: "A public letter to the Members of the European Parliament ahead of the Chat Control vote."
draft: false
type: "pages"
slug: "/chat-control/"
---

*This is a public letter to the Members of the European Parliament, published at [https://katzenpost.network/pages/chat-control](https://katzenpost.network/pages/chat-control).*

Dear Members of the European Parliament,

On Thursday you vote for the third time on Chat Control 1.0. I am asking you to vote to reject, and to be present, because under this procedure an absent or abstaining Member counts in favour.

My name is David Stainton. I founded the Katzenpost software project in 2017 and remain its core developer, though I write to you in a personal capacity. You have almost certainly never heard of Katzenpost. You paid for it.

Between 2015 and 2019 the European Commission funded PANORAMIX, Horizon 2020 grant agreement 653497, €4,459,711. The consortium included University College London, KU Leuven, the University of Edinburgh, GRNET, Greenhost and SAP. Its purpose was to build European infrastructure for communications that conceal not only content but metadata: who speaks to whom, when, how often, from where. The funding heading, and this is the Commission's language and not mine, was "Secure societies: protecting freedom and security of Europe and its citizens." The private messaging strand of that project produced Katzenpost. I built it, within that consortium, alongside some of Europe's best researchers in this field.

Do not take my word for any of this. Open our paper, Echomix: a Strong Anonymity System with Messaging, at [https://arxiv.org/abs/2501.02933](https://arxiv.org/abs/2501.02933). Section 3.4 states that Katzenpost grew out of the Panoramix project; the citation, reference [38], is the European Commission's own CORDIS record for grant 653497. The Acknowledgment section lists that same grant among the funders of the project's development. And the flag of the European Union is displayed, today, on our funders page at [https://katzenpost.network/pages/funders](https://katzenpost.network/pages/funders). Every claim in this letter is checkable against your own institutions' records. I am also available to brief you or your staff, today or at any time, on the technical questions this file raises.

The grant ended in January 2019. The project did not. Katzenpost is still being built by a small group of cryptographers, computer scientists, mathematicians and engineers. Echomix, the design it runs on, resists traffic analysis by adversaries who can watch the entire network at once, tolerates compromised servers and compromised contacts, and encrypts every packet against the quantum computers that do not exist yet but will.

I will be candid about where we are, because this letter asks you for honesty and owes you the same. Nine years in, we have not yet put a finished tool in the hands of ordinary Europeans. Our public network and its client software are still maturing toward a general release. I could present that to you as a confession. I present it instead as evidence. This is what a field looks like when a continent funds four years of research and then walks away: the United States has funded Tor continuously for two decades, while the European alternative has survived since 2019 on volunteers and small foundation grants. I am not writing to protect a product or a market position; I have neither. I am writing because the law you vote on this week would take the field Europe seeded and, rather than finish what it started, outlaw it.

I am especially proud of the work of my colleague Dr Ewa J. Infeld, our mathematician, who led the writing of the Echomix paper and is its first author. She took a doctorate at Dartmouth under Peter Winkler, applying matching theory to anonymity systems. Mix networks have existed as an idea since Chaum described them in 1981, but the published analysis of them contained errors that had gone uncorrected for years, including in the very designs ours descends from; her review of the field found them, and her mathematical insights made our design better than the literature it grew from. Stating precisely which adversary is defeated and which is not is exacting, foundational work that almost nobody funds. She is European, and she has done it for Europe, for a fraction of what a single national surveillance programme costs. What the project believes, and why, is at [https://katzenpost.network/pages/moral-character](https://katzenpost.network/pages/moral-character).

I will also be honest about the objection you are thinking of, because that published values statement is honest about it: the argument that anonymity networks can also serve criminals is not factually wrong. Neither is it an argument. Every infrastructure of freedom, from the postal system to the private home to the lawyer's office, serves the guilty alongside the innocent, and Europe has never before concluded that the remedy is to abolish the confidentiality of all of them. The question is never whether a protection can be abused. It is what a society becomes without it.

And here the research is precise in a way that matters for your vote. Anonymity loves company: it is a settled result in this field that an anonymity network used only by spies, soldiers and criminals protects none of them, because every user is already a target. What protects the journalist, the abuse victim seeking help, the whistleblower inside a ministry, is the ordinary traffic of ordinary people around them. Ordinary users are not incidental beneficiaries of networks like this. They are the protection. A law that drives ordinary Europeans off such networks does not inconvenience the vulnerable. It unmasks them. Those of us who build these systems assume, as a matter of routine operational security, that state intelligence services already use techniques like ours to protect their own communications. The only question this regulation decides is whether citizens may have what their governments already do.

The most widely deployed anonymity network in the world is Tor. Tor is excellent and I admire it; I have contributed to its ecosystem myself. It is also, by the explicit admission of its own design paper, unable to defend against an adversary who can watch the whole network at once. Mix networks can; that is what they are for.

Europe did the science. Loopix, Sphinx, the Usenix work: European. Europe wrote the cheque. Europe is now preparing to make the result illegal.

Understand precisely what Chat Control does to this work. The regulation assumes a service can identify a sender, inspect a message, and act on it. Katzenpost is engineered so that its own operators can do none of those things. That is not an oversight to be patched. It is the entire point. There is no "risk mitigation measure" available to a mix network, because you cannot scan what you cannot attribute. A legal regime built on mandatory inspectability does not burden this technology. It forbids it by construction. European law would destroy what European money created, and hand the field to the Americans for a generation.

It would do so for nothing. The Commission's own evaluation of this very regulation, COM(2025) 740 final of November 2025 ([https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52025DC0740](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52025DC0740)), concedes that the available data are insufficient to answer whether it is even proportionate, while recording provider-reported error rates for detecting new material as high as 20 percent. And in 2020 the Irish police received 4,192 referrals generated by precisely this kind of voluntary scanning. They confirmed that 471 of them, more than one in ten, were not abuse material at all. Among the flagged content: children playing on a beach. Fewer than 410 referrals were actionable. And having established that these people were innocent, An Garda Síochána kept their files anyway.

More than eight hundred scientists and researchers from thirty-seven countries have told you this does not work. Professors Carmela Troncoso and Bart Preneel, two of the leading researchers in the very field Europe funded, warned you against fast-tracking this file, citing error rates they consider unacceptable and targeted alternatives that have existed for years.

Nor is the harm confined to the wrongly accused. It is measurable in everyone else. Penney's study of Wikipedia traffic after the Snowden disclosures, and Stoycheff's work on Facebook, both found that people who know they are watched stop looking things up and stop saying what they think. Surveillance does not merely observe a population. It edits it: it makes people, in the words of the cryptographer Phillip Rogaway, conformant, fearful and boring.

One last thing.

The confidentiality of correspondence is written into Article 8 of the Convention, drafted in 1950, and into Article 10 of the German Basic Law, and into Article 7 of the Charter you are sworn to uphold. Those clauses were not written by people theorising about privacy. They were written by people who had spent a decade watching what a state becomes when nothing a citizen writes is beyond its reach.

The Gestapo read mail. It ran informants, opened envelopes, tapped lines. What it could not do was read everything, because reading everything was physically impossible. That limit was not restraint, and it was not law. It was physics. It is the reason the White Rose could print, and the reason resistance networks across occupied Europe could pass a message at all. Every one of them depended on communication the state could not read.

Client-side scanning removes that limit. It places on every device the capacity to inspect every private message before it is encrypted. No secret police in European history has held that capability. And it will not be installed by villains. It will be installed, as the project's founding statement puts it, by engineers just doing their jobs, the pattern Hannah Arendt taught Europe to recognise. The only safeguard left is a promise that the list of things being searched for will never grow. I invite you to name one European state, in the last hundred years, that made such a promise and kept it.

I do not accuse this Parliament of bad faith. I am saying that the constitutional order you serve was built by people who understood that the question is never whether today's government is decent. It is what tomorrow's inherits.

Vote to reject the Council text on Thursday, in person; failing that, vote for the amendments this Parliament already adopted. If the 361 votes cannot be found, insist the file returns to LIBE, where cross-party amendments can be drafted in the open rather than pushed through an emptying chamber. And when CSAR returns from trilogue, remember that Europe once spent public money building the thing you are being asked to outlaw.

Europe has been here before. It wrote the Convention afterwards.

Yours sincerely,

David Stainton\
Founder and core developer, the Katzenpost software project\
Writing in a personal capacity\
[https://katzenpost.network](https://katzenpost.network)\
[dstainton415@gmail.com](mailto:dstainton415@gmail.com)
