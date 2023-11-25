FROM ubuntu:22.04

WORKDIR /app

# Set ENV
ENV SHELL=/bin/bash

# Install build dependencies
RUN apt-get update -y && apt-get install -qq apt-transport-https apt-utils software-properties-common curl
RUN apt install -y python3.11 python3-pip
RUN curl -fsSL https://get.pnpm.io/install.sh | sh -
RUN apt -y upgrade

SHELL ["/bin/bash", "-c"]
