# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


from typing import List, Tuple
from functools import lru_cache


@lru_cache(maxsize=8192)
def _get_edit_distance(s_str: str, t_str: str):
    s, t = s_str.split(), t_str.split()
    len_s, len_t = len(s), len(t)
    d = [[0 for _ in range(len_t + 1)] for _ in range(len_s + 1)]
    for i in range(1, len_s + 1):
        d[i][0] = i
    for j in range(1, len_t + 1):
        d[0][j] = j
    for i in range(1, len_s + 1):
        for j in range(1, len_t + 1):
            sub = int(s[i - 1] != t[j - 1])
            d[i][j] = min(
                d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + sub
            )
    return d[-1][-1]


def get_edit_distance(s: List[str], t: List[str]):
    return _get_edit_distance(' '.join(s), ' '.join(t))


def _find_pairs(
        tokens_1: List[str], tokens_2: List[str]
) -> Tuple[int, int, int]:
    len_1, len_2 = len(tokens_1), len(tokens_2)
    for i_1 in range(len_1):
        for i_2 in range(len_2):
            if i_1 == i_2:
                continue
            if tokens_1[i_1] == tokens_2[i_2]:
                length = 1
                while i_1 + length < len_1 and i_2 + length < len_2 and \
                        tokens_1[i_1 + length] == tokens_2[i_2 + length]:
                    length += 1
                yield i_1, i_2, length


def _shift(
        hypo_tokens: List[str], ref_tokens: List[str]
) -> Tuple[int, List[str]]:
    candidates = {}
    for h_ofs, r_ofs, length in _find_pairs(hypo_tokens, ref_tokens):
        new = hypo_tokens[:h_ofs] + hypo_tokens[h_ofs + length:]
        new = new[:r_ofs] + hypo_tokens[h_ofs:h_ofs + length] + new[r_ofs:]
        new_n_edits = get_edit_distance(new, ref_tokens)
        candidates[new_n_edits] = new
    if len(candidates) == 0:
        return get_edit_distance(hypo_tokens, ref_tokens), hypo_tokens
    best = sorted(candidates)[0]
    return best, candidates[best]


def sentence_ter_one_ref(hypothesis: str, reference: str) -> float:
    hypo_tokens, ref_tokens = hypothesis.split(), reference.split()
    n_shifts = 0
    prev_n_edits = get_edit_distance(hypo_tokens, ref_tokens)
    while True:
        new_n_edits, new_tokens = _shift(hypo_tokens, ref_tokens)
        if prev_n_edits - new_n_edits <= 0:
            break
        n_shifts += 1
        prev_n_edits = new_n_edits
        hypo_tokens = new_tokens
    return (n_shifts + prev_n_edits) / len(ref_tokens)


def sentence_ter(hypothesis: str, references: List[str]) -> float:
    return max(sentence_ter_one_ref(hypothesis, r) for r in references)
