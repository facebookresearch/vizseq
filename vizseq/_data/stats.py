# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from collections import Counter, defaultdict
from typing import List, NamedTuple, Optional, Tuple, Union, Dict

import numpy as np

from vizseq._data import VizSeqDataSources


class VizSeqStatsResult(NamedTuple):
    n_examples: int
    # number of tokens for text, number of filter bank feature frames for speech
    n_src_tokens: Dict[str, int]
    n_ref_tokens: Dict[str, int]
    # number of chars for text, duration (ms) for speech
    n_src_chars: Dict[str, int]
    n_ref_chars: Dict[str, int]
    tag_freq: List[Tuple[str, int]]
    src_vocab: Dict[str, List[Tuple[str, int]]]
    ref_vocab: Dict[str, List[Tuple[str, int]]]
    src_tkn_log2_freq: Dict[str, List[float]]
    ref_tkn_log2_freq: Dict[str, List[float]]
    src_lens: Dict[str, List[int]]
    ref_lens: Dict[str, List[int]]

    def to_dict(self, formatting: bool = True) -> Dict:
        r = self._asdict()

        if formatting:
            def _format(d):
                if isinstance(d, (int, float)):
                    return f'{d:,}'
                elif isinstance(d, dict):
                    return {k: _format(v) for k, v in d.items()}
                else:
                    return d

            return {k: _format(v) for k, v in r.items()}

        return r


class VizSeqStats(object):
    MAX_SAMPLES = 4096

    @classmethod
    def auto_sample(cls, data: Union[List[int], List[float]]):
        n = len(data)
        if n > cls.MAX_SAMPLES:
            return [data[i] for i in range(0, n, n // cls.MAX_SAMPLES)]
        return data

    @classmethod
    def get(
            cls, src: VizSeqDataSources, ref: VizSeqDataSources,
            tags: Optional[VizSeqDataSources] = None
    ) -> VizSeqStatsResult:
        n_examples = len(src)
        n_src_tokens, n_ref_tokens = defaultdict(int), defaultdict(int)
        n_src_chars, n_ref_chars = defaultdict(int), defaultdict(int)
        src_vocab, ref_vocab = {}, {}
        src_lens, ref_lens = defaultdict(list), defaultdict(list)
        tag_freq = Counter()

        for name, cur_src in zip(src.names, src.data):
            for i in range(len(cur_src)):
                src_lens[name].append(cur_src.get_len(i))
                n_src_chars[name] += cur_src.get_len(i, finer=True)
            src_vocab[name] = cur_src.vocab
            n_src_tokens[name] = sum(src_lens[name])
            src_lens[name] = cls.auto_sample(src_lens[name])
            if n_src_chars[name] == 0:
                src_lens[name] = []

        for name, cur_ref in zip(ref.names, ref.data):
            for i in range(len(cur_ref)):
                ref_lens[name].append(cur_ref.get_len(i))
                n_ref_chars[name] += cur_ref.get_len(i, finer=True)
            ref_vocab[name] = cur_ref.vocab
            n_ref_tokens[name] = sum(ref_lens[name])
            ref_lens[name] = cls.auto_sample(ref_lens[name])
            if n_ref_chars[name] == 0:
                ref_lens[name] = []

        if tags is not None:
            assert tags.text_merged
            for cur_tags in tags.text:
                tag_freq.update(cur_tags)
        tag_freq = tag_freq.most_common()
        src_tkn_log2_freq = {
            k: cls.auto_sample([np.round(np.log2(f + 1), 2) for _, f in v])
            for k, v in src_vocab.items()
        }
        ref_tkn_log2_freq = {
            k: cls.auto_sample([np.round(np.log2(f + 1), 2) for _, f in v])
            for k, v in ref_vocab.items()
        }
        return VizSeqStatsResult(
            n_examples=n_examples,
            n_src_tokens=n_src_tokens,
            n_ref_tokens=n_ref_tokens,
            n_src_chars=n_src_chars,
            n_ref_chars=n_ref_chars,
            tag_freq=tag_freq,
            src_vocab=src_vocab,
            ref_vocab=ref_vocab,
            src_tkn_log2_freq=src_tkn_log2_freq,
            ref_tkn_log2_freq=ref_tkn_log2_freq,
            src_lens=src_lens,
            ref_lens=ref_lens,
        )
