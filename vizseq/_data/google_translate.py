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
from google.api_core import exceptions as google_exceptions

from vizseq._utils.logger import logger


def set_g_cred_path(path: str):
    """Set the Google Application Credentials environment variable.

    Args:
        path: Path to the Google credentials JSON file.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the path is not a file or not a JSON file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f'Credentials file not found: {path}')
    if not os.path.isfile(path):
        raise ValueError(f'Credentials path is not a file: {path}')
    if not path.endswith('.json'):
        raise ValueError('Credentials must be a JSON file')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(path)


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
    except google_exceptions.GoogleAPIError as e:
        logger.warning(f'Google Translate API error: {e}')
        return None
    except KeyError as e:
        logger.warning(f'Unexpected Google Translate response format: {e}')
        return None
