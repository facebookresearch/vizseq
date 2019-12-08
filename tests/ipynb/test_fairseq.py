# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


from . import VizSeqIpynbTestCase
from vizseq.ipynb.fairseq_viz import (view_stats, view_examples, view_n_grams,
                                      view_scores)


class VizSeqIpynbFairSeqTestCase(VizSeqIpynbTestCase):
    def setUp(self) -> None:
        self.log_paths = [
            'examples/data/wmt14_fr_en_test.fairseq_generate.log',
            'examples/data/wmt14_fr_en_test.fairseq_generate.log'
        ]

    def test_view_stats(self):
        _ = view_stats(self.log_paths[0])

    def test_view_examples(self):
        _ = view_examples(self.log_paths[0])
        _ = view_examples(self.log_paths)

    def test_view_scores(self):
        _ = view_scores(self.log_paths[0], ['bleu'])

    def test_view_n_grams(self):
        _ = view_n_grams(self.log_paths[0])
