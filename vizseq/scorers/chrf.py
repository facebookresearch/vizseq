# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional, Dict

import sacrebleu as sb
from tqdm import tqdm

from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore


def _get_sent_chrf(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
):
    return [
        sb.sentence_chrf(h, r).score for h, r in zip(hypothesis, references[0])
    ]


@register_scorer('chrf', 'chrF')
class ChrFScorer(VizSeqScorer):
    def score_corpus_multiprocess(
            self, hypothesis: List[str], references: List[List[str]]
    ) -> float:
        if self.n_workers == 1:
            corpus_score = sb.corpus_chrf(hypothesis, references[0]).score
        else:
            batches = list(
                self._batch(hypothesis, references, n_batches=self.n_workers)
            )
            corpus_statistics = [0 for _ in range(sb.CHRF_ORDER * 3)]
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                futures = [
                    executor.submit(
                        sb.get_corpus_statistics, b[0], b[1][0]
                    )
                    for b in batches
                ]
                progress = as_completed(futures)
                if self.verbose:
                    progress = tqdm(progress)
                for future in progress:
                    stats = future.result()
                    for i in range(sb.CHRF_ORDER * 3):
                        corpus_statistics[i] += stats[i]
            avg_precision, avg_recall = sb._avg_precision_and_recall(
                corpus_statistics, sb.CHRF_ORDER
            )
            corpus_score = sb._chrf(avg_precision, avg_recall)
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
