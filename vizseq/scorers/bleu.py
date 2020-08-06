# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional, Dict
import argparse

from sacrebleu.metrics import BLEU
from tqdm import tqdm

from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore
from vizseq._utils.optional import get_optional_dict


def get_default_args(force=True, lc=False, smooth_value=None,
                     smooth_method='exp', tokenize='13a', num_refs=1):
    args = argparse.Namespace()
    args.force = force
    args.lc = lc
    args.smooth_value = smooth_value
    args.smooth_method = smooth_method
    args.tokenize = tokenize
    args.num_refs = num_refs
    return args


def _get_sent_bleu(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None, score='score'
) -> List[float]:
    tokenizer = get_optional_dict(extra_args, 'tokenizer', 'none')
    data = [hypothesis] + references
    args = get_default_args(smooth_method='floor', tokenize=tokenizer,
                            num_refs=len(references))
    scorer = BLEU(args)
    scores = [
        scorer.corpus_score([h], [[rr] for rr in r], use_effective_order=True)
        for h, *r in zip(*data)
    ]
    proj = {'score': lambda s: s.score, 'bp': lambda s: s.bp}.get(score)
    return [proj(s) for s in scores]


@register_scorer('bleu', 'BLEU')
class BLEUScorer(VizSeqScorer):
    def score_corpus_multiprocess(
            self, hypothesis: List[str], references: List[List[str]],
            score='score'
    ) -> float:
        tokenizer = get_optional_dict(self.extra_args, 'tokenizer', 'none')
        args = get_default_args(tokenize=tokenizer, num_refs=len(references))
        scorer = BLEU(args)
        if self.n_workers == 1:
            corpus_score = scorer.corpus_score(
                hypothesis, references, use_effective_order=False
            )
        else:
            batches = list(
                self._batch(hypothesis, references, n_batches=self.n_workers)
            )
            ref_len, sys_len = 0, 0
            correct = [0 for _ in range(BLEU.NGRAM_ORDER)]
            total = [0 for _ in range(BLEU.NGRAM_ORDER)]
            with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
                futures = [
                    executor.submit(
                        scorer.corpus_score, b[0], b[1],
                        use_effective_order=False
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
                    for n in range(BLEU.NGRAM_ORDER):
                        correct[n] += s.counts[n]
                        total[n] += s.totals[n]
                corpus_score = scorer.compute_bleu(
                    correct, total, sys_len, ref_len, smooth_method='exp'
                )
        proj = {'score': lambda s: s.score, 'bp': lambda s: s.bp}.get(score)
        return proj(corpus_score)

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
