# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from . import VizSeqScorerTestCase
from vizseq.scorers.laser import LaserScorer


class LaserScorerTestCase(VizSeqScorerTestCase):
    def test(self):
        return self._test_embedding_based(
            LaserScorer, extra_args={'laser_trg_lang': 'de'}
        )
