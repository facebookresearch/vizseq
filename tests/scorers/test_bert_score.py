# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from . import VizSeqScorerTestCase
from vizseq.scorers.bert_score import BERTScoreScorer


class BERTScoreScorerTestCase(VizSeqScorerTestCase):
    def test(self):
        return self._test_embedding_based(BERTScoreScorer)


class BERTScoreScorerReuseTestCase(unittest.TestCase):
    def test_reuses_model_for_repeated_scores_in_same_language(self):
        instances = []

        class FakeBERTScorer:
            def __init__(self, lang, nthreads):
                self.lang = lang
                self.nthreads = nthreads
                self.calls = []
                instances.append(self)

            def score(self, hypothesis, references, verbose=False):
                self.calls.append((hypothesis, references, verbose))
                scores = np.array([0.25, 0.75])
                return scores, scores, scores

        modules = {
            'bert_score': SimpleNamespace(BERTScorer=FakeBERTScorer),
            'langid': SimpleNamespace(classify=lambda _: ('en', 1.0)),
        }
        scorer = BERTScoreScorer(
            corpus_level=True, sent_level=True, n_workers=1, verbose=True
        )
        hypothesis = ['first hypothesis', 'second hypothesis']
        references = [['first reference', 'second reference']]

        with patch.dict(sys.modules, modules):
            first = scorer.score(hypothesis, references)
            second = scorer.score(hypothesis, references)

        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0].nthreads, 1)
        self.assertEqual(len(instances[0].calls), 2)
        self.assertTrue(instances[0].calls[0][2])
        self.assertEqual(first, second)
        self.assertEqual(first.corpus_score, 0.5)
        self.assertEqual(first.sent_scores, [0.25, 0.75])
