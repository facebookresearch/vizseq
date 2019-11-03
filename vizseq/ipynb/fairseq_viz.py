# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
from typing import List, Optional

from vizseq.ipynb.core import (view_examples as _view_examples,
                               view_stats as _view_stats,
                               view_n_grams as _view_n_grams,
                               view_scores as _view_scores)
from vizseq._view import DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NO, VizSeqSortingType


def _get_data(generation_log_path: str):
    assert os.path.isfile(generation_log_path)
    sources, references, hypothesis = {}, {}, {}
    with open(generation_log_path) as f:
        for l in f:
            line = l.strip()
            if line.startswith('H-'):
                _id, _, sent = line.split('\t', 2)
                hypothesis[_id[2:]] = sent
            elif line.startswith('T-'):
                _id, sent = line.split('\t', 1)
                references[_id[2:]] = sent
            elif line.startswith('S-'):
                _id, sent = line.split('\t', 1)
                sources[_id[2:]] = sent
    assert set(sources.keys()) == set(references.keys()) == set(
        hypothesis.keys())
    ids = sorted(sources.keys())
    sources = [sources[i] for i in ids]
    references = [references[i] for i in ids]
    hypothesis = [hypothesis[i] for i in ids]
    return {'0': sources}, {'0': references}, {'fairseq': hypothesis}


# TODO: visualize alignment by attention
def view_examples(
        generation_log_path: str,
        metrics: Optional[List[str]] = None,
        query: str = '',
        page_sz: int = DEFAULT_PAGE_SIZE,
        page_no: int = DEFAULT_PAGE_NO,
        sorting: VizSeqSortingType = VizSeqSortingType.original,
        need_g_translate: bool = False):
    sources, references, hypothesis = _get_data(generation_log_path)
    return _view_examples(
        sources, references, hypothesis, metrics, query, page_sz=page_sz,
        page_no=page_no, sorting=sorting, need_g_translate=need_g_translate
    )


def view_stats(generation_log_path: str):
    sources, references, hypothesis = _get_data(generation_log_path)
    _view_stats(sources, references, hypothesis)


def view_n_grams(generation_log_path: str, k: int = 64):
    sources, references, hypothesis = _get_data(generation_log_path)
    return _view_n_grams(sources, k=k)


def view_scores(generation_log_path: str, metrics: List[str]):
    sources, references, hypothesis = _get_data(generation_log_path)
    return _view_scores(references, hypothesis, metrics)
