# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional, Dict

from sacrebleu.metrics import BLEU
from tqdm import tqdm

from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore
from vizseq._utils.optional import get_optional_dict


def _project(score, kind: str = 'score') -> float:
    return {'score': lambda s: s.score, 'bp': lambda s: s.bp}[kind](score)


def _get_sent_bleu(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None, score='score'
) -> List[float]:
    tokenizer = get_optional_dict(extra_args, 'tokenizer', 'none')
    scorer = BLEU(
        tokenize=tokenizer, smooth_method='floor', effective_order=True,
        force=True,
    )
    data = [hypothesis] + references
    scores = [scorer.sentence_score(h, list(r)) for h, *r in zip(*data)]
    return [_project(s, score) for s in scores]


@register_scorer('bleu', 'BLEU')
class BLEUScorer(VizSeqScorer):
    def score_corpus_multiprocess(
            self, hypothesis: List[str], references: List[List[str]],
            score='score'
    ) -> float:
        tokenizer = get_optional_dict(self.extra_args, 'tokenizer', 'none')
        scorer = BLEU(tokenize=tokenizer, force=True)
        if self.n_workers == 1:
            corpus_score = scorer.corpus_score(hypothesis, references)
        else:
            batches = list(
                self._batch(hypothesis, references, n_batches=self.n_workers)
            )
            stats: List[List[int]] = []
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                futures = [
                    executor.submit(
                        scorer._extract_corpus_statistics, b[0], b[1]
                    )
                    for b in batches
                ]
                progress = as_completed(futures)
                if self.verbose:
                    progress = tqdm(progress)
                for future in progress:
                    stats.extend(future.result())
            corpus_score = scorer._aggregate_and_compute(stats)
        return _project(corpus_score, score)

    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        self._update_n_workers(len(hypothesis))

        corpus_score, group_scores, sent_scores = None, None, None

        if self.sent_level:
            sent_scores = self._score_sentences_multiprocess(
                hypothesis, references, _get_sent_bleu
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
