#!/usr/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.

TASK=${1:-translation_wmt14_en_de_test}

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DESC_DIR="${ROOT}/examples/data"
FILENAME=${TASK}.zip

if [ ! -d "${DESC_DIR}/${TASK}" ]; then
  curl "https://dl.fbaipublicfiles.com/vizseq/examples/data/${FILENAME}" --output "${DESC_DIR}/${FILENAME}"
  unzip "${DESC_DIR}/${FILENAME}" -d "${DESC_DIR}"
  rm "${DESC_DIR}/${FILENAME}"
fi
