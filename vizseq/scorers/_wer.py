# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, NamedTuple
from enum import Enum

import numpy as np


class OperationType(Enum):
    correct = 0
    substitution = 1
    insertion = 2
    deletion = 3


class WerScore(NamedTuple):
    wer: float
    insertion: int
    deletion: int
    substitution: int
    len_r: int


def _get_wer(r: List[str], h: List[str]) -> WerScore:
    len_r, len_h = len(r), len(h)
    edits = [[0 for _ in range(len_h + 1)] for _ in range(len_r + 1)]
    pt = [
        [OperationType.correct for _ in range(len_h + 1)]
        for _ in range(len_r + 1)
    ]

    for i in range(1, len_r + 1):
        edits[i][0] = i
        pt[i][0] = OperationType.deletion
    for j in range(1, len_h + 1):
        edits[0][j] = j
        pt[0][j] = OperationType.insertion
    for i in range(1, len_r + 1):
        for j in range(1, len_h + 1):
            if r[i - 1] == h[j - 1]:
                edits[i][j] = edits[i - 1][j - 1]
                pt[i][j] = OperationType.correct
            else:
                edits[i][j] = edits[i - 1][j - 1] + 1
                pt[i][j] = OperationType.substitution

            if edits[i][j - 1] + 1 < edits[i][j]:
                edits[i][j] = edits[i][j - 1] + 1
                pt[i][j] = OperationType.insertion

            if edits[i - 1][j] + 1 < edits[i][j]:
                edits[i][j] = edits[i - 1][j] + 1
                pt[i][j] = OperationType.deletion

    i, j = len_r, len_h
    n_sub, n_del, n_ins = 0, 0, 0
    while i > 0 or j > 0:
        if pt[i][j] == OperationType.correct:
            i -= 1
            j -= 1
        elif pt[i][j] == OperationType.substitution:
            n_sub += 1
            i -= 1
            j -= 1
        elif pt[i][j] == OperationType.insertion:
            n_ins += 1
            j -= 1
        elif pt[i][j] == OperationType.deletion:
            n_del += 1
            i -= 1

    return WerScore(
        wer=100. * (n_sub + n_del + n_ins) / len_r, len_r=len_r, deletion=n_del,
        substitution=n_sub, insertion=n_ins
    )


def get_wer(reference: List[str], hypothesis: str) -> WerScore:
    all_scores = [_get_wer(r.split(), hypothesis.split()) for r in reference]
    return WerScore(
        wer=np.min([s.wer for s in all_scores]),
        len_r=np.max([s.len_r for s in all_scores]),
        deletion=np.min([s.deletion for s in all_scores]),
        substitution=np.min([s.substitution for s in all_scores]),
        insertion=np.min([s.insertion for s in all_scores]),
    )
