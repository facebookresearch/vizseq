# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import Dict

import pandas as pd

pd.options.display.float_format = '{:,.2f}'.format


class VizSeqTableExporter(object):
    @classmethod
    def to_latex(cls, table: Dict[str, float]):
        return pd.DataFrame(table).transpose().to_latex()

    @classmethod
    def to_csv(cls, table: Dict[str, float]):
        return pd.DataFrame(table).transpose().to_csv()
