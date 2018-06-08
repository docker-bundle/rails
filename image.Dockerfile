FROM ruby:2.3.6-slim-stretch

# deps

RUN apt-get update \
    && apt-get install -y \
      xz-utils axel \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# node
# depends_on: [xz-utils, axel]

ENV NODE_VERSION 10.2.1
ENV NODE_BIN "node-v$NODE_VERSION-linux-x64"

RUN mkdir "/tmp/$NODE_BIN" && cd "/tmp/$NODE_BIN" \
    && axel "https://nodejs.org/dist/v$NODE_VERSION/$NODE_BIN.tar.xz" -q -o $NODE_BIN.tar.xz \
    && tar xf $NODE_BIN.tar.xz \
    && cp -r "$NODE_BIN"/* /usr/local/ \
    && cd / && rm -rf "/tmp/$NODE_BIN"

# yarn

RUN npm i -g yarn

# rails deps

RUN apt-get update \
    && apt-get install -y build-essential patch ruby-dev zlib1g-dev liblzma-dev libpq-dev python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
