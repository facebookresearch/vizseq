# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from . import VizSeqScorerTestCase
from vizseq.scorers.ter import TERScorer


class TERScorerTestCase(VizSeqScorerTestCase):
    def test_basic_case(self):
        ref = (
            'SAUDI ARABIA denied THIS WEEK information published in the'
            ' AMERICAN new york times'
        )
        hyp = (
            'THIS WEEK THE SAUDIS denied information published in the'
            ' new york times'
        )
        score = TERScorer(sent_level=True, corpus_level=False).score(
            [hyp], [[ref]]
        ).sent_scores[0]
        self.assertEqual(score, round(4 / 13, 3))

    def test(self):
        return self._test_n_grams_based(TERScorer, 0.9)
