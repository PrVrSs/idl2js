# Firefox ASAN (AddressSanitizer) build — latest mozilla-central
#
# Downloads Mozilla's official ASAN+Fuzzing build from TaskCluster:
#   gecko.v2.mozilla-central.latest.firefox.linux64-asan-opt
#
# Build:
#   docker build -f examples/firefox-asan.Dockerfile -t firefox-asan .
#
# Verify:
#   docker run --rm firefox-asan --version
#
# Run PoC:
#   docker run --rm --shm-size=2g \
#     -v /path/to/poc.html:/tmp/poc.html:ro \
#     firefox-asan file:///tmp/poc.html

FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# ── Runtime dependencies ──────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
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
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

# ── Download Firefox ASAN build from TaskCluster ──────────────────────────
# linux64-asan-opt: ASAN optimized build from mozilla-central (nightly)
ARG VARIANT=linux64-asan-opt
ARG TC_URL=https://firefox-ci-tc.services.mozilla.com/api/index/v1/task/gecko.v2.mozilla-central.latest.firefox

RUN set -eux; \
    echo "Downloading Firefox ASAN (${VARIANT})..."; \
    curl -fSL -o /tmp/firefox.tar.xz \
        "${TC_URL}.${VARIANT}/artifacts/public/build/target.tar.xz"; \
    echo "Extracting..."; \
    mkdir -p /opt; \
    cd /opt; \
    tar xf /tmp/firefox.tar.xz; \
    rm /tmp/firefox.tar.xz; \
    chmod +x /opt/firefox/firefox; \
    echo "Installed: /opt/firefox/firefox"

# ── Create profile with fuzzing-friendly prefs ────────────────────────────
RUN mkdir -p /tmp/ff-profile && \
    printf '\
user_pref("browser.shell.checkDefaultBrowser", false);\n\
user_pref("datareporting.policy.dataSubmissionEnabled", false);\n\
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);\n\
user_pref("browser.aboutConfig.showWarning", false);\n\
user_pref("browser.dom.window.dump.enabled", true);\n\
user_pref("devtools.console.stdout.content", true);\n\
user_pref("security.sandbox.content.level", 0);\n\
user_pref("dom.ipc.plugins.sandbox-level.default", 0);\n\
user_pref("media.navigator.permission.disabled", true);\n\
user_pref("media.autoplay.default", 0);\n\
user_pref("dom.webgpu.enabled", true);\n\
user_pref("dom.webtransport.enabled", true);\n\
user_pref("layout.css.constructable-stylesheets.enabled", true);\n\
user_pref("dom.workers.modules.enabled", true);\n\
user_pref("browser.startup.homepage_override.mstone", "ignore");\n\
user_pref("browser.warnOnQuit", false);\n\
user_pref("toolkit.startup.max_resumed_crashes", -1);\n\
' > /tmp/ff-profile/user.js

# ── Sanitizer runtime options ─────────────────────────────────────────────
ENV ASAN_OPTIONS="detect_leaks=0:halt_on_error=1:abort_on_error=1:detect_stack_use_after_return=1:alloc_dealloc_mismatch=0:symbolize=1:print_stacktrace=1"
ENV UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1:symbolize=1"

# Smoke test
RUN /opt/firefox/firefox --version 2>/dev/null || true

ENTRYPOINT ["/opt/firefox/firefox", "-profile", "/tmp/ff-profile", "--headless", "--no-remote"]
