#!/usr/bin/env bash
#
# CVE-2019-13720 targeted fuzzer — end-to-end runner.
#
# Builds the ASAN-instrumented Chromium 77 Docker image (if missing),
# then runs the fuzzer inside it until a crash is detected.
#
# Usage:
#   ./examples/run_cve_2019_13720.sh              # defaults
#   ./examples/run_cve_2019_13720.sh --runs 20    # more attempts
#   ./examples/run_cve_2019_13720.sh --skip-build # image already exists

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

IMAGE="chrome77-asan"
DOCKERFILE="$SCRIPT_DIR/chrome77-asan.Dockerfile"
CHROME_PATH="/opt/chromium/asan-linux-release-681094/chrome"
TIMEOUT_MS=60000
RUNS=10
MAX_SAMPLES=200
SKIP_BUILD=false

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --image NAME        Docker image name (default: $IMAGE)
  --timeout MS        Per-run timeout in ms (default: $TIMEOUT_MS)
  --runs N            Execution attempts per PoC (default: $RUNS)
  --max-samples N     Fuzzer samples to generate (default: $MAX_SAMPLES)
  --skip-build        Skip Docker image build
  -h, --help          Show this help
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --image)       IMAGE="$2";       shift 2 ;;
        --timeout)     TIMEOUT_MS="$2";  shift 2 ;;
        --runs)        RUNS="$2";        shift 2 ;;
        --max-samples) MAX_SAMPLES="$2"; shift 2 ;;
        --skip-build)  SKIP_BUILD=true;  shift   ;;
        -h|--help)     usage ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# --- Preflight checks -------------------------------------------------------

if ! command -v docker &>/dev/null; then
    echo "ERROR: docker is not installed or not in PATH" >&2
    exit 1
fi

if ! docker info &>/dev/null; then
    echo "ERROR: Docker daemon is not running" >&2
    exit 1
fi

if ! command -v poetry &>/dev/null; then
    echo "ERROR: poetry is not installed or not in PATH" >&2
    exit 1
fi

# --- Build Docker image (if needed) -----------------------------------------

if [[ "$SKIP_BUILD" == false ]]; then
    if docker image inspect "$IMAGE" &>/dev/null; then
        echo "[*] Docker image '$IMAGE' already exists, skipping build."
        echo "    Use 'docker rmi $IMAGE' to force rebuild."
    else
        echo "[*] Building Docker image '$IMAGE' (ASAN Chromium 77)..."
        echo "    This downloads a ~3.5 GB ASAN build — may take a while."
        echo ""
        docker build -f "$DOCKERFILE" -t "$IMAGE" "$PROJECT_DIR"
        echo ""
        echo "[*] Image built successfully."
    fi
else
    if ! docker image inspect "$IMAGE" &>/dev/null; then
        echo "ERROR: --skip-build specified but image '$IMAGE' does not exist" >&2
        exit 1
    fi
    echo "[*] Skipping build, using existing image '$IMAGE'."
fi

# --- Verify Chrome works inside the container --------------------------------

echo "[*] Verifying Chromium inside container..."
VERSION=$(docker run --rm --entrypoint "$CHROME_PATH" "$IMAGE" --version 2>/dev/null || true)
if [[ -z "$VERSION" ]]; then
    echo "ERROR: Could not get Chromium version from container" >&2
    exit 1
fi
echo "    $VERSION"

# --- Run the fuzzer ----------------------------------------------------------

echo ""
echo "[*] Running CVE-2019-13720 fuzzer"
echo "    Image:       $IMAGE"
echo "    Chrome:      $CHROME_PATH"
echo "    Timeout:     ${TIMEOUT_MS}ms per run"
echo "    Runs:        $RUNS"
echo "    Max samples: $MAX_SAMPLES"
echo ""

cd "$PROJECT_DIR"
poetry run python examples/cve_2019_13720_fuzzer.py \
    --docker-image "$IMAGE" \
    --chrome "$CHROME_PATH" \
    --timeout "$TIMEOUT_MS" \
    --runs "$RUNS" \
    --max-samples "$MAX_SAMPLES"
