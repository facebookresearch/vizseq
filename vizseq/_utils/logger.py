# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import logging
import time
from datetime import timedelta


class VizSeqLogFormatter(object):
    def __init__(self):
        self.start_time = time.time()

    def format(self, record: logging.LogRecord):
        elapsed_seconds = round(record.created - self.start_time)

        prefix = "{} - {} - {}".format(
            record.levelname,
            time.strftime('%x %X'),
            timedelta(seconds=elapsed_seconds)
        )
        message = record.getMessage()
        message = message.replace('\n', '\n' + ' ' * (len(prefix) + 3))
        return "{} - {}".format(prefix, message)


class VizSeqLogger(object):
    def __init__(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(VizSeqLogFormatter())
        # create logger and set level to debug
        self._logger = logging.getLogger()
        self._logger.handlers = []
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False
        self._logger.addHandler(console_handler)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)


logger = VizSeqLogger()
