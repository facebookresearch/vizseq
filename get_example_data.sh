#!/usr/bin/env bash
# Copyright (c) Facebook, Inc. and its affiliates.

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
exec python3 "${ROOT}/get_example_data.py" "$@"
