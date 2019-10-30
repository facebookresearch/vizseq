# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


from typing import List, Optional, Dict

import numpy as np

from vizseq.scorers._wer import get_wer
from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore


def _get_sent_ins(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    joined_references = list(zip(*references))
    return [
        float(get_wer(r, h).insertion)
        for r, h in zip(joined_references, hypothesis)
    ]


def _get_sent_del(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    joined_references = list(zip(*references))
    return [
        float(get_wer(r, h).deletion)
        for r, h in zip(joined_references, hypothesis)
    ]


def _get_sent_sub(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    joined_references = list(zip(*references))
    return [
        float(get_wer(r, h).substitution)
        for r, h in zip(joined_references, hypothesis)
    ]


def _get_sent_len_r(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    joined_references = list(zip(*references))
    return [
        float(get_wer(r, h).len_r)
        for r, h in zip(joined_references, hypothesis)
    ]


def _get_sent_wer(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    joined_references = list(zip(*references))
    return [
        get_wer(r, h).wer for r, h in zip(joined_references, hypothesis)
    ]


@register_scorer('wer_ins', 'WER-Insertion')
class WERInsertionScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        return self._score_multiprocess_averaged(
            hypothesis, references, tags, sent_score_func=_get_sent_ins
        )


@register_scorer('wer_del', 'WER-Deletion')
class WERDeletionScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        return self._score_multiprocess_averaged(
            hypothesis, references, tags, sent_score_func=_get_sent_del
        )


@register_scorer('wer_sub', 'WER-Substitution')
class WERSubstitutionScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        return self._score_multiprocess_averaged(
            hypothesis, references, tags, sent_score_func=_get_sent_sub
        )


@register_scorer('wer', 'WER')
class WERScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        self._update_n_workers(len(hypothesis))

        corpus_score, group_scores, sent_scores = None, None, None
        sent_scores = self._score_sentences_multiprocess(
            hypothesis, references, _get_sent_wer
        )

        sent_lens = None
        if self.corpus_level:
            sent_lens = self._score_sentences_multiprocess(
                hypothesis, references, _get_sent_len_r
            )
            n_incorrect = np.sum(
                [s * l for s, l in zip(sent_scores, sent_lens)]
            )
            corpus_score = n_incorrect / np.sum(sent_lens)

        if tags is not None:
            tag_set = self._unique(tags)
            group_scores = {}
            if sent_lens is None:
                sent_lens = self._score_sentences_multiprocess(
                    hypothesis, references, _get_sent_len_r
                )
            for t in tag_set:
                indices = [i for i, cur in enumerate(tags) if t in cur]
                cur_sent_scores = [sent_scores[i] for i in indices]
                cur_sent_lens = [sent_lens[i] for i in indices]
                n_incorrect = np.sum(
                    [s * l for s, l in zip(cur_sent_scores, cur_sent_lens)]
                )
                group_scores[t] = n_incorrect / np.sum(sent_lens)

        return VizSeqScore.make(
            corpus_score=corpus_score, sent_scores=sent_scores,
            group_scores=group_scores
        )
