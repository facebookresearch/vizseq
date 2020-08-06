# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from enum import Enum

from sacrebleu.tokenizers import (Tokenizer13a, TokenizerV14International,
                                 TokenizerZh)


class VizSeqTokenization(Enum):
    none = 0
    mteval_13a = 1
    mteval_v14_international = 2
    zh = 3
    char = 4


def _tokenize_by_char(line: str) -> str:
    return ' '.join(list(line.strip()))


class VizSeqTokenizer(object):
    @classmethod
    def tokenize_line(cls, line: str, tokenization: VizSeqTokenization) -> str:
        if tokenization == VizSeqTokenization.none:
            return line
        elif tokenization == VizSeqTokenization.mteval_13a:
            return Tokenizer13a()(line)
        elif tokenization == VizSeqTokenization.mteval_v14_international:
            return TokenizerV14International()(line)
        elif tokenization == VizSeqTokenization.zh:
            return TokenizerZh()(line)
        elif tokenization == VizSeqTokenization.char:
            return _tokenize_by_char(line)
        else:
            raise ValueError(f'Unknown tokenization {tokenization.name}')
