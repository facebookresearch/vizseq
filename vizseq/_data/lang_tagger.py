# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Optional

import langid
import logging
logging.getLogger("langid").setLevel(logging.WARNING)


class VizSeqLanguageTagger(object):
    POTENTIAL_UNSEGMENTED_LANGUAGES = {'zh', 'ja', 'th'}

    @classmethod
    def tag_lang_pair(cls, src: str, ref: Optional[str]) -> List[str]:
        machine_tags = []
        src_lang = langid.classify(src)[0]
        ref_lang = None if ref is None else langid.classify(ref)[0]
        if ref is not None and src_lang == ref_lang:
            machine_tags.append(f'lang: {ref_lang}')
        else:
            machine_tags.append(f'src_lang: {src_lang}')
            if ref is not None:
                machine_tags.append(f'trg_lang: {ref_lang}')

        if ref_lang is not None \
                and ref_lang in cls.POTENTIAL_UNSEGMENTED_LANGUAGES \
                and ref.find(' ') == -1:
            machine_tags.append('unsegmented_trg')
        return machine_tags

    @classmethod
    def tag_lang(cls, ref: str) -> str:
        return langid.classify(ref)[0]
