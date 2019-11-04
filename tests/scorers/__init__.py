# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest
import time
import os
from typing import Union, List, Optional, Type, Dict

from vizseq.scorers import VizSeqScorer, VizSeqScore


class VizSeqScorerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        dataset_root = 'examples/data/translation_wmt14_en_de_test'
        if not os.path.isdir(dataset_root):
            raise NotADirectoryError(f'{dataset_root} does not exist.')
        with open(f'{dataset_root}/src_0.txt') as f:
            self.source = [l.strip() for l in f]
        with open(f'{dataset_root}/ref_0.txt') as f:
            self.references = [[l.strip() for l in f]]
        with open(f'{dataset_root}/pred_onlineA.0.txt') as f:
            self.hypothesis = [l.strip() for l in f]

    def _verify_speed(
            self, time_sp: float, time_mp: float, min_speedup_ratio: float = 0.9
    ):
        self.assertLessEqual(time_mp, time_sp * min_speedup_ratio)

    def _get_single_multi_proc_output_and_time(
            self, scorer_type: Type[VizSeqScorer], corpus_level: bool,
            sent_level: bool
    ):
        scorer_sp = scorer_type(
            corpus_level=corpus_level, sent_level=sent_level, n_workers=1
        )
        start = time.time()
        score_sp = scorer_sp.score(self.hypothesis, self.references)
        time_sp = time.time() - start

        score_mp = scorer_type(
            corpus_level=corpus_level, sent_level=sent_level, n_workers=2
        )
        start = time.time()
        score_mp = score_mp.score(self.hypothesis, self.references)
        time_mp = time.time() - start
        return score_sp, score_mp, time_sp, time_mp

    def _verify_score(
            self, score_sp: Union[float, List[float]],
            score_mp: Union[float, List[float]]
    ):
        self.assertEqual(score_mp, score_sp)

    def _test_n_grams_based(
            self, scorer_type: Type[VizSeqScorer], min_speedup_ratio: float,
            ref_score: Optional[VizSeqScore] = None
    ):
        # sentence-level score
        score_sp, score_mp, time_sp, time_mp = \
            self._get_single_multi_proc_output_and_time(
                scorer_type, corpus_level=False, sent_level=True
            )
        self._verify_speed(
            time_sp, time_mp, min_speedup_ratio=min_speedup_ratio
        )
        self._verify_score(score_sp.sent_scores, score_mp.sent_scores)
        if ref_score is not None and ref_score.sent_scores is not None:
            self._verify_score(score_sp.sent_scores, ref_score.sent_scores)

        # corpus-level score
        score_sp, score_mp, time_sp, time_mp = \
            self._get_single_multi_proc_output_and_time(
                scorer_type, corpus_level=True, sent_level=False
            )
        self._verify_speed(
            time_sp, time_mp, min_speedup_ratio=min_speedup_ratio
        )
        self._verify_score(score_sp.corpus_score, score_mp.corpus_score)
        if ref_score is not None and ref_score.corpus_score is not None:
            self._verify_score(score_sp.corpus_score, ref_score.corpus_score)

    def _test_embedding_based(
            self, scorer_type: Type[VizSeqScorer],
            extra_args: Optional[Dict[str, str]] = None
    ):
        scores_sp = scorer_type(
            corpus_level=True, sent_level=True, extra_args=extra_args
        ).score(self.hypothesis, self.references)
