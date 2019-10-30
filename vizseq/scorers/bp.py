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
from vizseq._utils.optional import get_optional_dict


def _get_sent_bp(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
):
    tokenizer = get_optional_dict(extra_args, 'bp_tokenizer', 'none')
    data = [hypothesis] + references
    return [
        sb.corpus_bleu(
            [h], [r], smooth_method='floor', use_effective_order=True,
            force=True, tokenize=tokenizer
        ).bp
        for h, *r in zip(*data)
    ]


@register_scorer('bp', 'BP')
class BrevityPenaltyScorer(VizSeqScorer):
    def score_corpus_multiprocess(
            self, hypothesis: List[str], references: List[List[str]]
    ) -> float:
        tokenizer = get_optional_dict(self.extra_args, 'bp_tokenizer', 'none')
        if self.n_workers == 1:
            corpus_score = sb.corpus_bleu(
                hypothesis, references, force=True, tokenize=tokenizer
            ).bp
        else:
            batches = list(
                self._batch(hypothesis, references, n_batches=self.n_workers)
            )
            ref_len, sys_len = 0, 0
            correct = [0 for _ in range(sb.NGRAM_ORDER)]
            total = [0 for _ in range(sb.NGRAM_ORDER)]
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                futures = [
                    executor.submit(
                        sb.corpus_bleu, b[0], b[1], force=True,
                        tokenize=tokenizer
                    )
                    for b in batches
                ]
                progress = as_completed(futures)
                if self.verbose:
                    progress = tqdm(progress)
                for future in progress:
                    s = future.result()
                    ref_len += s.ref_len
                    sys_len += s.sys_len
                    for n in range(sb.NGRAM_ORDER):
                        correct[n] += s.counts[n]
                        total[n] += s.totals[n]
            corpus_score = sb.compute_bleu(
                correct, total, sys_len, ref_len, smooth_method='exp'
            ).bp
        return corpus_score

    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        self._update_n_workers(len(hypothesis))

        corpus_score, group_scores, sent_scores = None, None, None
        if self.sent_level:
            sent_scores = self._score_sentences_multiprocess(
                hypothesis, references, _get_sent_bp
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
