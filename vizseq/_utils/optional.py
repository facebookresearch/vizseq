# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


from typing import Optional, Dict, Any


def get_optional_dict(
        maybe_dict: Optional[Dict[str, str]], key: str, default: Any
) -> Optional[Any]:
    if maybe_dict is None:
        return default
    return maybe_dict.get(key, default)


def map_optional(obj: Optional[Any], map_fn: callable):
    return None if obj is None else map_fn(obj)
