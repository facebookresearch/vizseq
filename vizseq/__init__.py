# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os.path as op

with open(op.join('vizseq', 'VERSION')) as f:
    __version__ = f.read()

from vizseq.ipynb import *
from vizseq.ipynb import fairseq_viz as fairseq
