#!/usr/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
FILENAME=example_data.zip
wget https://dl.fbaipublicfiles.com/vizseq/${FILENAME} -O "${ROOT}/examples/${FILENAME}"
unzip "${ROOT}/examples/${FILENAME}"
rm "${ROOT}/examples/${FILENAME}"
