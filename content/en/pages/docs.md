---
title: "Katzenpost Documentation"
linkTitle: "Documentation"
draft: false
menu: {main: {weight: 70}}
slug: "/docs/"
type: "pages"
---


### Fine Katzenpost Literature

---

|      | Title                                                                                                    | Description                                                                                                                                                        | Link(s)                                                                                                                     |
|------|----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| 📖   | **[Admin Guide](/pages/admin_guide)**                                                                    | Detailed guide for deploying and managing Katzenpost servers, including setting up a local Docker-based mixnet.                                                   | [HTML](/pages/admin_guide)                                                                                            |
| 🔒   | **[Threat Model](/pages/threat_model)**                                                                   | An evolving document defining Katzenpost's security assumptions, attack scenarios, and mitigation strategies.                                                      | [HTML](/pages/threat_model) / [PDF](/research/Threat_Model_Doc.pdf)                     |
| 📚   | **[Literature Review](/research/Literature_overview__website_version.pdf)**          | A curated review of academic literature, explaining the theoretical foundations behind Katzenpost's design decisions.                                              | [PDF](/research/Literature_overview__website_version.pdf)                                 |
| 🎧   | **[Audio Engineering Considerations for a Modern Mixnet](/pages/audio_eng)**                                                  | Technical analysis of audio transmission challenges and solutions for modern mixnets, with a focus on usability and scalability.                                   | [HTML](/pages/audio_eng) / [PDF](/research/Audio_Engineering_Considerations_for_a_Modern_Mixnet.pdf) |

---

### Design Specification Documents

These documents are mostly for internal use. They go into excruciating detail which is not so good for most people but great for experts.

---

|    | Title                                                                            | Description                                                                                                                                               | Link(s)                                                        |
|----|----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| 📖 | **[Mixnet](/specs/mixnet.pdf)**                                                  | Describes the overall mixnet design.                                                                                                                | [PDF](/specs/mixnet.pdf)                                       |
| 📖 | **[Public Key Infrastructure](/specs/pki.pdf)**                                  | Every mixnet must have a PKI, this doc describes ours.                                                                                              | [PDF](/specs/pki.pdf)                                          |
| 📖 | **[Wire Protocol](/pages/wire_protocol)**                                        | A detailed design specification for our PQ Noise based wire protocol, which is used for transport encryption between all the mix nodes and dirauth nodes. | [HTML](/pages/wire_protocol) / [PDF](/specs/wire_protocol.pdf) |
| 📖 | **[Sphinx packet format](/specs/sphinx.pdf)**                                    | Sphinx packet format, a nested cryptographic packet format designed for mix networks.                                                                                                                                      | [PDF](/specs/sphinx.pdf)                                       |
| 📖 | **[KEM Sphinx packet format](/specs/sphinx.pdf)**                                | The KEM Sphinx variation of Sphinx                                                                                                                        | [PDF](/specs/kemsphinx.pdf)                                    |
| 📖   | **[Sphinx Replay Detection](/specs/sphinx_replay_detection.pdf)**   | Sphinx Replay Detection | [PDF](/specs//specs/sphinx_replay_detection.pdf) |
| 📖 | **[Certificate format](/specs/certificate.pdf)**                                 | PKI Certificate format                                                                                                                                        | [PDF](/specs/certificate.pdf)                                  |
| 📖 | **[Client2](/specs/client2.pdf)**                                                | Client2 thin client library design..                                                                                                                                                  | [PDF](/specs/client2.pdf)                                      |
| 📖 | **[Mix decoy stats propagation](/specs/mix_decoy_stats_propagation.pdf)** | Mix decoy stats propagation                                                                                                                               | [PDF](/specs/mix_decoy_stats_propagation.pdf)                  |


---
