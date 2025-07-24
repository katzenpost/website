---
title:
linkTitle: Run a Katzenpost Mix server in a Docker container
description: ""
categories: [""]
tags: [""]
author: []
version: 0
draft: false
slug: "/run_katzenpost_mixnode_docker/"
---

# Run a Katzenpost Mix server in a Docker container

## Prerequisites

* Access to the `namenlos` git repo

## Preparing host filesystem

    mkdir katzenpost-server
    cd katzenpost-server
    mkdir {conf,data}
    chmod 700 data

All further actions are performed from the `katzenpost-server` directory.

## Building the Docker image

* Create `Dockerfile`:

    ```
    FROM golang:bookworm AS builder

    LABEL authors="<ops@cryptonymity.net>"

    RUN \
        cd /go && \
        git clone https://github.com/katzenpost/katzenpost  && \
        cd katzenpost && \
        go mod tidy && \
        cd cmd/server && go build

    FROM debian:bookworm AS deploy

    COPY --from=builder /go/katzenpost/cmd/server/server /usr/bin/server

    EXPOSE 8181

    ARG uid=1000
    ARG gid=1000

    RUN \
        mkdir -p /home/user && \
        echo "user:x:${uid}:${gid}:User,,,:/home/user:/bin/bash" >> /etc/passwd && \
        echo "user:x:${uid}:" >> /etc/group

    USER user
    ENV HOME=/home/user

    ENTRYPOINT ["/usr/bin/server","-f","/conf/katzenpost.toml"]
    ```

* Build Docker image:

    ```
    docker build -t katzenpost/server --build-arg uid=$(id -u) --build-arg gid=$(id -g) .
    ```

* Create `run.sh` to run the server (adjust to your port) and make it executable:

    ```
    #!/bin/bash

    docker run -d --restart=always \
        --name katzenpost-server -h kp-server \
        -p 0.0.0.0:<port>:8181 \
        -v $(pwd)/conf:/conf \
        -v $(pwd)/data:/var/lib/pq-katzenpost-mixserver \
        katzenpost/server
    ```

    Always run this script while in the `katzenpost-server` directory.

## Creating a configuration file

* Create a new file named `<yourname>-pq-mixserver.toml` in `<namenlos.repo>/configs/SSOT/mixes` and adjust `Identifier` and  IP/port setting in `Addresses`:

    ```
    [Server]
    Identifier = "<yourname>"
    PKISignatureScheme = "Ed25519 Sphincs+"
    WireKEM = "KYBER768-X25519"
    Addresses = [ "tcp://<public-ipv4>:<port>", "tcp://<public-ipv6>:<port>" ]
    BindAddresses = [ "tcp://127.0.0.1:8181", "tcp://[::1]:8181" ]
    DataDir = "/var/lib/pq-katzenpost-mixserver"
    IsGatewayNode = false
    IsServiceNode = false

    [Logging]
    Disable = false
    File = ""
    Level = "NOTICE"

    ```

* Assemble the configuration file `conf/katzenpost.toml`:

    ```
    cat \
        <namelos.repo>/configs/SSOT/mixes/<yourname>-pq-mixserver.toml \ <namelos.repo>/configs/pki.toml \
        <namelos.repo>/configs/SSOT/mixserver.toml \
        <namelos.repo>/configs/SSOT/sphinx.toml \
    > conf/katzenpost.toml
    ```

## Generating and extracting keys

* Run the server for the first time:

    ```
    ./run.sh
    ```
* Monitor execution:

    ```
    docker logs -f katzenpost-server
    ```

    Once the server has started sucessfully, the Docker container can be stopped and removed.

* Check that keys (`*.pem`) have been created in the `data/` directory and copy the public identity key to the `namenlos` repo:

    ```
    cp data/identity.public.pem <namelos.repo>/keys/mixserver-keys/<yourname>_mix_id_pub_key.pem
    ```

* Update the repo:

    ```
    cd <namenlos.repo>/configs
    make
    git commit -a
    git push
    ```

## Running the server

    cd katzenpost-server
    ./run.sh
