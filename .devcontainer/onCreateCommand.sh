#!/usr/bin/env bash

# Add ngrok key
RUN curl -fsSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc > /etc/apt/trusted.gpg.d/ngrok.asc \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list

apt-get update && apt-get install -y \
    bash-completion \
    ngrok

echo '
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi
' >> ~/.bashrc
