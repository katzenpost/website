---
title: "Katzenpost Documentation"
linkTitle: "Documentation"
draft: false
menu: {main: {weight: 70}}
type: "base"
---


### Fine Literature

---

|      | Title                                                                                                    | Description                                                                                                                                                        | Link(s)                                                                                                                     |
|------|----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| 📖   | **[Admin Guide](/docs/admin_guide)**                                                                    | Detailed guide for deploying and managing Katzenpost servers, including setting up a local Docker-based mixnet.                                                   | [HTML](/docs/admin_guide) / [PDF](/admin_guide/admin_guide.pdf)                                                                                              |
| 🔒   | **[Threat Model](/docs/threat_model)**                                                                   | An evolving document defining Katzenpost's security assumptions, attack scenarios, and mitigation strategies.                                                      | [HTML](/docs/threat_model) / [PDF](/research/Threat_Model_Doc.pdf)                     |
| 📚   | **[Literature Review](/research/Literature_overview__website_version.pdf)**          | A curated review of academic literature, explaining the theoretical foundations behind Katzenpost's design decisions.                                              | [PDF](/research/Literature_overview__website_version.pdf)                                 |
| 🎧   | **[Audio Engineering Considerations for a Modern Mixnet](/docs/audio_eng)**                                                  | Technical analysis of audio transmission challenges and solutions for modern mixnets, with a focus on usability and scalability.                                   | [HTML](/docs/audio_eng) / [PDF](/research/Audio_Engineering_Considerations_for_a_Modern_Mixnet.pdf) |

---

### Design Specifications

These documents are mostly for internal use. They go into excruciating detail which is not so good for most people but great for experts.

---

|    | Title                                                                            | Description                                                                                                                                               | Link(s)                                                        |
|----|----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| 📖 | **[Mixnet](/docs/specs/mixnet)**                                                  | Describes the overall mixnet design.                                                                                                                | [HTML](/docs/specs/mixnet)                                   |
| 📖 | **[Public Key Infrastructure](/docs/specs/pki)**                                  | Every mixnet must have a PKI, this doc describes ours.                                                                                              | [HTML](/docs/specs/pki)                                        |
| 📖 | **[Wire Protocol](/docs/specs/wire_protocol)**                                        | A detailed design specification for our PQ Noise based wire protocol, which is used for transport encryption between all the mix nodes and dirauth nodes. | [HTML](/docs/specs/wire_protocol) / [PDF](/specs/wire_protocol.pdf) |
| 📖 | **[Sphinx packet format](/docs/specs/sphinx)**                                    | Sphinx packet format, a nested cryptographic packet format designed for mix networks.                                                                                                                                      | [HTML](/docs/specs/sphinx)                                      |
| 📖 | **[KEM Sphinx packet format](/docs/specs/kem_sphinx)**                                | The KEM Sphinx variation of Sphinx                                                                                                                        | [HTML](/docs/specs/kem_sphinx) / [PDF](/specs/kemsphinx.pdf)                                    |
| 📖   | **[Sphinx Replay Detection](/docs/specs/sphinx_replay_detection)**   | Sphinx Replay Detection | [HTML](/docs/specs/sphinx_replay_detection) |
| 📖 | **[Certificate format](/docs/specs/certificate)**                                 | PKI Certificate format                                                                                                                                        | [HTML](/docs/specs/certificate)                                 |
| 📖 | **[Client2](/docs/specs/client2)**                                                | Client2 thin client library design..                                                                                                                                                  | [HTML](/docs/specs/client2)                                      |
| 📖 | **[Mix decoy stats propagation](/docs/specs/mix_decoy_stats_propagation)** | Mix decoy stats propagation                                                                                                                               | [HTML](/docs/specs/mix_decoy_stats_propagation)                 |


---
