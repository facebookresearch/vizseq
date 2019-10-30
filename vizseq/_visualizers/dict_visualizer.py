# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from jinja2 import Markup


class VizSeqDictVisualizer(object):
    WORSE_MD_TEMPLATE = '<span style="font-style:italic"><u>{}</u></span>'
    BEST_MD_TEMPLATE = '<span style="font-weight:bold">{}</span>'

    # TODO: deal with tied values
    @classmethod
    def visualize(cls, a_dict: dict, by_min=False):
        if len(a_dict) == 0:
            return a_dict
        sorted_values = sorted(a_dict.values(), reverse=not by_min)
        best_v, worst_v = sorted_values[0], sorted_values[-1]
        result = {}
        for k, v in a_dict.items():
            if v == best_v:
                result[k] = Markup(cls.BEST_MD_TEMPLATE.format(v))
            elif v == worst_v:
                result[k] = Markup(cls.WORSE_MD_TEMPLATE.format(v))
            else:
                result[k] = str(v)
        return result
