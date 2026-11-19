---
title: "Download"
linkTitle: "Download"
description: ""
slug: "/download/"
menu: {main: {weight: 60}}
type: "pages"
---

hushphone is a group chat with push-to-talk voice messages.

## kpclientd

Every app on this page connects to kpclientd running on the same computer
or phone, over a unix domain socket or TCP. Without kpclientd running, they
do not work.

| Get it | Download |
|--------|----------|
| Android 13 or later, phones | [kpclientd-android-v1.2.0-arm64-v8a.apk](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-arm64-v8a.apk) |
| Android 13 or later, emulators | [kpclientd-android-v1.2.0-x86_64.apk](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-x86_64.apk) |
| Debian 13 and Ubuntu 24.04, amd64 | [kpclientd_0.0.111_amd64.deb](/downloads/kpclientd_0.0.111_amd64.deb) |
| From source | [katzenpost](https://github.com/katzenpost/katzenpost) |

SHA-256 of `kpclientd_0.0.111_amd64.deb`:
`ab3fb57b05cd2fc33f9044779a1f82d8b54757d3d85d14542fbd19df14df684d`.
Android checksums:
[SHA256SUMS](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/SHA256SUMS).

To build from source you need Go and a C compiler:

```
git clone https://github.com/katzenpost/katzenpost
cd katzenpost
make kpclientd
```

Then run it with the
[namenlos client config](https://github.com/katzenpost/kno/blob/main/data/networks/namenlos/.generated/configs/client.toml):

```
cmd/kpclientd/kpclientd -c client.toml
```

## Android

Android 13 or later. Most phones need the arm64-v8a files.

1. Download both apps:
   - [hushphone-v0.3.6-arm64-v8a.apk](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-arm64-v8a.apk)
   - [kpclientd-android-v1.2.0-arm64-v8a.apk](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-arm64-v8a.apk)
2. Open each file to install it. Android may ask you to allow installs from
   your browser.
3. Open **KP Daemon** and start it.
4. Open **hushphone**. When KP Daemon asks, allow it.

For an emulator, use the x86_64 files instead:
[hushphone](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-x86_64.apk),
[kpclientd](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-x86_64.apk).

## Linux desktop

Debian 13 or Ubuntu 24.04, on a 64-bit PC.

1. Download hushphone for your system, and kpclientd:
   - Debian 13: [hushphone-v0.3.6-debian-13-amd64.deb](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-debian-13-amd64.deb)
   - Ubuntu 24.04: [hushphone-v0.3.6-ubuntu-24.04-amd64.deb](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-ubuntu-24.04-amd64.deb)
   - Both: [kpclientd_0.0.111_amd64.deb](/downloads/kpclientd_0.0.111_amd64.deb)
2. Install them. In a terminal, in the folder with the files:

   ```
   sudo apt install ./hushphone-v0.3.6-*-amd64.deb ./kpclientd_0.0.111_amd64.deb
   ```

3. Start kpclientd:

   ```
   systemctl --user enable --now kpclientd
   ```

4. Start hushphone from your applications menu, or run `hushphone`.

Other Linux systems:
[hushphone-v0.3.6-linux-x86_64.tar.gz](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-linux-x86_64.tar.gz)
holds the `hushphone` program. Get kpclientd by building it from source,
above.

hushphone checksums:
[SHA256SUMS](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/SHA256SUMS).

## Other chat clients

These are experimental.

| Client | Get it |
|--------|--------|
| katzenqt | [source](https://github.com/katzenpost/katzenqt) (no release yet) |
| katzenrns | [source](https://github.com/katzenpost/katzenrns) (no release yet) |
| jam | [v0.2.0 release](https://github.com/katzenpost/jam/releases/tag/v0.2.0) |
| frank_chat | [v0.4.1 release](https://github.com/katzenpost/frank_chat/releases/tag/v0.4.1) |
