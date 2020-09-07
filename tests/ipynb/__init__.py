# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest
import os


class VizSeqIpynbTestCase(unittest.TestCase):
    def setUp(self) -> None:
        dataset_root = 'examples/data/translation_wmt14_en_de_test'
        if not os.path.isdir(dataset_root):
            raise NotADirectoryError(f'{dataset_root} does not exist.')
        with open(f'{dataset_root}/src_0.txt') as f:
            self.source = {'src': [l.strip() for l in f]}
        with open(f'{dataset_root}/ref_0.txt') as f:
            self.references = {'ref': [l.strip() for l in f]}
        with open(f'{dataset_root}/pred_onlineA.0.txt') as f:
            self.hypothesis = {'hypo': [l.strip() for l in f]}
        self.tags = {'tag': ['default' for _ in self.source]}

    def test_view_stats(self):
        pass

    def test_view_examples(self):
        pass

    def test_view_scores(self):
        pass

    def test_view_n_grams(self):
        pass
