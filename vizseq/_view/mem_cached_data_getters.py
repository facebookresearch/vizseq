# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List
from functools import lru_cache
import os.path as op
from glob import glob

from vizseq._data import VizSeqDataSources
from vizseq.scorers import get_scorer


@lru_cache(maxsize=2)
def _get_src(dir_path: str):
    return VizSeqDataSources(sorted(glob(op.join(dir_path, 'src_*.*'))))


@lru_cache(maxsize=2)
def _get_ref(dir_path: str):
    return VizSeqDataSources(sorted(glob(op.join(dir_path, 'ref_*.txt'))))


@lru_cache(maxsize=2)
def _get_tag(dir_path: str):
    return VizSeqDataSources(
        sorted(glob(op.join(dir_path, 'tag_*.txt'))), text_merged=True
    )


@lru_cache(maxsize=2)
def __get_hypo(dir_path: str, models: str):
    if len(models) > 0:
        paths = [op.join(dir_path, f'pred_{m}.txt') for m in models.split(',')]
    else:
        paths = glob(op.join(dir_path, 'pred_*.txt'))
    return VizSeqDataSources(paths)


def _get_hypo(dir_path: str, models: List[str]):
    return __get_hypo(dir_path, ','.join(models))


@lru_cache(maxsize=64)
def _get_scores(dir_path: str, metric: str, model: str):
    hypo = _get_hypo(dir_path, [model])
    ref = _get_ref(dir_path)
    tag = _get_tag(dir_path)
    return get_scorer(metric)(corpus_level=True, sent_level=True).score(
        hypo.data[0].text, ref.text, tags=tag.text
    )
