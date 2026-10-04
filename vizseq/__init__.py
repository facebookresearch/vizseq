# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('vizseq')
except PackageNotFoundError:
    __version__ = '0+unknown'

from vizseq.ipynb import (  # noqa: E402  (must follow __version__ setup)
    VizSeqSortingType,
    available_scorers,
    set_google_credential_path,
    view_examples,
    view_n_grams,
    view_scores,
    view_stats,
)
from vizseq.ipynb import fairseq_viz as fairseq  # noqa: E402

__all__ = [
    '__version__',
    'VizSeqSortingType',
    'available_scorers',
    'fairseq',
    'set_google_credential_path',
    'view_examples',
    'view_n_grams',
    'view_scores',
    'view_stats',
]
