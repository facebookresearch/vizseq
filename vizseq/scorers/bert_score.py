# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore

import numpy as np
from threading import Lock
from typing import Any, List, Optional, Tuple


# A BERTScorer holds a large transformer model (RoBERTa-large for English),
# whose loading dominates the cost of scoring. Callers build a throwaway
# scorer object per metric per model on every call (see vizseq.ipynb.core and
# vizseq._view.data_view, which re-score on every page render and sort), so
# the cache has to outlive the scorer instance to be of any use. One entry is
# enough, and keeps us from pinning several models in memory at once: a given
# view scores all of its models against the same references, so the key only
# changes when the dataset's language does.
#
# n_workers is deliberately neither passed through nor part of the key.
# bert-score's nthreads only sizes the pool in get_idf_dict(), reachable just
# from compute_idf(), which needs idf=True; we score with the default
# idf=False, so it cannot affect a score. Keying on it would evict and reload
# RoBERTa-large for byte-identical output. If idf support is ever added,
# nthreads has to go back into the key *and* the constructor together.
_cached_bert_scorer_key: Optional[Tuple[type, str]] = None
_cached_bert_scorer: Optional[Any] = None
_bert_scorer_cache_lock = Lock()


def _get_bert_scorer(bs, lang: str):
    global _cached_bert_scorer_key, _cached_bert_scorer
    # The class is part of the key: a cached instance is only valid for the
    # constructor that produced it, so a swapped-out bert_score module (a
    # reload, or a test double) gets its own scorer rather than a stale one.
    key = (bs.BERTScorer, lang)
    with _bert_scorer_cache_lock:
        if _cached_bert_scorer is None or _cached_bert_scorer_key != key:
            # Drop the old model before loading its replacement so a language
            # change does not require both models to fit in memory at once.
            _cached_bert_scorer_key, _cached_bert_scorer = None, None
            scorer = bs.BERTScorer(lang=lang)
            _cached_bert_scorer_key, _cached_bert_scorer = key, scorer
        return _cached_bert_scorer


def _clear_bert_scorer_cache() -> None:
    global _cached_bert_scorer_key, _cached_bert_scorer
    with _bert_scorer_cache_lock:
        _cached_bert_scorer_key, _cached_bert_scorer = None, None


@register_scorer('bert_score', 'BERTScore')
class BERTScoreScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        corpus_score, sent_scores, group_scores = None, None, None

        # BERTScorer.score() has no length check of its own (the functional
        # bert_score.score() it replaced did), and silently mis-aligns
        # hypotheses and references when the two disagree.
        n_samples = len(hypothesis)
        if not all(len(r) == n_samples for r in references):
            raise ValueError(
                f'All reference lists must have the same length as hypothesis ({n_samples})'
            )
        if n_samples == 0:
            # Nothing to score, and no text to detect a language from. Most
            # scorers return nan for an empty corpus rather than raising, so
            # do the same instead of falling through to references[0][0].
            return VizSeqScore.make(
                corpus_score=np.nan if self.corpus_level else None,
                sent_scores=[],
                group_scores={} if tags is not None else None,
            )
        if not references:
            # The length check above is vacuous when there is nothing to
            # iterate over, and scoring reads references[0] below.
            raise ValueError('At least one reference list is required')

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

        bert_scorer = _get_bert_scorer(bs, lang)

        sent_scores = bert_scorer.score(
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
