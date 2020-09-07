# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional, Dict
import argparse

from sacrebleu.metrics import CHRF
from tqdm import tqdm

from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore


def get_default_args(chrf_whitespace=False, chrf_order=6, chrf_beta=2):
    args = argparse.Namespace()
    args.chrf_whitespace = chrf_whitespace
    args.chrf_order = chrf_order
    args.chrf_beta = chrf_beta
    return args


def _get_sent_chrf(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
):
    scorer = CHRF(get_default_args())
    data = [hypothesis] + references
    return [scorer.sentence_score(h, r).score for h, *r in zip(*data)]


def _get_corpus_statistics(hypothesis: List[str], references: List[List[str]]):
    scorer = CHRF(get_default_args())
    corpus_statistics = [0] * (scorer.order * 3)
    data = [hypothesis] + references
    for h, *r in zip(*data):
        statistics = scorer.get_sentence_statistics(h, r)
        for i in range(len(statistics)):
            corpus_statistics[i] += statistics[i]
    return corpus_statistics


@register_scorer('chrf', 'chrF')
class ChrFScorer(VizSeqScorer):
    def score_corpus_multiprocess(
            self, hypothesis: List[str], references: List[List[str]]
    ) -> float:
        scorer = CHRF(get_default_args())
        if self.n_workers == 1:
            corpus_score = scorer.corpus_score(hypothesis, references).score
        else:
            batches = list(
                self._batch(hypothesis, references, n_batches=self.n_workers)
            )
            corpus_stats = [0 for _ in range(CHRF.ORDER * 3)]
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                futures = [
                    executor.submit(_get_corpus_statistics, b[0], b[1])
                    for b in batches
                ]
                progress = as_completed(futures)
                if self.verbose:
                    progress = tqdm(progress)
                for future in progress:
                    stats = future.result()
                    for i in range(CHRF.ORDER * 3):
                        corpus_stats[i] += stats[i]
            corpus_score = scorer.compute_chrf(corpus_stats, scorer.order,
                                               scorer.beta).score
        return corpus_score

    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None,
    ) -> VizSeqScore:
        self._update_n_workers(len(hypothesis))

        corpus_score, group_scores, sent_scores = None, None, None
        if self.sent_level:
            sent_scores = self._score_sentences_multiprocess(
                hypothesis, references, _get_sent_chrf
            )

        if self.corpus_level:
            corpus_score = self.score_corpus_multiprocess(
                hypothesis, references
            )

        if tags is not None:
            tag_set = self._unique(tags)
            group_scores = {}
            for t in tag_set:
                indices = [i for i, cur in enumerate(tags) if t in cur]
                ref_slice = [[r[i] for i in indices] for r in references]
                pred_slice = [hypothesis[i] for i in indices]
                group_scores[t] = self.score_corpus_multiprocess(
                    pred_slice, ref_slice
                )

        return VizSeqScore.make(
                corpus_score=corpus_score, sent_scores=sent_scores,
                group_scores=group_scores
            )
