# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os.path as op
from collections import Counter
from typing import List, Optional, Union

from vizseq.ipynb.core import (view_examples as _view_examples,
                               view_stats as _view_stats,
                               view_n_grams as _view_n_grams,
                               view_scores as _view_scores)
from vizseq._view import DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NO, VizSeqSortingType


def _get_data(log_path_or_paths: Union[str, List[str]]):
    if isinstance(log_path_or_paths, str):
        log_path_or_paths = [log_path_or_paths]
    ids, src, ref, hypo = None, None, None, {}
    names = Counter()
    for k, log_path in enumerate(log_path_or_paths):
        assert op.isfile(log_path)
        cur_src, cur_ref, cur_hypo = {}, {}, {}
        with open(log_path) as f:
            for l in f:
                line = l.strip()
                if line.startswith('H-'):
                    _id, _, sent = line.split('\t', 2)
                    cur_hypo[_id[2:]] = sent
                elif line.startswith('T-'):
                    _id, sent = line.split('\t', 1)
                    cur_ref[_id[2:]] = sent
                elif line.startswith('S-'):
                    _id, sent = line.split('\t', 1)
                    cur_src[_id[2:]] = sent
        cur_ids = sorted(cur_src.keys())
        assert set(cur_ids) == set(cur_ref.keys()) == set(cur_hypo.keys())
        cur_src = [cur_src[i] for i in cur_ids]
        cur_ref = [cur_ref[i] for i in cur_ids]
        if k == 0:
            ids, src, ref = cur_ids, cur_src, cur_ref
        else:
            assert set(ids) == set(cur_ids) and set(src) == set(cur_src)
            assert set(ref) == set(cur_ref)
        name = op.splitext(op.basename(log_path))[0]
        names.update([name])
        if names[name] > 1:
            name += f'.{names[name]}'
        hypo[name] = [cur_hypo[i] for i in cur_ids]
    return {'0': src}, {'0': ref}, hypo


# TODO: visualize alignment by attention
def view_examples(
        log_path_or_paths: Union[str, List[str]],
        metrics: Optional[List[str]] = None,
        query: str = '',
        page_sz: int = DEFAULT_PAGE_SIZE,
        page_no: int = DEFAULT_PAGE_NO,
        sorting: VizSeqSortingType = VizSeqSortingType.original,
        need_g_translate: bool = False,
        disable_alignment: bool = False
):
    sources, references, hypothesis = _get_data(log_path_or_paths)
    return _view_examples(
        sources, references, hypothesis, metrics, query, page_sz=page_sz,
        page_no=page_no, sorting=sorting, need_g_translate=need_g_translate,
        disable_alignment=disable_alignment
    )


def view_stats(log_path: str):
    sources, references, hypothesis = _get_data(log_path)
    _view_stats(sources, references, hypothesis)


def view_n_grams(log_path: str, k: int = 64):
    sources, _, _ = _get_data(log_path)
    return _view_n_grams(sources, k=k)


def view_scores(log_path: str, metrics: List[str]):
    sources, references, hypothesis = _get_data(log_path)
    return _view_scores(references, hypothesis, metrics)
