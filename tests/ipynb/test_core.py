# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from . import VizSeqIpynbTestCase
from vizseq.ipynb.core import (view_stats, view_examples, view_n_grams,
                               view_scores)


class VizSeqIpynbCoreTestCase(VizSeqIpynbTestCase):
    def test_view_stats(self):
        _ = view_stats(self.source, self.references)

    def test_view_examples(self):
        _ = view_examples(self.source, self.references, self.hypothesis)

    def test_view_scores(self):
        _ = view_scores(self.references, self.hypothesis, ['bleu'])
        _ = view_scores(self.references, self.hypothesis, ['rouge_1'],
                        tags=self.tags)

    def test_view_n_grams(self):
        _ = view_n_grams(self.references)
