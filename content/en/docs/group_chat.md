---
title: "Katzenpost Group Chat Design"
linkTitle: "Group Chat"
url: "docs/specs/group_chat.html"
description: ""
categories: [""]
tags: [""]
author: ["Threebit Hacker", "David Stainton"]
version: 0
draft: true
---



MVP group chat draft, without key rotation

BACAP primitives give us:
- SingleMessage
- AllOrNothingMessage (for big messages: upload n chunks to temp stream and then put a pointer to that in your own stream as a single message)


Group State:
    - "MembershipCaps": For each member:
        - BACAP read caps (PLEASEADD messages)
    - MembershipHash (hash of "MembershipCaps")

Group Chat Message Types
All messages are SingleMessage if they fit in one BACAP slot, or an AllOrNothingMessage if they are too big.

* TEXT Payload (a normal UTF-8 text message to be displayed inline)
* INTRODUCTION of new Group Member (message with BACAP read cap for new group member)

    * Display Name for the person

    * Universal Read Cap

* File Upload (message containing file name, file size, file content)
  * Image upload (message containing picture, displayed inline by the client)
  * Sound bite upload (walkie talkie style; message containing audio, but played inline by the client)
* "WHO is currently in the group" (question, perhaps about a )
* WHOREPLY with answer to WHO (AllOrNothingMessage with the BACAP read caps for all members)


Group chat message structure (CBOR):
    - Message type (TEXT, INTRODUCTION, ...)
    - schema version (v1 of "File upload" or whatever)
    - GroupState.MembershipHash

Flow for making a new group from scratch (OOB / REUNION / whatever):
    - Everybody exchanges display names + BACAP read caps (PLEASEADD messages)

Flow for introduction to existing group (over existing channel between introducer + new member)
- "INVITATION There exists a group called YoloGroup, do you wanna join?"
- "PLEASEADD I want to join your group"
  - BACAP read cap for the new member
  - Display name chosen by the new member
  - All signed with the BACAP write cap
- The introducer receives PLEASEADD, and if they like the Display Name, they publish PLEASEADD to their own BACAP stream for the group
   - guess there could be a PLEASE REVISE YOUR DISPLAY NAME message for when introducer doesn't like the chosen message


1. the new member needs existing members read caps
2. existing members need the new member's read cap


   - Fuck: how do we do this AllOrNothing when we need to tell both the group the PLEASEADD and the new member needs to know the WHOREPLY ?
      - Courier would need to be able to post the "release" to two separate boxes, which is something we didn't talk about in the paper (but maybe it already works):
          - The BACAP stream for the introducer (so the rest of group can see the PLEASEADD)
          - The new member needs to get a read cap for the introducer's BACAP stream
            - we COULD send this as part of the initial INVITATION, but then we get these silent members that can read stuff that nobody knows about, that sucks
            
- Good question: What if we are adding a whole bunch of people at once; do we really need to upload all the members n times?


FUTURE WORK:
    - Forward secrecy: Can add two extensions that allow transmitting public keys + stuff encrypted under those public keys

