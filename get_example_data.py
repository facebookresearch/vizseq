#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.

"""Download and extract a VizSeq example dataset."""

import argparse
import re
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional


DEFAULT_TASK = 'translation_wmt14_en_de_test'
DATA_URL = 'https://dl.fbaipublicfiles.com/vizseq/examples/data'
TASK_NAME = re.compile(r'^[A-Za-z0-9_.-]+$')


def _safe_extract(archive_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            member_path = Path(member.filename)
            if member_path.is_absolute() or '..' in member_path.parts:
                raise ValueError(
                    f'Archive contains an unsafe path: {member.filename}'
                )
            target = (destination / member_path).resolve()
            if not target.is_relative_to(destination):
                raise ValueError(
                    f'Archive contains an unsafe path: {member.filename}'
                )
        archive.extractall(destination)


def download_example_data(
        task: str = DEFAULT_TASK, data_root: Optional[Path] = None,
        data_url: str = DATA_URL,
) -> Path:
    if (
            not TASK_NAME.fullmatch(task)
            or task in {'.', '..'}
            or Path(task).name != task
    ):
        raise ValueError(f'Invalid task name: {task}')

    if data_root is None:
        data_root = Path(__file__).resolve().parent / 'examples' / 'data'
    else:
        data_root = Path(data_root)
    destination = data_root / task
    if destination.is_dir():
        print(f'Example data already exists at {destination}')
        return destination

    data_root.mkdir(parents=True, exist_ok=True)
    url = f'{data_url.rstrip("/")}/{task}.zip'
    with tempfile.TemporaryDirectory(
            prefix='.vizseq-download-', dir=data_root
    ) as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        archive_path = temp_dir / f'{task}.zip'
        extracted_root = temp_dir / 'extracted'
        extracted_root.mkdir()

        print(f'Downloading {url}')
        try:
            with (
                    urllib.request.urlopen(url) as response,
                    archive_path.open('wb') as output,
            ):
                shutil.copyfileobj(response, output)
        except urllib.error.HTTPError as error:
            if error.code in {403, 404}:
                raise SystemExit(
                    f'No example dataset named {task!r} was found.'
                ) from error
            raise
        _safe_extract(archive_path, extracted_root)

        extracted_task = extracted_root / task
        if not extracted_task.is_dir():
            raise ValueError(f'Archive does not contain the expected {task} directory')
        shutil.move(str(extracted_task), destination)

    print(f'Example data extracted to {destination}')
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task', nargs='?', default=DEFAULT_TASK)
    args = parser.parse_args()
    download_example_data(args.task)


if __name__ == '__main__':
    main()
