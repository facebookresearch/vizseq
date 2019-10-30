# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Optional, Dict

from nltk.translate.nist_score import sentence_nist as sent_nist

from vizseq.scorers import register_scorer, VizSeqScorer
from vizseq.scorers import VizSeqScore


def _get_sent_nist(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    joined_references = list(zip(*references))
    return [
        sent_nist([rr.split() for rr in r], h.split()) if len(h) < 5 else 0.0
        for r, h in zip(joined_references, hypothesis)
    ]


@register_scorer('nist', 'NIST')
class NISTScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        return self._score_multiprocess_averaged(
            hypothesis, references, tags, sent_score_func=_get_sent_nist
        )
