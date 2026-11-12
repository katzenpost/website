---
title: "Writing READMEs"
linkTitle: "Writing READMEs"
description: "A checklist for writing the README of any Katzenpost repository."
author: ["David Stainton"]
draft: false
url: "docs/writing_readmes"
---

A README is the doorway into a repository for one named audience: a
user who wants a client running, an operator, an application
developer, or a contributor. Write it for that reader. Use this
checklist for every Katzenpost repository.

## Checklist

1. **Who is this for?** Name the primary audience, and at most one
   secondary audience, before writing.
2. **One sentence.** Say what this repository is and what it is for,
   in that audience's words.
3. **Is it for you?** Say what it does and does not do, and when to
   use something else.
4. **Fastest path to success.** Installation, then the smallest
   working example, with commands that actually run.
5. **Map.** List what is in the repository (crates, modules,
   binaries), with one line and a link each.
6. **Link out, don't dump.** Specifications, design notes and long
   how-tos live in `docs/` or on this website; the README stays short.
7. **Status and compatibility.** Versions, wire versions, what it
   interoperates with, and which test vectors prove it.
8. **Testing, contributing, licence.** Briefly.
9. **Checked.** Every command and claim is verified against the code;
   the README describes only this repository; no bragging.
   Changelog-style "new in" sections belong in a changelog or the
   release notes.

## Where the rest goes

[Diátaxis](https://diataxis.fr/) divides documentation into four
kinds: tutorials, which teach by doing; how-to guides, which solve a
stated task; reference, which describes the machinery; and
explanation, which gives the reasons behind it. A README is none of
these at length. It gives the reader one quick start and then links
to each kind where it lives, in the repository's `docs/` or on this
website.

## Sources

- Daniele Procida, [Diátaxis](https://diataxis.fr/).
- Tom Preston-Werner, [Readme Driven Development](https://tom.preston-werner.com/2010/08/23/readme-driven-development.html) (2010).
- Stephen Whitmore, [Art of README](https://web.archive.org/web/2023/https://github.com/hackergrrl/art-of-readme) (archived copy).
- Richard Littauer, [Standard Readme](https://github.com/RichardLitt/standard-readme).
- [Google developer documentation style guide](https://developers.google.com/style).
- [Write the Docs](https://www.writethedocs.org/).
- Jared Bhatti, Zachary Sarah Corleissen, Jen Lambourne, David Nunez and Heidi Waterhouse, [Docs for Developers](https://docsfordevelopers.com/) (Apress, 2021).
