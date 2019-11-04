# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore

import numpy as np
from typing import List, Optional


@register_scorer('bert_score', 'BERTScore')
class BERTScoreScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        corpus_score, sent_scores, group_scores = None, None, None

        import bert_score as bs
        import langid
        import logging
        logging.getLogger('pytorch_pretrained_bert').setLevel(logging.WARNING)
        logging.getLogger('langid').setLevel(logging.WARNING)

        lang = langid.classify(references[0][0])[0]

        sent_scores = bs.score(
            hypothesis, references[0], nthreads=self.n_workers, lang=lang,
            verbose=self.verbose
        )[2].tolist()

        if self.corpus_level:
            corpus_score = np.mean(sent_scores)

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
