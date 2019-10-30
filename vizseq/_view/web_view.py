# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Tuple, Iterable
import math
import os
import os.path as op
from glob import glob
import json

from vizseq._data import (VizSeqTaskConfigManager, VizSeqGlobalConfigManager,
                          VizSeqStats, set_g_cred_path, VizSeqTableExporter,
                          VizSeqNGrams, VizSeqTokenization)
from vizseq.scorers import get_scorer_name, get_scorer_ids_and_names
from .data_view import VizSeqDataPageView, VizSeqPageData
from .mem_cached_data_getters import (_get_src, _get_ref, _get_tag, _get_hypo,
                                      _get_scores)


class VizSeqWebView(object):
    def __init__(
            self, data_root: str, task: str = '', models: List[str] = (),
            page_sz: int = 10, page_no: int = 1, query: str = '',
            sorting: int = 0, sorting_metric: str = ''
    ):
        if not op.isdir(data_root):
            raise NotADirectoryError(f'{data_root} is not a valid data root.')
        self.data_root = data_root
        self.task = task
        self.dir_path = op.join(data_root, task)
        self.models = models
        self.page_sz = page_sz
        self.page_no = page_no
        self.all_metrics_and_names = [
            list(e) for e in get_scorer_ids_and_names()
        ]

        self.cfg = VizSeqTaskConfigManager(self.dir_path)
        self.metrics = self.cfg.metrics
        if len(self.cfg.task_name) == 0:
            self.cfg.set_task_name(task)
        self.task_name = self.cfg.task_name
        self.description = self.cfg.description
        self.tokenization = self.cfg.tokenization

        self.all_tokenization = [e.name for e in VizSeqTokenization]
        self.query = query
        self.sorting = sorting
        self.sorting_metric = sorting_metric
        set_g_cred_path(VizSeqGlobalConfigManager().g_cred_path)
        src = _get_src(self.dir_path)
        self.src_has_text = src.has_text
        self.enum_src_names_and_types = self.get_enum(
            zip(src.names, [t.name for t in src.data_types])
        )
        ref = _get_ref(self.dir_path)
        self.enum_ref_names = self.get_enum(ref.names)

    @classmethod
    def get_enum(cls, data: Iterable) -> List:
        return VizSeqDataPageView.get_enum(data)

    def set_task_name(self, task_name: str):
        self.cfg.set_task_name(task_name)

    def get_stats(self):
        src = _get_src(self.dir_path)
        ref = _get_ref(self.dir_path)
        tag = _get_tag(self.dir_path)
        return json.dumps(VizSeqStats.get(src, ref, tag).to_dict())

    @classmethod
    def get_enum_tasks_and_names_and_enum_models(
            cls, data_root: str
    ) -> List[Tuple[int, str, str, List[Tuple[int, str]]]]:
        dirs = [
            d for d in os.listdir(data_root)
            if op.isdir(op.join(data_root, d))
        ]
        enum_tasks_and_names_and_enum_models = []
        c = 0
        for d in dirs:
            dir_path = op.join(data_root, d)
            task_name = VizSeqTaskConfigManager(dir_path).task_name
            if len(task_name) == 0:
                task_name = d
            paths = sorted(glob(op.join(dir_path, 'pred_*.txt')))
            if len(paths) == 0:
                continue
            models = [
                (i, str(op.splitext(op.basename(p))[0]).split('_', 1)[1])
                for i, p in enumerate(paths)
            ]
            enum_tasks_and_names_and_enum_models.append(
                (c, d, task_name, models)
            )
            c += 1
        return enum_tasks_and_names_and_enum_models

    def get_tag_set(self) -> List[str]:
        return list(_get_tag(self.dir_path).unique())

    def get_tags(self):
        return _get_tag(self.dir_path).text

    def get_enum_metrics_and_names(self):
        return [[i, s, get_scorer_name(s)] for i, s in enumerate(self.metrics)]

    def get_scores(self):
        tag_set = self.get_tag_set()

        corpus_scores = {s: {} for s in self.metrics}
        group_scores = {s: {t: {} for t in tag_set} for s in self.metrics}
        sent_scores = {s: {} for s in self.metrics}
        for s in self.metrics:
            for i, m in enumerate(self.models):
                cur = _get_scores(self.dir_path, s, m)
                cur = [cur.corpus_score, cur.group_scores, cur.sent_scores]
                corpus_scores[s][m] = cur[0]
                for t in tag_set:
                    group_scores[s][t][m] = cur[1][t]
                sent_scores[s][m] = cur[2]

        scores = {
            'corpus_scores': corpus_scores,
            'group_scores': group_scores,
            'sent_scores': sent_scores,
            'corpus_group_scores_latex': self.latex_corpus_group_scores(
                corpus_scores, group_scores
            ),
            'corpus_group_scores_csv': self.csv_corpus_group_scores(
                corpus_scores, group_scores
            )
        }
        return json.dumps(scores)

    def get_n_grams(self, k=50):
        src = _get_src(self.dir_path)
        if src.has_text:
            ngrams = VizSeqNGrams.extract(src, k=k)
        else:
            ref = _get_ref(self.dir_path)
            ngrams = VizSeqNGrams.extract(ref, k=k)
        return json.dumps(ngrams)

    def get_page_data(self) -> VizSeqPageData:
        dir_path = op.join(self.data_root, self.task)
        src = _get_src(dir_path)
        ref = _get_ref(dir_path)
        hypo = _get_hypo(dir_path, self.models)
        return VizSeqDataPageView.get(
            src, ref, hypo, self.page_sz, self.page_no, metrics=self.metrics,
            query=self.query, sorting=self.sorting,
            sorting_metric=self.sorting_metric, need_lang_tags=True
        )

    def get_page_data_with_pagination(self) -> str:
        page_data = self.get_page_data()._asdict()
        page_data['pagination'] = self.get_pagination(
            page_data['total_examples'], self.page_sz, self.page_no
        )
        return json.dumps(page_data)

    def get_pagination(
            self, total_examples: int, page_sz: int, page_no: int,
            nav_group_sz: int = 3
    ) -> Tuple[List[int], List[int], List[int], List[int]]:
        assert page_sz > 0 and page_no > 0
        n_pages = math.ceil(total_examples / page_sz)
        _page_no = min(max(1, page_no), n_pages)

        group1_end = min(nav_group_sz, _page_no - nav_group_sz - 1)
        group1 = list(range(1, group1_end + 1))

        group2_start = max(1, _page_no - nav_group_sz)
        group2_end = _page_no - 1
        group2 = list(range(group2_start, group2_end + 1))

        group3_start = _page_no + 1
        group3_end = min(n_pages, _page_no + nav_group_sz)
        group3 = list(range(group3_start, group3_end + 1))

        group4_start = max(
                _page_no + nav_group_sz + 1, n_pages - nav_group_sz + 1
            )
        group4 = list(range(group4_start, n_pages + 1))

        return group1, group2, group3, group4

    @classmethod
    def _export_corpus_group_scores(
            cls, corpus_scores, group_scores, export_func: callable
    ):
        assert set(corpus_scores.keys()) == set(group_scores.keys())
        metrics = corpus_scores.keys()
        exported = {}
        for s in metrics:
            cur_scores = {'All': corpus_scores[s]}
            cur_scores.update(group_scores[s])
            exported[s] = export_func(cur_scores)
        return exported

    @classmethod
    def latex_corpus_group_scores(cls, corpus_scores, group_scores):
        return cls._export_corpus_group_scores(
            corpus_scores, group_scores, VizSeqTableExporter.to_latex
        )

    @classmethod
    def csv_corpus_group_scores(cls, corpus_scores, group_scores):
        return cls._export_corpus_group_scores(
            corpus_scores, group_scores, VizSeqTableExporter.to_csv
        )

    @property
    def page_sizes(self):
        return [10, 25, 50, 100]
