# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
from functools import lru_cache
from typing import Optional

from google.cloud import translate

from vizseq._utils.logger import logger


def set_g_cred_path(path: str):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path


@lru_cache(maxsize=256)
def get_g_translate(sent: str, lang: str) -> Optional[str]:
    """Translate a sentence using Google Translate API.

    Args:
        sent: The sentence to translate.
        lang: Target language code.

    Returns:
        Translated text, or None if translation fails.
    """
    try:
        client = translate.Client()
        t = client.translate(sent, target_language=lang)['translatedText']
        return t
    except Exception as e:
        logger.warn(f'Google Translate error: {e}')
        return None
