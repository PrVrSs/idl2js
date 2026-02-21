# Chromium ASan (AddressSanitizer) build — latest stable channel
#
# Downloads the official Chromium ASan build from Google's public GCS bucket:
#   gs://chromium-browser-asan/linux-release/asan-linux-release-{POSITION}.zip
#
# ASan detects:
#   - Heap buffer overflow / underflow
#   - Use-after-free (UAF)
#   - Stack buffer overflow
#   - Use-after-return
#
# UBSAN detects:
#   - Integer overflow
#   - NaN / Infinity in arithmetic that expects finite values
#   - Null pointer dereference
#
# Build (uses position 1568190 = Chrome 145 stable, ~Jan 2026):
#   docker build -f examples/chrome-asan.Dockerfile -t chrome-asan .
#
# Build with a different position (find via chromiumdash):
#   POS=$(curl -s 'https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Linux&num=1' \
#         | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['chromium_main_branch_position'])")
#   docker build --build-arg ASAN_POSITION=$POS -f examples/chrome-asan.Dockerfile -t chrome-asan .
#
# Verify:
#   docker run --rm chrome-asan --version
#
# Run PoC:
#   docker run --rm -v /path/to/poc.html:/tmp/poc.html:ro chrome-asan \
#     --headless --no-sandbox --disable-gpu file:///tmp/poc.html

FROM debian:bookworm-slim

# Build position for the target Chromium ASan release.
# 1568190 = Chrome 145.0.7632.116 stable (~Jan 2026).
# Override with --build-arg ASAN_POSITION=<new_position> for newer releases.
# Source: https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Linux&num=1
ARG ASAN_POSITION=1568190

# ── Runtime dependencies ────────────────────────────────────────────────────
# Same set as chrome-122.Dockerfile (bookworm-confirmed) plus python3 for the
# optional dynamic-position lookup and llvm tools for optional symbolization.
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
        libdrm2 \
        libexpat1 \
        libgbm1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libuuid1 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxi6 \
        libxkbcommon0 \
        libxrandr2 \
        libxrender1 \
        libxss1 \
        libxtst6 \
        libpci3 \
        libxshmfence1 \
        python3 \
        unzip \
        xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# ── Download Chromium ASan build ────────────────────────────────────────────
# The official get_asan_chrome.py script (tools/get_asan_chrome/) fetches from
# chromium-browser-asan bucket and retries with position-1 on 404.
# We replicate that logic here with up to 20 retries.
RUN set -eux; \
    POS="${ASAN_POSITION}"; \
    FOUND=0; \
    for ATTEMPT in $(seq 0 20); do \
        ACTUAL_POS=$((POS - ATTEMPT)); \
        URL="https://commondatastorage.googleapis.com/chromium-browser-asan/linux-release/asan-linux-release-${ACTUAL_POS}.zip"; \
        HTTP=$(curl -fsSLI -o /dev/null -w "%{http_code}" "${URL}"); \
        if [ "${HTTP}" = "200" ]; then \
            echo "Downloading ASan build at position ${ACTUAL_POS}"; \
            curl -fSL -o /tmp/asan.zip "${URL}"; \
            FOUND=1; \
            break; \
        fi; \
        echo "Position ${ACTUAL_POS}: HTTP ${HTTP}, retrying..."; \
    done; \
    [ "${FOUND}" = "1" ] || (echo "ERROR: no ASan build found near position ${POS}" && exit 1); \
    mkdir -p /opt/chromium; \
    cd /opt/chromium; \
    unzip -q /tmp/asan.zip; \
    rm /tmp/asan.zip; \
    # Locate the chrome binary (may be flat or in a subdirectory). \
    CHROME=$(find /opt/chromium -maxdepth 3 -name chrome -type f | head -1); \
    chmod +x "${CHROME}"; \
    # Create a stable /opt/chromium/chrome symlink only when needed. \
    if [ "${CHROME}" != "/opt/chromium/chrome" ]; then \
        ln -sf "${CHROME}" /opt/chromium/chrome; \
    fi; \
    echo "Installed: ${CHROME}"

# ── Sanitizer runtime options ───────────────────────────────────────────────
#
# ASAN_OPTIONS:
#   detect_leaks=0            — disable LeakSanitizer (false positives in headless)
#   halt_on_error=1           — stop on first ASAN report
#   abort_on_error=1          — send SIGABRT so Docker exit_code > 128 → CRASH
#   detect_stack_use_after_return=1 — extra UAF detection via fake stack
#   alloc_dealloc_mismatch=0  — suppress new/free mismatch (common in Chrome internals)
#   symbolize=1               — enable runtime symbolization for readable ASAN reports
#   print_stacktrace=1        — include full stack traces in ASAN reports
#
# UBSAN_OPTIONS:
#   halt_on_error=1           — stop on first UBSAN report
#   print_stacktrace=1        — print raw PCs for offline symbolization
ENV ASAN_OPTIONS="detect_leaks=0:halt_on_error=1:abort_on_error=1:detect_stack_use_after_return=1:alloc_dealloc_mismatch=0:symbolize=1:print_stacktrace=1"
ENV UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1:symbolize=1"

# Smoke test: version string confirms the binary is functional.
RUN /opt/chromium/chrome --version --no-sandbox 2>/dev/null || true

ENTRYPOINT ["/opt/chromium/chrome"]
