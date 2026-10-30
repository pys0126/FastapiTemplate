#!/usr/bin/env bash

set -euo pipefail

APP_NAME="${APP_NAME:-fastapi[uvicorn]}"
APP_MODE="${APP_MODE:-pro}"
RUNNER="${RUNNER:-auto}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ENTRY="${APP_ENTRY:-${SCRIPT_DIR}/main.py}"
RUNTIME_DIR="${RUNTIME_DIR:-${SCRIPT_DIR}}"
PID_FILE="${PID_FILE:-${RUNTIME_DIR}/${APP_NAME}.pid}"
LOG_DIR="${LOG_DIR:-${SCRIPT_DIR}/logs}"
LOG_FILE="${LOG_FILE:-${LOG_DIR}/process.log}"
STOP_TIMEOUT="${STOP_TIMEOUT:-15}"
LOG_LINES="${LOG_LINES:-100}"

RUN_COMMAND=()
RUNNER_LABEL=""

usage() {
  cat <<EOF
Usage: $(basename "$0") {start|stop|kill|restart|status|logs}

Commands:
  start    Start ${APP_NAME}.
  stop     Gracefully stop ${APP_NAME}.
  kill     Force stop ${APP_NAME}.
  restart  Restart the service.
  status   Show current process status.
  logs     Follow the process log.

Runner:
  RUNNER=auto  Use PYTHON_BIN, .venv, venv, then python3 (default).
  RUNNER=uv    Use uv with requirements.txt.

Overrides:
  PYTHON_BIN=/path/to/python
  APP_ENTRY=/path/to/main.py
  APP_MODE=pro
  APP_CONFIG=/path/to/config.yaml
  PID_FILE=/path/to/app.pid
  LOG_DIR=/path/to/logs
  STOP_TIMEOUT=15
EOF
}


message() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S%z')" "$*"
}


resolve_runner() {
  if [[ "${RUNNER}" == "uv" ]]; then
    command -v uv >/dev/null 2>&1 || {
      echo "uv not found in PATH." >&2
      return 1
    }
    RUN_COMMAND=(
      uv run
      --with-requirements "${SCRIPT_DIR}/requirements.txt"
      python
    )
    RUNNER_LABEL="uv"
    return
  fi

  [[ "${RUNNER}" == "auto" ]] || {
    echo "RUNNER must be auto or uv, got: ${RUNNER}" >&2
    return 1
  }

  if [[ -n "${PYTHON_BIN:-}" ]]; then
    RUN_COMMAND=("${PYTHON_BIN}")
    RUNNER_LABEL="${PYTHON_BIN}"
  elif [[ -x "${SCRIPT_DIR}/.venv/bin/python" ]]; then
    RUN_COMMAND=("${SCRIPT_DIR}/.venv/bin/python")
    RUNNER_LABEL=".venv/bin/python"
  elif [[ -x "${SCRIPT_DIR}/venv/bin/python" ]]; then
    RUN_COMMAND=("${SCRIPT_DIR}/venv/bin/python")
    RUNNER_LABEL="venv/bin/python"
  else
    RUN_COMMAND=(python3)
    RUNNER_LABEL="python3"
  fi

  command -v "${RUN_COMMAND[0]}" >/dev/null 2>&1 || {
    echo "Python executable not found: ${RUN_COMMAND[0]}" >&2
    return 1
  }
}


read_pid() {
  [[ -f "${PID_FILE}" ]] && awk 'NR == 1 {print $1}' "${PID_FILE}"
}


is_running() {
  local pid
  pid="$(read_pid 2>/dev/null || true)"
  [[ "${pid}" =~ ^[1-9][0-9]*$ ]] && kill -0 "${pid}" >/dev/null 2>&1
}


remove_stale_pid() {
  if [[ -f "${PID_FILE}" ]] && ! is_running; then
    rm -f "${PID_FILE}"
  fi
}


start_app() {
  [[ -f "${APP_ENTRY}" ]] || {
    echo "App entry not found: ${APP_ENTRY}" >&2
    return 1
  }
  local config_file="${APP_CONFIG:-${SCRIPT_DIR}/config.yaml}"
  [[ -f "${config_file}" ]] || {
    echo "Config file not found: ${config_file}" >&2
    return 1
  }
  # 启动脚本会切换工作目录，先将自定义配置路径转成绝对路径。
  APP_CONFIG="$(cd "$(dirname "${config_file}")" && pwd)/$(basename "${config_file}")"
  export APP_CONFIG
  resolve_runner
  mkdir -p "${RUNTIME_DIR}" "${LOG_DIR}"
  remove_stale_pid

  if is_running; then
    message "${APP_NAME} is already running. pid=$(read_pid)"
    return
  fi

  cd "${SCRIPT_DIR}"
  nohup env PYTHONUNBUFFERED=1 \
    "${RUN_COMMAND[@]}" "${APP_ENTRY}" "${APP_MODE}" \
    >> "${LOG_FILE}" 2>&1 &
  local pid="$!"
  echo "${pid}" > "${PID_FILE}"
  sleep 1

  if is_running; then
    message "${APP_NAME} started. pid=${pid}, runner=${RUNNER_LABEL}"
    echo "log: ${LOG_FILE}"
    return
  fi

  rm -f "${PID_FILE}"
  message "${APP_NAME} failed to start. Check ${LOG_FILE}"
  return 1
}


stop_app() {
  remove_stale_pid
  if ! is_running; then
    message "${APP_NAME} is not running."
    return
  fi

  local pid
  pid="$(read_pid)"
  message "Stopping ${APP_NAME}. pid=${pid}"
  kill -TERM "${pid}" >/dev/null 2>&1 || true

  local elapsed=0
  while kill -0 "${pid}" >/dev/null 2>&1 && (( elapsed < STOP_TIMEOUT )); do
    sleep 1
    elapsed=$((elapsed + 1))
  done

  if kill -0 "${pid}" >/dev/null 2>&1; then
    message "Stop timed out. Run './$(basename "$0") kill'."
    return 1
  fi

  rm -f "${PID_FILE}"
  message "${APP_NAME} stopped."
}


kill_app() {
  remove_stale_pid
  if ! is_running; then
    message "${APP_NAME} is not running."
    return
  fi

  local pid
  pid="$(read_pid)"
  pkill -KILL -P "${pid}" >/dev/null 2>&1 || true
  kill -KILL "${pid}" >/dev/null 2>&1 || true
  rm -f "${PID_FILE}"
  message "${APP_NAME} was force stopped. pid=${pid}"
}


status_app() {
  remove_stale_pid
  if is_running; then
    echo "${APP_NAME} is running. pid=$(read_pid)"
    echo "log: ${LOG_FILE}"
  else
    echo "${APP_NAME} is not running."
  fi
}


follow_logs() {
  mkdir -p "${LOG_DIR}"
  touch "${LOG_FILE}"
  tail -n "${LOG_LINES}" -f "${LOG_FILE}"
}


case "${1:-}" in
  start) start_app ;;
  stop) stop_app ;;
  kill) kill_app ;;
  restart) stop_app && start_app ;;
  status) status_app ;;
  logs) follow_logs ;;
  -h|--help|help|"") usage ;;
  *)
    echo "Unknown command: $1" >&2
    usage >&2
    exit 1
    ;;
esac
