FROM debian:buster-slim

ARG ASAN_URL=https://commondatastorage.googleapis.com/chromium-browser-asan/linux-release/asan-linux-release-681094.zip

# Buster is archived — point to archive.debian.org
RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list \
    && sed -i '/buster-updates/d' /etc/apt/sources.list \
    && sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcups2 \
        libdbus-1-3 \
        libgbm1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libxss1 \
        libxtst6 \
        libpci3 \
        unzip \
        xdg-utils \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fSL -o /tmp/asan.zip "$ASAN_URL" \
    && mkdir -p /opt/chromium \
    && cd /opt/chromium \
    && unzip /tmp/asan.zip \
    && rm /tmp/asan.zip \
    && chmod +x /opt/chromium/asan-linux-release-681094/chrome

ENV ASAN_OPTIONS="detect_leaks=0:halt_on_error=1:abort_on_error=1"

ENTRYPOINT ["/opt/chromium/asan-linux-release-681094/chrome"]
