# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Optional
from functools import partial

from vizseq.scorers import register_scorer, VizSeqScore
from vizseq.scorers.bleu import _get_sent_bleu, BLEUScorer

_get_sent_bp = partial(_get_sent_bleu, score='bp')


@register_scorer('bp', 'BP')
class BrevityPenaltyScorer(BLEUScorer):
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
                hypothesis, references, score='bp'
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
