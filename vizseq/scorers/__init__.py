# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from abc import abstractmethod
import importlib
import os
import sys
from pathlib import Path
import math
from typing import List, Optional, Set, Dict, Callable, NamedTuple, Tuple, Type
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count

import numpy as np
from tqdm import tqdm

from vizseq._utils.optional import map_optional

EXCLUDED_PREFIXES = ('.', '_')
PY_FILE_EXT = ('.py', '.pyc')
PRECISION = 3

SENT_SCORE_FN_TYPE = Callable[[List[str], List[List[str]], Dict], List[float]]


class VizSeqScore(NamedTuple):
    corpus_score: Optional[float] = None
    sent_scores: Optional[List[float]] = None
    group_scores: Optional[Dict[str, float]] = None

    @classmethod
    def make(
            cls, corpus_score: Optional[float],
            sent_scores: Optional[List[float]],
            group_scores: Optional[Dict[str, float]],
    ):
        return cls(
            map_optional(
                corpus_score, lambda x: np.round(x, PRECISION)
            ),
            map_optional(
                sent_scores, lambda x: [np.round(xx, PRECISION) for xx in x]
            ),
            map_optional(
                group_scores,
                lambda x: {k: np.round(v, PRECISION) for k, v in x.items()}
            ),
        )

    def to_dict(self):
        return {
            'corpus_score': self.corpus_score, 'sent_scores': self.sent_scores,
            'group_scores': self.group_scores,
        }


def _batch(a_list: list, n_batches: int):
    batch_size = len(a_list) // n_batches + int(len(a_list) % n_batches > 0)
    if batch_size > 0:
        for i in range(0, len(a_list), batch_size):
            yield a_list[i: min(i + batch_size, len(a_list))]


class VizSeqScorer(object):
    SAMPLES_PER_WORKER = 1000

    def __init__(
            self, corpus_level: bool = True, sent_level: bool = False,
            n_workers: Optional[int] = None, verbose: bool = False,
            extra_args: Optional[Dict[str, str]] = None
    ):
        self.corpus_level = corpus_level
        self.sent_level = sent_level
        self.n_workers = n_workers
        self._update_n_workers()
        self.verbose = verbose
        self.extra_args = extra_args

    @staticmethod
    def _unique(data: Optional[List[List[str]]]) -> Optional[Set[str]]:
        if data is None:
            return None
        unique_elements = set()
        for cur_list in data:
            unique_elements.update(cur_list)
        return unique_elements

    def _update_n_workers(self, n_samples: Optional[int] = None) -> None:
        max_n_workers = cpu_count() - 1
        if self.n_workers is None:
            if n_samples is not None:
                self.n_workers = int(
                    math.ceil(n_samples / self.SAMPLES_PER_WORKER)
                )
            else:
                self.n_workers = 2
        self.n_workers = max(1, min(self.n_workers, max_n_workers))

    @staticmethod
    def _batch(hypo: List[str], ref: List[List[str]], n_batches: int):
        n_samples = len(hypo)
        assert all(len(r) == n_samples for r in ref)
        hypo_and_ref = [hypo] + ref
        tupled = list(zip(*hypo_and_ref))
        batched = _batch(tupled, n_batches=n_batches)
        for b in batched:
            part_hypo, *part_ref = zip(*b)
            yield part_hypo, part_ref

    @classmethod
    @abstractmethod
    def score(
            cls, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        raise NotImplementedError

    def _score_sentences_multiprocess(
            self, hypothesis: List[str], references: List[List[str]],
            sent_score_func: Optional[SENT_SCORE_FN_TYPE] = None
    ) -> List[float]:
        self._update_n_workers(len(hypothesis))
        if self.n_workers == 1:
            sent_scores = sent_score_func(
                hypothesis, references, extra_args=self.extra_args
            )
        else:
            batches = list(
                self._batch(hypothesis, references, n_batches=self.n_workers)
            )
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                futures = {
                    executor.submit(
                        sent_score_func, b[0], b[1], extra_args=self.extra_args
                    ): i
                    for i, b in enumerate(batches)
                }
                progress = as_completed(futures)
                if self.verbose:
                    progress = tqdm(progress)
                tmp = {futures[future]: future.result() for future in progress}
            sent_scores = []
            for k in sorted(tmp):
                sent_scores.extend(tmp[k])
        return sent_scores

    def _score_multiprocess_averaged(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None,
            sent_score_func: Optional[SENT_SCORE_FN_TYPE] = None,
    ) -> VizSeqScore:
        self._update_n_workers(len(hypothesis))

        corpus_score, sent_scores, group_scores = None, None, None
        sent_scores = self._score_sentences_multiprocess(
            hypothesis, references, sent_score_func
        )

        if self.corpus_level:
            corpus_score = np.mean(sent_scores)
        if not self.sent_level:
            sent_scores = None
        tag_set = self._unique(tags)
        if tag_set is not None:
            group_scores = {}
            for t in tag_set:
                indices = [i for i, cur in enumerate(tags) if t in cur]
                group_scores[t] = np.mean([sent_scores[i] for i in indices])

        return VizSeqScore.make(
                corpus_score=corpus_score, sent_scores=sent_scores,
                group_scores=group_scores
            )


FILE_ROOT = Path(__file__).parent

_SCORER_REGISTRY = {}
_SCORER_ID_TO_NAME = {}


def register_scorer(scorer_id: str, scorer_name: str):
    def register_scorer_class(scorer: Type[VizSeqScorer]) -> Type[VizSeqScorer]:
        if scorer_id in _SCORER_REGISTRY:
            raise ValueError(f'Cannot register duplicate scorer ({scorer_id})')
        if not issubclass(scorer, VizSeqScorer):
            raise ValueError(f'Scorer must be VizSeqScorer ({scorer_id})')
        _SCORER_REGISTRY[scorer_id] = scorer
        _SCORER_ID_TO_NAME[scorer_id] = scorer_name
        return scorer
    return register_scorer_class


def get_scorer(scorer_id: str) -> Type[VizSeqScorer]:
    assert scorer_id in _SCORER_REGISTRY.keys()
    return _SCORER_REGISTRY[scorer_id]


def get_scorer_ids() -> List[str]:
    return list(_SCORER_REGISTRY.keys())


def get_scorer_name(scorer_id: str) -> str:
    return _SCORER_ID_TO_NAME.get(scorer_id, '')


def get_scorer_names() -> List[str]:
    return list(_SCORER_ID_TO_NAME.values())


def get_scorer_ids_and_names() -> List[Tuple[str, str]]:
    return [tuple(e) for e in _SCORER_ID_TO_NAME.items()]


# automatically import any Python files in the scorers/ directory
scorer_filenames = sorted(
    m for m in os.listdir(FILE_ROOT)
    if m.endswith(PY_FILE_EXT) and not m.startswith(EXCLUDED_PREFIXES)
)
for m in scorer_filenames:
    module_name = f'vizseq.scorers.{os.path.splitext(os.path.basename(m))[0]}'
    if module_name not in sys.modules:
        importlib.import_module(module_name)
