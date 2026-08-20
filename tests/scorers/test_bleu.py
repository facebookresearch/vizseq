# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from . import VizSeqScorerTestCase
from vizseq.scorers.bleu import BLEUScorer


class BLEUScorerTestCase(VizSeqScorerTestCase):
    def test(self):
        return self._test_n_grams_based(BLEUScorer, 0.9)

    def test_default_tokenizer_matches_sacrebleu_13a(self):
        # Regression test: the default tokenizer must follow sacrebleu's
        # standard (13a), not the no-op 'none' that silently lowered scores.
        hypothesis = ['This is really nice.']
        references = [["That's really nice."]]
        default = BLEUScorer(
            corpus_level=True, sent_level=False, n_workers=1
        ).score(hypothesis, references)
        explicit_13a = BLEUScorer(
            corpus_level=True, sent_level=False, n_workers=1,
            extra_args={'tokenizer': '13a'},
        ).score(hypothesis, references)
        self.assertEqual(default.corpus_score, explicit_13a.corpus_score)
