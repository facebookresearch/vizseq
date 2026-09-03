#!/usr/bin/env bash
# Copyright (c) Facebook, Inc. and its affiliates.

set -euo pipefail

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
python_cmd=()
if [ -n "${PYTHON:-}" ]; then
  read -r -a python_cmd <<< "${PYTHON}"
elif command -v python3 >/dev/null 2>&1; then
  python_cmd=(python3)
elif command -v python >/dev/null 2>&1; then
  python_cmd=(python)
elif command -v py >/dev/null 2>&1; then
  python_cmd=(py)
else
  echo "Python 3.11 or newer is required." >&2
  exit 1
fi
if [ "${#python_cmd[@]}" -eq 0 ]; then
  echo "Python interpreter not found: PYTHON is empty or whitespace only." >&2
  exit 1
fi
if ! command -v "${python_cmd[0]}" >/dev/null 2>&1; then
  echo "Python interpreter not found: ${python_cmd[0]}" >&2
  exit 1
fi
if ! "${python_cmd[@]}" -c \
    'import sys; sys.exit(sys.version_info < (3, 11))'; then
  echo "Python 3.11 or newer is required." >&2
  exit 1
fi

script_path="${ROOT}/get_example_data.py"
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    if ! command -v cygpath >/dev/null 2>&1; then
      echo "cygpath is required to run this wrapper on Windows." >&2
      exit 1
    fi
    if ! converted_path="$(cygpath -w "${script_path}")"; then
      echo "Could not convert the downloader path for Windows." >&2
      exit 1
    fi
    script_path="${converted_path}"
    if [ -z "${script_path}" ]; then
      echo "Could not convert the downloader path for Windows." >&2
      exit 1
    fi
    ;;
esac

exec "${python_cmd[@]}" "${script_path}" "$@"
