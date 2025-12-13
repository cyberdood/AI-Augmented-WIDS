FROM ubuntu:25.04

ENV DEBIAN_FRONTEND=noninteractive

# Base tools needed for Kismet repo + install
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        gnupg \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add Kismet apt repo + key, then install Kismet
RUN set -eux; \
    mkdir -p /usr/share/keyrings; \
    wget -qO- https://www.kismetwireless.net/repos/kismet-release.gpg.key \
      | gpg --dearmor -o /usr/share/keyrings/kismet-archive-keyring.gpg; \
    echo 'deb [signed-by=/usr/share/keyrings/kismet-archive-keyring.gpg] https://www.kismetwireless.net/repos/apt/release/plucky plucky main' \
      > /etc/apt/sources.list.d/kismet.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends kismet; \
    rm -rf /var/lib/apt/lists/*

# Optional: create dirs for logs/config if you want to mount volumes later
RUN mkdir -p /kismet/logs /kismet/config

# Kismet web UI default port
EXPOSE 2501

# Default command (you can override with docker run if needed)
CMD ["kismet"]
