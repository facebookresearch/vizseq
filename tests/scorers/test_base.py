# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from vizseq.scorers import (
    MAX_WINDOWS_WORKERS, VizSeqScorer, _max_workers_for_platform,
)


class VizSeqScorerBaseTestCase(unittest.TestCase):
    def test_max_workers_for_windows_is_capped(self):
        self.assertEqual(
            _max_workers_for_platform(128, 'win32'), MAX_WINDOWS_WORKERS
        )
        self.assertEqual(_max_workers_for_platform(128, 'linux'), 127)

    @patch(
        'vizseq.scorers._max_workers_for_platform',
        return_value=MAX_WINDOWS_WORKERS,
    )
    def test_worker_count_respects_platform_limit(self, _max_workers):
        automatically_scaled = VizSeqScorer()
        explicitly_scaled = VizSeqScorer(n_workers=100)

        automatically_scaled._update_n_workers(62_000)

        self.assertEqual(
            automatically_scaled.n_workers, MAX_WINDOWS_WORKERS
        )
        self.assertEqual(explicitly_scaled.n_workers, MAX_WINDOWS_WORKERS)
