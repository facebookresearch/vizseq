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

from vizseq.ipynb import *  # noqa: F401, F403, E402
from vizseq.ipynb import fairseq_viz as fairseq  # noqa: E402
