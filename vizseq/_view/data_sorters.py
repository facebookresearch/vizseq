# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Dict
from enum import Enum

import numpy as np


class VizSeqSortingType(Enum):
    original = 0
    random = 1
    ref_len = 2
    ref_alphabetical = 3
    src_len = 4
    src_alphabetical = 5
    metric = 6


class VizSeqOriginalSorter(object):
    @classmethod
    def sort(cls, data: List[str]):
        return list(range(len(data)))


class VizSeqRandomSorter(object):
    @classmethod
    def sort(cls, indices: List[int]):
        np.random.seed(seed=1)
        n_examples = len(indices)
        return [indices[i] for i in np.random.permutation(n_examples)]


class VizSeqByLenSorter(object):
    @classmethod
    def sort(cls, data: List[str], indices: List[int]):
        sent_lens = [len(data[i].split(' ')) for i in indices]
        return [indices[i] for i in np.argsort(sent_lens).tolist()[::-1]]


class VizSeqByStrOrderSorter(object):
    @classmethod
    def sort(cls, data: List[str], indices: List[int]):
        sorted_indices = np.argsort([data[i] for i in indices])
        return [indices[i] for i in sorted_indices]


class VizSeqByMetricSorter(object):
    @classmethod
    def sort(cls, scores: List[Dict[str, float]], indices: List[int]):
        """
        :param scores: List of model-score dictionaries
        :param indices:
        :return:
        """
        avg_scores = [np.mean(list(s.values())) for s in scores]
        sorted_indices = np.argsort(avg_scores)
        return [indices[i] for i in sorted_indices]
