# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


from typing import List


# TODO: scale this part
class VizSeqFilter(object):
    @classmethod
    def filter(cls, data: List[List[str]], query: str) -> List[int]:
        if len(query) == 0:
            return list(range(len(data[0])))

        indices = []
        for i, cur_list in enumerate(zip(*data)):
            if any(s.find(query) > -1 for s in cur_list):
                indices.append(i)

        return indices
