#!/usr/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.

TASK=${1:-translation_wmt14_en_de_test}

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
FILENAME=${TASK}.zip
curl "https://dl.fbaipublicfiles.com/vizseq/examples/data/${FILENAME}" --output "${ROOT}/examples/data/${FILENAME}"
unzip "${ROOT}/examples/data/${FILENAME}" -d "${ROOT}/examples/data"
rm "${ROOT}/examples/data/${FILENAME}"
