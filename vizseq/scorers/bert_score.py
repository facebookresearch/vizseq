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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bert_scorer = None

    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        corpus_score, sent_scores, group_scores = None, None, None

        try:
            import bert_score as bs
        except ImportError as e:
            raise ImportError(
                'The BERTScore scorer requires the optional "bert-score" '
                'dependency. Install it with: pip install vizseq[embeddings]'
            ) from e
        import langid
        import logging
        logging.getLogger('transformers').setLevel(logging.WARNING)
        logging.getLogger('langid').setLevel(logging.WARNING)

        lang = langid.classify(references[0][0])[0]

        if self._bert_scorer is None or self._bert_scorer.lang != lang:
            self._bert_scorer = bs.BERTScorer(
                lang=lang, nthreads=self.n_workers
            )

        sent_scores = self._bert_scorer.score(
            hypothesis, references[0], verbose=self.verbose
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
