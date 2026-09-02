# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import sys
import unittest
import weakref
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Timer
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from . import VizSeqScorerTestCase
from vizseq.scorers.bert_score import (
    BERTScoreScorer,
    _clear_bert_scorer_cache,
)


class BERTScoreScorerTestCase(VizSeqScorerTestCase):
    def test(self):
        return self._test_embedding_based(BERTScoreScorer)


class BERTScoreScorerReuseTestCase(unittest.TestCase):
    def setUp(self):
        _clear_bert_scorer_cache()

    def tearDown(self):
        _clear_bert_scorer_cache()

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
        first_scorer = BERTScoreScorer(
            corpus_level=True, sent_level=True, n_workers=1, verbose=True
        )
        second_scorer = BERTScoreScorer(
            corpus_level=True, sent_level=True, n_workers=1, verbose=True
        )
        hypothesis = ['first hypothesis', 'second hypothesis']
        references = [['first reference', 'second reference']]

        with patch.dict(sys.modules, modules):
            first = first_scorer.score(hypothesis, references)
            second = second_scorer.score(hypothesis, references)

        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0].nthreads, 1)
        self.assertEqual(len(instances[0].calls), 2)
        self.assertTrue(instances[0].calls[0][2])
        self.assertEqual(first, second)
        self.assertEqual(first.corpus_score, 0.5)
        self.assertEqual(first.sent_scores, [0.25, 0.75])

    def test_releases_cached_model_before_loading_replacement(self):
        instances = []

        class FakeBERTScorer:
            def __init__(self, lang, nthreads):
                if instances and instances[-1]() is not None:
                    raise AssertionError('Previous model is still alive')
                self.lang = lang
                instances.append(weakref.ref(self))

            def score(self, hypothesis, references, verbose=False):
                scores = np.array([0.5])
                return scores, scores, scores

        languages = iter(['en', 'de'])
        modules = {
            'bert_score': SimpleNamespace(BERTScorer=FakeBERTScorer),
            'langid': SimpleNamespace(
                classify=lambda _: (next(languages), 1.0)
            ),
        }

        with patch.dict(sys.modules, modules):
            BERTScoreScorer().score(['first'], [['first']])
            BERTScoreScorer().score(['zweite'], [['zweite']])

        self.assertIsNone(instances[0]())
        self.assertIsNotNone(instances[1]())

    def test_initializes_model_once_for_concurrent_cache_misses(self):
        constructor_started = Event()
        release_constructor = Event()
        instances = []

        class FakeBERTScorer:
            def __init__(self, lang, nthreads):
                self.lang = lang
                instances.append(self)
                constructor_started.set()
                release_constructor.wait(timeout=2)

            def score(self, hypothesis, references, verbose=False):
                scores = np.array([0.5])
                return scores, scores, scores

        modules = {
            'bert_score': SimpleNamespace(BERTScorer=FakeBERTScorer),
            'langid': SimpleNamespace(classify=lambda _: ('en', 1.0)),
        }

        with patch.dict(sys.modules, modules):
            with ThreadPoolExecutor(max_workers=1) as executor:
                first = executor.submit(
                    BERTScoreScorer().score, ['first'], [['first']]
                )
                self.assertTrue(constructor_started.wait(timeout=1))
                timer = Timer(0.5, release_constructor.set)
                timer.start()
                try:
                    BERTScoreScorer().score(['second'], [['second']])
                    first.result(timeout=2)
                finally:
                    release_constructor.set()
                    timer.join()

        self.assertEqual(len(instances), 1)
