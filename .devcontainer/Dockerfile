FROM mcr.microsoft.com/devcontainers/python:1-3.9-bookworm

# Add ngrok key
RUN curl -fsSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
    gettext \
    ngrok \
    && rm -rf /var/lib/apt/lists/*

RUN pipx install uv pre-commit
