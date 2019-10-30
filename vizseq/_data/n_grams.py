# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import Dict, List, Tuple
from collections import Counter

from tqdm import tqdm

from vizseq._data import VizSeqDataSources

MAX_K = 256


class VizSeqNGrams(object):
    MAX_N = 4
    SPACE = ' '

    @classmethod
    # TODO: multi-process implementation
    def extract(
            cls, data: VizSeqDataSources, k=MAX_K, verbose=False
    ) -> Dict[int, List[Tuple[str, int]]]:
        k = max(1, min(k, MAX_K))
        count = {n: Counter() for n in range(1, cls.MAX_N + 1)}
        text = data.text
        if not data.text_merged:
            text = zip(*text)
        progress = enumerate(text)
        if verbose:
            progress = tqdm(progress)
        for i, e in progress:
            for s in e:
                tokens = s.lower().split(cls.SPACE)
                for t in range(len(tokens)):
                    for n in range(1, min(cls.MAX_N, len(tokens) - t) + 1):
                        n_gram = cls.SPACE.join(tokens[t: t + n])
                        count[n].update([n_gram])

        for n in range(1, cls.MAX_N + 1):
            count[n] = count[n].most_common(k)

        return count
