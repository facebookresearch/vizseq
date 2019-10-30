# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os.path as op
from typing import List, NamedTuple, Any

from vizseq._utils.json import VizSeqJson
from vizseq.scorers import get_scorer_ids
from .tokenizers import VizSeqTokenization


DEFAULT_TASK_NAME = ''
DEFAULT_TASK_DESCRIPTION = ''
DEFAULT_METRICS = []
DEFAULT_G_CRED_PATH = ''
DEFAULT_TOKENIZATION = 'none'


class VizSeqTaskConfig(NamedTuple):
    task_name: str = DEFAULT_TASK_NAME
    description: str = DEFAULT_TASK_DESCRIPTION
    metrics: List[str] = DEFAULT_METRICS
    tokenization: str = DEFAULT_TOKENIZATION


class VizSeqGlobalConfig(NamedTuple):
    g_cred_path: str = DEFAULT_G_CRED_PATH


class VizSeqBaseConfigManager(object):
    JSON_FILENAME = '__vizseq_cfg__.json'

    def __init__(self, root: str, config_cls: NamedTuple):
        self.root = root
        self.path = op.join(root, self.JSON_FILENAME)
        if op.exists(self.path):
            self.cfg = VizSeqJson.load_from_path(self.path)
        else:
            self.cfg = config_cls()._asdict()
            VizSeqJson.dump_to_path(self.cfg, self.path)

    def get(self, key: str, default=None):
        return self.cfg.get(key, default)

    def update(self, key: str, value: Any) -> None:
        self.cfg[key] = value
        self.flush()

    def flush(self) -> None:
        with open(self.path, 'w') as f:
            VizSeqJson.dump(self.cfg, f)

    @property
    def dict(self):
        return self.cfg


class VizSeqTaskConfigManager(VizSeqBaseConfigManager):
    def __init__(self, root: str):
        super().__init__(root, VizSeqTaskConfig)

    @property
    def task_name(self) -> str:
        return self.get('task_name', DEFAULT_TASK_NAME)

    def set_task_name(self, task_name: str) -> None:
        return self.update('task_name', task_name)

    @property
    def description(self) -> str:
        return self.get('description', DEFAULT_TASK_DESCRIPTION)

    def set_description(self, description: str):
        return self.update('description', description)

    @property
    def metrics(self) -> List[str]:
        return self.get('metrics', DEFAULT_METRICS)

    def set_metrics(self, metrics: List[str]) -> None:
        all_metrics = set(get_scorer_ids())
        for m in metrics:
            if m not in all_metrics:
                raise ValueError(f'{m} is not a valid metric.')
        return self.update('metrics', metrics)

    @property
    def tokenization(self):
        return self.get('tokenization', DEFAULT_TOKENIZATION)

    def set_tokenization(self, tokenizaton: str) -> None:
        all_tokenizations = set(t.name for t in VizSeqTokenization)
        for t in tokenizaton:
            if t not in all_tokenizations:
                raise ValueError(f'{t} is not a valid tokenization.')
        return self.update('tokenization', tokenizaton)


class VizSeqGlobalConfigManager(VizSeqBaseConfigManager):
    def __init__(self):
        super().__init__(op.expanduser('~'), VizSeqGlobalConfig)

    @property
    def g_cred_path(self) -> str:
        return self.get('g_cred_path', DEFAULT_G_CRED_PATH)

    def set_g_cred_path(self, value: str):
        self.update('g_cred_path', value)
