# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import Dict, List, Optional

from rouge_score import rouge_scorer

from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore


def _get_sent_rouge(
        hypothesis: List[str], references: List[List[str]], rouge_type: str,
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    assert rouge_type in {'rouge-1', 'rouge-2', 'rouge-l'}
    metric = {
        'rouge-1': 'rouge1',
        'rouge-2': 'rouge2',
        'rouge-l': 'rougeL',
    }[rouge_type]
    scorer = rouge_scorer.RougeScorer([metric], use_stemmer=True)
    return [
        scorer.score(reference, prediction)[metric].fmeasure
        for prediction, reference in zip(hypothesis, references[0])
    ]


def _get_sent_rouge_1(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    return _get_sent_rouge(hypothesis, references, rouge_type='rouge-1')


def _get_sent_rouge_2(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    return _get_sent_rouge(hypothesis, references, rouge_type='rouge-2')


def _get_sent_rouge_l(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    return _get_sent_rouge(hypothesis, references, rouge_type='rouge-l')


@register_scorer('rouge_1', 'ROUGE-1')
class Rouge1Scorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        return self._score_multiprocess_averaged(
            hypothesis, references, tags, sent_score_func=_get_sent_rouge_1
        )


@register_scorer('rouge_2', 'ROUGE-2')
class Rouge2Scorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        return self._score_multiprocess_averaged(
            hypothesis, references, tags, sent_score_func=_get_sent_rouge_2
        )


@register_scorer('rouge_l', 'ROUGE-L')
class RougeLScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        return self._score_multiprocess_averaged(
            hypothesis, references, tags, sent_score_func=_get_sent_rouge_l,
        )
