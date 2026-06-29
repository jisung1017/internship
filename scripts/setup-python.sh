#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.14}"
RESET_VENV="${RESET_VENV:-0}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
export UV_CACHE_DIR="${UV_CACHE_DIR:-${PROJECT_ROOT}/.uv-cache}"
export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-${PROJECT_ROOT}/.uv-python}"

info() {
  printf '[setup] %s\n' "$1"
}

fail() {
  printf '[setup] error: %s\n' "$1" >&2
  exit 1
}

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return
  fi

  info "uv가 없어 설치를 시도합니다."

  if ! command -v curl >/dev/null 2>&1; then
    fail "curl이 없어 uv를 자동 설치할 수 없습니다. https://docs.astral.sh/uv/ 에서 uv를 먼저 설치해 주세요."
  fi

  curl -LsSf https://astral.sh/uv/install.sh | sh

  export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:${PATH}"

  if ! command -v uv >/dev/null 2>&1; then
    fail "uv 설치 후에도 실행 파일을 찾지 못했습니다. 터미널을 다시 열거나 PATH에 uv 설치 경로를 추가해 주세요."
  fi
}

venv_python_version() {
  "${VENV_DIR}/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
}

cd "${PROJECT_ROOT}"

ensure_uv

info "uv cache: ${UV_CACHE_DIR}"
info "uv Python install dir: ${UV_PYTHON_INSTALL_DIR}"
info "Python ${PYTHON_VERSION} 설치 여부를 확인합니다."
uv python install "${PYTHON_VERSION}"

info ".python-version을 ${PYTHON_VERSION}(으)로 맞춥니다."
uv python pin "${PYTHON_VERSION}"

if [ -d "${VENV_DIR}" ] && [ "${RESET_VENV}" = "1" ]; then
  info "RESET_VENV=1 이므로 기존 .venv를 삭제합니다."
  rm -rf "${VENV_DIR}"
fi

if [ -x "${VENV_DIR}/bin/python" ]; then
  CURRENT_VERSION="$(venv_python_version)"
  if [ "${CURRENT_VERSION}" != "${PYTHON_VERSION}" ]; then
    fail ".venv는 Python ${CURRENT_VERSION}입니다. RESET_VENV=1 scripts/setup-python.sh 로 재생성해 주세요."
  fi
  info "기존 .venv가 이미 Python ${CURRENT_VERSION}을 사용합니다."
else
  info "Python ${PYTHON_VERSION} 가상환경을 생성합니다."
  uv venv --python "${PYTHON_VERSION}" "${VENV_DIR}"
fi

if [ -f "${PROJECT_ROOT}/uv.lock" ]; then
  info "uv.lock 기준으로 의존성을 동기화합니다."
  uv sync --python "${PYTHON_VERSION}" --no-install-project
elif [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
  info "requirements.txt 기준으로 의존성을 설치합니다."
  uv pip install --python "${VENV_DIR}/bin/python" -r requirements.txt
else
  info "설치할 의존성 파일이 없어 가상환경만 준비합니다."
fi

info "완료: source .venv/bin/activate"
info "확인: python --version"
