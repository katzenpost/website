---
title: "Download"
linkTitle: "Download"
description: ""
slug: "/download/"
menu: {main: {weight: 60}}
type: "pages"
---

Each link below is a file from the project's latest release on GitHub.
Every release has a `SHA256SUMS` file; with it beside the downloads,
`sha256sum --check --ignore-missing SHA256SUMS` checks them.

## kpclientd

kpclientd is the Katzenpost client daemon. Applications reach the mixnet
through it, so a computer or phone that runs any of the applications below
on the mixnet needs it too.

| Platform | Download |
|----------|----------|
| Linux, Debian package | Not yet released; it will appear on the [Katzenpost releases](https://github.com/katzenpost/katzenpost/releases) page. |
| Android 13 or later, phones (arm64-v8a) | [kpclientd-android-v1.1.0-arm64-v8a.apk](https://github.com/katzenpost/kpclientd-android/releases/download/v1.1.0/kpclientd-android-v1.1.0-arm64-v8a.apk) |
| Android 13 or later, emulators (x86_64) | [kpclientd-android-v1.1.0-x86_64.apk](https://github.com/katzenpost/kpclientd-android/releases/download/v1.1.0/kpclientd-android-v1.1.0-x86_64.apk) |

Android checksums: [SHA256SUMS](https://github.com/katzenpost/kpclientd-android/releases/download/v1.1.0/SHA256SUMS).
The [v1.1.0 release](https://github.com/katzenpost/kpclientd-android/releases/tag/v1.1.0)
also has unsigned APKs, for checking that the build is reproducible.

## Applications

### hushphone

Group chat with push-to-talk voice messages, over the Katzenpost mixnet or
a Reticulum mesh. On the mesh it needs no kpclientd.

| Platform | Download |
|----------|----------|
| Debian 13, amd64 | [hushphone-v0.1.3-debian-13-amd64.deb](https://github.com/katzenpost/hushphone/releases/download/v0.1.3/hushphone-v0.1.3-debian-13-amd64.deb) |
| Ubuntu 24.04, amd64 | [hushphone-v0.1.3-ubuntu-24.04-amd64.deb](https://github.com/katzenpost/hushphone/releases/download/v0.1.3/hushphone-v0.1.3-ubuntu-24.04-amd64.deb) |
| Linux, x86_64 | [hushphone-v0.1.3-linux-x86_64.tar.gz](https://github.com/katzenpost/hushphone/releases/download/v0.1.3/hushphone-v0.1.3-linux-x86_64.tar.gz) |
| Android, phones (arm64-v8a) | [hushphone-v0.1.3-arm64-v8a.apk](https://github.com/katzenpost/hushphone/releases/download/v0.1.3/hushphone-v0.1.3-arm64-v8a.apk) |
| Android, emulators (x86_64) | [hushphone-v0.1.3-x86_64.apk](https://github.com/katzenpost/hushphone/releases/download/v0.1.3/hushphone-v0.1.3-x86_64.apk) |

Checksums: [SHA256SUMS](https://github.com/katzenpost/hushphone/releases/download/v0.1.3/SHA256SUMS).
Release notes: [v0.1.3](https://github.com/katzenpost/hushphone/releases/tag/v0.1.3).

### frank_chat

A desktop group chat over the Katzenpost mixnet that speaks katzenqt's
group chat.

| Platform | Download |
|----------|----------|
| Linux, x86_64 | [frank_chat-v0.4.1-x86_64-linux](https://github.com/katzenpost/frank_chat/releases/download/v0.4.1/frank_chat-v0.4.1-x86_64-linux) |
| Android, phones (arm64) | [frank_chat-v0.4.1-arm64.apk](https://github.com/katzenpost/frank_chat/releases/download/v0.4.1/frank_chat-v0.4.1-arm64.apk) |

Checksums: [SHA256SUMS](https://github.com/katzenpost/frank_chat/releases/download/v0.4.1/SHA256SUMS);
the APK before signing: [UNSIGNED-SHA256SUMS](https://github.com/katzenpost/frank_chat/releases/download/v0.4.1/UNSIGNED-SHA256SUMS).
Release notes: [v0.4.1](https://github.com/katzenpost/frank_chat/releases/tag/v0.4.1).

### jam

A terminal group chat over the Katzenpost mixnet that speaks katzenqt's
group chat.

| Platform | Download |
|----------|----------|
| Linux, x86_64 | [jam-v0.2.0-x86_64-linux](https://github.com/katzenpost/jam/releases/download/v0.2.0/jam-v0.2.0-x86_64-linux) |

Checksums: [SHA256SUMS](https://github.com/katzenpost/jam/releases/download/v0.2.0/SHA256SUMS).
Release notes: [v0.2.0](https://github.com/katzenpost/jam/releases/tag/v0.2.0).

## Running a mixnet

Teams that run a mixnet need the other Katzenpost programs: the server
for mix, gateway and service nodes, the directory authority, the courier,
the replica, and the configuration and key tools. A second Debian package holds them all, with their
systemd units. It is not yet released; it will appear on the
[Katzenpost releases](https://github.com/katzenpost/katzenpost/releases) page.
