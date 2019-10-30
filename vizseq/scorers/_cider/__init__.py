# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

# Adapted from
# https://github.com/tylin/coco-caption/blob/master/pycocoevalcap/cider/cider_scorer.py
# (authored by Tsung-Yi Lin <tl483@cornell.edu> and Ramakrishna Vedantam
# <vrama91@vt.edu>)

from typing import List, Dict, Tuple
from collections import defaultdict
import math
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
from tqdm import tqdm


def _batch(a_list: list, n_batches: int):
    batch_size = len(a_list) // n_batches + int(len(a_list) % n_batches > 0)
    for i in range(0, len(a_list), batch_size):
        yield a_list[i: min(i + batch_size, len(a_list))]


def _extract_sentence_n_grams(s: str, n: int = 4) -> Dict[Tuple[str], int]:
    """
    :param s: str : sentence to be converted into n-grams
    :param n: int : number of n-grams for which representation is calculated
    :return: term frequency vector for n-grams
    """
    words = s.split()
    counts = defaultdict(int)
    for k in range(1, n + 1):
        for i in range(len(words) - k + 1):
            ngram = tuple(words[i:i + k])
            counts[ngram] += 1
    return counts


def _batch_extract_n_grams(
        sentences: List[str], n: int = 4
) -> List[Dict[Tuple[str], int]]:
    return [_extract_sentence_n_grams(s, n) for s in sentences]


def _multiprocess_batch_extract_n_grams(
        sentences: List[str], n: int = 4, n_workers: int = 1,
        verbose: bool = False
) -> List[Dict[Tuple[str], int]]:
    if n_workers == 1:
        return _batch_extract_n_grams(sentences, n)
    else:
        batches = list(_batch(sentences, n_batches=n_workers))
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = {
                executor.submit(_batch_extract_n_grams, b, n): i
                for i, b in enumerate(batches)
            }
            progress = as_completed(futures)
            if verbose:
                progress = tqdm(progress)
            tmp = {futures[future]: future.result() for future in progress}
        result = []
        for k in sorted(tmp):
            result.extend(tmp[k])
        return result


class _CIDErScorer(object):
    def __init__(
            self, n: int = 4, sigma: float = 6.0, n_workers: int = 1,
            verbose: bool = False

    ):
        """
        :param n: int : number of n-grams for which representation is calculated
        :param sigma: float :
        """
        self.n = n
        self.sigma = sigma
        self.n_workers = n_workers
        self.verbose = verbose

        self.doc_freq = defaultdict(float)
        self.n_examples = 0
        self.ref_len = 1.
        self.refs = None

    def _counts_to_vec(
            self, counts: Dict[Tuple[str], int]
    ) -> Tuple[List[Dict[Tuple[str], float]], List[float], int]:
        """
        Function maps counts of ngram to vector of tf-idf weights.
        The function returns vec, an array of dictionary that store mapping of
        n-gram and tf-idf weights. The n-th entry of array denotes length of
        n-grams.
        :param counts:
        :return: vec (array of dict), norm (array of float), length (int)
        """
        vec = [defaultdict(float) for _ in range(self.n)]
        length = 0
        norm = [0.0 for _ in range(self.n)]
        for ngram, term_freq in counts.items():
            # Give word count 1 if it doesn't appear in reference corpus
            cur_doc_freq = np.log(max(1.0, self.doc_freq[ngram]))
            # ngram index
            n = len(ngram) - 1
            # tf (term_freq) * idf (precomputed idf) for n-grams
            vec[n][ngram] = float(term_freq) * (self.ref_len - cur_doc_freq)
            # Compute vector norm, use it for computing similarity
            norm[n] += pow(vec[n][ngram], 2)
            if n == 1:
                length += term_freq
        norm = [np.sqrt(n) for n in norm]
        return vec, norm, length

    def _get_sim(
            self, vec_h: List[Dict[Tuple[str], float]],
            vec_r: List[Dict[Tuple[str], float]], norm_h: List[float],
            norm_r: List[float], len_h: int, len_r: int, sigma: float
    ) -> np.ndarray:
        """
        Compute the cosine similarity of two vectors.
        :param vec_h: array of dictionary for vector corresponding to hypothesis
        :param vec_r: array of dictionary for vector corresponding to reference
        :param norm_h: array of float for vector corresponding to hypothesis
        :param norm_r: array of float for vector corresponding to reference
        :param len_h: int containing length of hypothesis
        :param len_r: int containing length of reference
        :param sigma: float
        :return: array of score for each n-grams cosine similarity
        """
        delta = float(len_h - len_r)
        # measure cosine similarity
        val = np.array([0.0 for _ in range(self.n)])
        for n in range(self.n):
            for ngram, count in vec_h[n].items():
                val[n] += min(
                    vec_h[n][ngram], vec_r[n][ngram]
                ) * vec_r[n][ngram]
            if norm_h[n] != 0 and norm_r[n] != 0:
                val[n] /= norm_h[n] * norm_r[n]
            assert not math.isnan(val[n])
            val[n] *= np.e ** (-(delta ** 2) / (2 * sigma ** 2))
        return val

    def _get_idf(self, references: List[List[str]]):
        self.refs = [
            _multiprocess_batch_extract_n_grams(
                r, n=self.n, n_workers=self.n_workers, verbose=self.verbose
            ) for r in references
        ]
        for cur_refs in zip(*self.refs):
            for ngram in set(ngram for r in cur_refs for ngram, c in r.items()):
                self.doc_freq[ngram] += 1

    def get_sent_scores(
            self, hypothesis: List[str], references: List[List[str]]
    ) -> List[float]:
        self.n_examples = len(hypothesis)
        self.ref_len = np.log(self.n_examples)

        self._get_idf(references)

        scores = []
        hypo = _multiprocess_batch_extract_n_grams(
            hypothesis, self.n, self.n_workers, self.verbose
        )
        for h, cur_refs in zip(hypo, self.refs):
            vec_h, norm_h, len_h = self._counts_to_vec(h)
            score = np.array([0.0 for _ in range(self.n)])
            for r in cur_refs:
                vec_r, norm_r, len_r = self._counts_to_vec(r)
                score += self._get_sim(
                    vec_h, vec_r, norm_h, norm_r, len_h, len_r, self.sigma
                )
            score_avg = np.mean(score) / len(cur_refs) * 10.0
            scores.append(score_avg)
        return scores
