# Firefox Nightly — for WebNN research
#
# Installs the latest Firefox Nightly from Mozilla's APT repository.
#
# Build:
#   docker build -f examples/firefox-nightly.Dockerfile -t firefox-nightly .
#
# Verify:
#   docker run --rm firefox-nightly --version
#
# Run PoC:
#   docker run --rm --shm-size=2g \
#     -v /path/to/poc.html:/tmp/poc.html:ro \
#     firefox-nightly \
#     --headless --no-remote file:///tmp/poc.html

FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# ── Runtime dependencies ──────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libdbus-glib-1-2 \
        libdrm2 \
        libgbm1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libxrender1 \
        libxt6 \
        libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# ── Install Firefox Nightly from Mozilla APT repo ─────────────────────────
RUN install -d -m 0755 /etc/apt/keyrings /etc/apt/preferences.d /etc/apt/sources.list.d && \
    curl -fsSL https://packages.mozilla.org/apt/repo-signing-key.gpg | \
        gpg --dearmor --no-tty -o /etc/apt/keyrings/packages.mozilla.org.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/packages.mozilla.org.gpg] https://packages.mozilla.org/apt mozilla main" | \
        tee /etc/apt/sources.list.d/packages.mozilla.org.list > /dev/null && \
    printf 'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\n' | \
        tee /etc/apt/preferences.d/mozilla > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends firefox-nightly && \
    rm -rf /var/lib/apt/lists/*

# ── Create profile with prefs ─────────────────────────────────────────────
RUN mkdir -p /tmp/ff-profile && \
    printf '\
user_pref("browser.shell.checkDefaultBrowser", false);\n\
user_pref("datareporting.policy.dataSubmissionEnabled", false);\n\
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);\n\
user_pref("browser.aboutConfig.showWarning", false);\n\
user_pref("browser.dom.window.dump.enabled", true);\n\
user_pref("devtools.console.stdout.content", true);\n\
user_pref("dom.webnn.enabled", true);\n\
user_pref("dom.webgpu.enabled", true);\n\
' > /tmp/ff-profile/user.js

# Smoke test
RUN firefox-nightly --version 2>/dev/null || true

ENTRYPOINT ["firefox-nightly", "-profile", "/tmp/ff-profile", "--headless", "--no-remote"]
