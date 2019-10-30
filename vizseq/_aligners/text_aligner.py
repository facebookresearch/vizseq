# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


from typing import List, Tuple, Dict
from collections import Counter
from enum import Enum

from nltk.translate.ribes_score import word_rank_alignment


class VizSeqBaseTextAligner(object):
    NEG_IDX = -1
    ALIGNMENT_TYPE_TO_STYLE = {}

    @classmethod
    def _align(
            cls, trg_tokens: List[str], tokens: List[str],
            pos_label: Enum, neg_label: Enum
    ) -> List[Tuple[int, Enum]]:
        indices = word_rank_alignment(trg_tokens, tokens)
        token_labels = []
        cur = 0
        for i, w in enumerate(tokens):
            if cur < len(indices) and w == trg_tokens[indices[cur]]:
                token_labels.append((indices[cur], pos_label))
                cur += 1
            else:
                token_labels.append((cls.NEG_IDX, neg_label))
        return token_labels

    @classmethod
    def align(
            cls, trg_tokens: List[str], tokens: Dict[str, List[str]]
    ) -> Dict[str, List[Tuple[int, Enum]]]:
        raise NotImplementedError

    @classmethod
    def _get_span_html(
            cls, token: str, span_id_prefix: str, span_type: Enum, data_id: str,
            example_id: int, token_id: int, trg_span_id_prefix: str,
            trg_token_id: int
    ):
        attributes = [
            f'id="{span_id_prefix}_{data_id}_{example_id}_{token_id}"',
        ]
        if trg_token_id != cls.NEG_IDX:
            trg_span_id = f'{trg_span_id_prefix}_{example_id}_{trg_token_id}'
            attributes.extend([
                f'onmouseover="javascript:highlight_span(this, &quot;{trg_span_id}&quot;)"',
                f'onmouseout="javascript:dehighlight_span(this, &quot;{trg_span_id}&quot;)"'
            ])
        span_style = cls.ALIGNMENT_TYPE_TO_STYLE[span_type]
        if len(span_style) > 0:
            attributes.append(f'style="{span_style}"')
        return '<span ' + ' '.join(attributes) + ' >' + token + '</span>'

    @classmethod
    def to_span_html(
            cls, tokens: Dict[str, List[str]],
            alignments: Dict[str, List[Tuple[int, Enum]]], span_id_prefix: str,
            example_id: int, trg_span_id_prefix: str
    ) -> Dict[str, List[str]]:
        return {
            k: [
                cls._get_span_html(
                    tokens[k][i], span_id_prefix, t[1], k, example_id, i,
                    trg_span_id_prefix, t[0]
                )
                for i, t in enumerate(v)
            ]
            for k, v in alignments.items()
        }


class VizSeqSrcRefAlignmentType(Enum):
    none = 0
    copy = 1


class VizSeqRefHypoAlignmentType(Enum):
    confirmed = 1
    unconfirmed = 2
    improving = 3
    worsening = 4


class VizseqSrcRefTextAligner(VizSeqBaseTextAligner):
    ALIGNMENT_TYPE_TO_STYLE = {
        VizSeqSrcRefAlignmentType.copy: 'color:#AF601A;font-weight:bold',
        VizSeqSrcRefAlignmentType.none: '',
    }

    @classmethod
    def align(
            cls, trg_tokens: List[str], tokens: Dict[str, List[str]]
    ) -> Dict[str, List[Tuple[int, Enum]]]:
        return {
            i: cls._align(
                trg_tokens, t, pos_label=VizSeqSrcRefAlignmentType.copy,
                neg_label=VizSeqSrcRefAlignmentType.none
            )
            for i, t in tokens.items()
        }


class VizseqRefHypoTextAligner(VizSeqBaseTextAligner):
    ALIGNMENT_TYPE_TO_STYLE = {
        VizSeqRefHypoAlignmentType.confirmed: 'color:#1A5276;font-weight:bold',
        VizSeqRefHypoAlignmentType.improving: 'color:#5499C7;font-weight:bold',
        VizSeqRefHypoAlignmentType.worsening: 'color:#B03A2E;font-weight:bold',
        VizSeqRefHypoAlignmentType.unconfirmed: '',
    }

    @classmethod
    def align(
            cls, trg_tokens: List[str], tokens: Dict[str, List[str]]
    ) -> Dict[str, List[Tuple[int, Enum]]]:
        aligned = {
            i: cls._align(
                trg_tokens, t, pos_label=VizSeqRefHypoAlignmentType.confirmed,
                neg_label=VizSeqRefHypoAlignmentType.unconfirmed
            )
            for i, t in tokens.items()
        }

        counter = {
            VizSeqRefHypoAlignmentType.confirmed: Counter(),
            VizSeqRefHypoAlignmentType.unconfirmed: Counter()
        }

        for k, a in aligned.items():
            for i, e in enumerate(a):
                label = e[1]
                if label in counter:
                    token = tokens[k][i]
                    counter[label].update([token])

        new_label_map = {
            VizSeqRefHypoAlignmentType.confirmed: VizSeqRefHypoAlignmentType.improving,
            VizSeqRefHypoAlignmentType.unconfirmed: VizSeqRefHypoAlignmentType.worsening
        }
        cross_aligned = {}
        for k, a in aligned.items():
            cur = []
            for i, e in enumerate(a):
                label = e[1]
                token = tokens[k][i]
                if counter[label][token] == 1:
                    cur.append((e[0], new_label_map[label]))
                else:
                    cur.append(e)
            cross_aligned[k] = cur
        return cross_aligned
