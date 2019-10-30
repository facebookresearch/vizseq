# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import json
from typing import Any


class VizSeqJson(object):
    @classmethod
    def load(cls, fp) -> Any:
        return json.load(fp)

    @classmethod
    def load_from_path(cls, path: str) -> Any:
        with open(path) as f:
            return cls.load(f)

    @classmethod
    def dump(cls, obj: Any, fp):
        return json.dump(obj, fp, indent=4, sort_keys=True)

    @classmethod
    def dumps(cls, obj: Any) -> str:
        return json.dumps(obj)

    @classmethod
    def dump_to_path(cls, obj: Any, path: str):
        with open(path, 'w') as f:
            return cls.dump(obj, f)
