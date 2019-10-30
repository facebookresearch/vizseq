# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Optional, Dict

import numpy as np

from vizseq.scorers._cider import _CIDErScorer
from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore
from vizseq._utils.optional import get_optional_dict


def _get_sent_cider(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    n_workers = get_optional_dict(extra_args, 'n_workers', 1)
    verbose = get_optional_dict(extra_args, 'verbose', False)
    return _CIDErScorer(n_workers=n_workers, verbose=verbose).get_sent_scores(
        hypothesis, references
    )


@register_scorer('cider', 'CIDEr')
class CIDErScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        self._update_n_workers(len(hypothesis))

        sent_scores = _get_sent_cider(
            hypothesis, references, extra_args={
                'n_workers': self.n_workers, 'verbose': self.verbose
            }
        )
        corpus_score, group_scores = None, None

        if self.corpus_level:
            corpus_score = np.mean(sent_scores)
        if not self.sent_level:
            sent_scores = None
        if tags is not None:
            tag_set = self._unique(tags)
            group_scores = {}
            for t in tag_set:
                indices = [i for i, cur in enumerate(tags) if t in cur]
                group_scores[t] = np.mean([sent_scores[i] for i in indices])

        return VizSeqScore.make(
            corpus_score=corpus_score, sent_scores=sent_scores,
            group_scores=group_scores
        )
