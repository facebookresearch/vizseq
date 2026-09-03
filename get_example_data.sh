#!/usr/bin/env bash
# Copyright (c) Facebook, Inc. and its affiliates.

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ -n "${PYTHON:-}" ]; then
  python_cmd="${PYTHON}"
elif command -v python3 >/dev/null 2>&1; then
  python_cmd=python3
elif command -v python >/dev/null 2>&1; then
  python_cmd=python
elif command -v py >/dev/null 2>&1; then
  python_cmd=py
else
  echo "Python 3.11 or newer is required." >&2
  exit 1
fi
if ! command -v "${python_cmd}" >/dev/null 2>&1; then
  echo "Python interpreter not found: ${python_cmd}" >&2
  exit 1
fi

script_path="${ROOT}/get_example_data.py"
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    script_path="$(cygpath -w "${script_path}")"
    ;;
esac

exec "${python_cmd}" "${script_path}" "$@"
