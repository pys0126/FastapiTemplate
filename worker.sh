#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ARQ worker复用service.sh的启停和日志能力。
export APP_NAME="${ARQ_APP_NAME:-fastapi-arq}"
export APP_ENTRY="${ARQ_APP_ENTRY:-${SCRIPT_DIR}/main.py}"
export APP_MODE="${ARQ_APP_MODE:-worker}"
export RUNTIME_DIR="${ARQ_RUNTIME_DIR:-${SCRIPT_DIR}}"
export PID_FILE="${ARQ_PID_FILE:-${RUNTIME_DIR}/${APP_NAME}.pid}"
export LOG_DIR="${ARQ_LOG_DIR:-${SCRIPT_DIR}/logs}"
export LOG_FILE="${ARQ_LOG_FILE:-${LOG_DIR}/arq-process.log}"
export RUNNER="${ARQ_RUNNER:-${RUNNER:-auto}}"

exec "${SCRIPT_DIR}/service.sh" "$@"
