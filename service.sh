#!/usr/bin/env bash

set -euo pipefail

APP_NAME="fastapi[uvicorn]"
APP_MODE="pro"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ENTRY="${APP_ENTRY:-${SCRIPT_DIR}/main.py}"
RUNTIME_DIR="${RUNTIME_DIR:-${SCRIPT_DIR}}"
PID_FILE="${PID_FILE:-${RUNTIME_DIR}/${APP_NAME}.pid}"
LOG_DIR="${LOG_DIR:-${SCRIPT_DIR}/logs}"
LOG_FILE="${LOG_FILE:-${LOG_DIR}/process.log}"

if [[ -x "${SCRIPT_DIR}/venv/bin/python" ]]; then
  PYTHON_BIN="${PYTHON_BIN:-${SCRIPT_DIR}/venv/bin/python}"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
fi

usage() {
  cat <<EOF
Usage: $(basename "$0") {start|stop|kill|restart|status}

Commands:
  start    Start ${APP_NAME} in production mode.
  stop     Gracefully stop the running process.
  kill     Force kill the running process.
  restart  Restart the service.
  status   Show current process status.

Environment overrides:
  PYTHON_BIN=/path/to/python
  APP_ENTRY=/path/to/main.py
  PID_FILE=/path/to/app.pid
  LOG_DIR=/path/to/logs
  LOG_FILE=/path/to/app.log
EOF
}

ensure_dirs() {
  mkdir -p "${RUNTIME_DIR}" "${LOG_DIR}"
}

read_pid() {
  if [[ -f "${PID_FILE}" ]]; then
    tr -d '[:space:]' < "${PID_FILE}"
  fi
}

is_running() {
  local pid="${1:-}"
  [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1
}

remove_stale_pid() {
  local pid
  pid="$(read_pid || true)"
  if [[ -n "${pid}" ]] && ! is_running "${pid}"; then
    rm -f "${PID_FILE}"
  fi
}

child_pids() {
  local pid="${1}"
  pgrep -P "${pid}" 2>/dev/null || true
}

start_app() {
  ensure_dirs
  remove_stale_pid

  local pid
  pid="$(read_pid || true)"
  if is_running "${pid}"; then
    echo "${APP_NAME} is already running. pid=${pid}"
    return 0
  fi

  if [[ ! -f "${APP_ENTRY}" ]]; then
    echo "App entry not found: ${APP_ENTRY}" >&2
    exit 1
  fi

  if [[ ! -f "${SCRIPT_DIR}/config.yaml" ]]; then
    echo "config.yaml not found. Create it from config-template.yaml before starting." >&2
    exit 1
  fi

  cd "${SCRIPT_DIR}"
  nohup "${PYTHON_BIN}" "${APP_ENTRY}" "${APP_MODE}" >> "${LOG_FILE}" 2>&1 &
  pid="$!"
  echo "${pid}" > "${PID_FILE}"

  sleep 1
  if is_running "${pid}"; then
    echo "${APP_NAME} started. pid=${pid}, log=${LOG_FILE}"
  else
    rm -f "${PID_FILE}"
    echo "${APP_NAME} failed to start. Check log: ${LOG_FILE}" >&2
    exit 1
  fi
}

stop_app() {
  remove_stale_pid

  local pid
  pid="$(read_pid || true)"
  if ! is_running "${pid}"; then
    echo "${APP_NAME} is not running."
    return 0
  fi

  echo "Stopping ${APP_NAME}. pid=${pid}"
  kill "${pid}" >/dev/null 2>&1 || true

  for _ in {1..30}; do
    if ! is_running "${pid}"; then
      rm -f "${PID_FILE}"
      echo "${APP_NAME} stopped."
      return 0
    fi
    sleep 1
  done

  echo "${APP_NAME} did not stop within 30s. Use './$(basename "$0") kill' to force kill." >&2
  exit 1
}

kill_app() {
  remove_stale_pid

  local pid
  pid="$(read_pid || true)"
  if ! is_running "${pid}"; then
    echo "${APP_NAME} is not running."
    rm -f "${PID_FILE}"
    return 0
  fi

  echo "Force killing ${APP_NAME}. pid=${pid}"
  child_pids "${pid}" | xargs -r kill -9 2>/dev/null || true
  kill -9 "${pid}" >/dev/null 2>&1 || true
  rm -f "${PID_FILE}"
  echo "${APP_NAME} killed."
}

status_app() {
  remove_stale_pid

  local pid
  pid="$(read_pid || true)"
  if is_running "${pid}"; then
    echo "${APP_NAME} is running. pid=${pid}"
    local children
    children="$(child_pids "${pid}" | tr '\n' ' ' | sed 's/[[:space:]]*$//')"
    if [[ -n "${children}" ]]; then
      echo "worker pids: ${children}"
    fi
    echo "log: ${LOG_FILE}"
  else
    echo "${APP_NAME} is not running."
  fi
}

case "${1:-}" in
  start)
    start_app
    ;;
  stop)
    stop_app
    ;;
  kill)
    kill_app
    ;;
  restart)
    stop_app
    start_app
    ;;
  status)
    status_app
    ;;
  -h|--help|help|"")
    usage
    ;;
  *)
    echo "Unknown command: $1" >&2
    usage >&2
    exit 1
    ;;
esac
