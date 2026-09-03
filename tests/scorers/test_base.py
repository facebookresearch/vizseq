# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from vizseq.scorers import MAX_WINDOWS_WORKERS, VizSeqScorer


class VizSeqScorerBaseTestCase(unittest.TestCase):
    @patch('vizseq.scorers._available_cpu_count', return_value=128)
    @patch('vizseq.scorers.sys.platform', 'win32')
    def test_windows_worker_count_is_capped(self, _cpu_count):
        automatically_scaled = VizSeqScorer()
        explicitly_scaled = VizSeqScorer(n_workers=100)

        automatically_scaled._update_n_workers(62_000)

        self.assertEqual(
            automatically_scaled.n_workers, MAX_WINDOWS_WORKERS
        )
        self.assertEqual(explicitly_scaled.n_workers, MAX_WINDOWS_WORKERS)
