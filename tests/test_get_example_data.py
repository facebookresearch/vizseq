# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import tempfile
import unittest
import zipfile
from pathlib import Path

from get_example_data import _safe_extract, download_example_data


class ExampleDataDownloadTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_root = self.root / 'data'
        self.source_root = self.root / 'source'
        self.source_root.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_archive(self, task, members):
        archive_path = self.source_root / f'{task}.zip'
        with zipfile.ZipFile(archive_path, 'w') as archive:
            for name, content in members.items():
                archive.writestr(name, content)
        return archive_path

    def test_downloads_and_extracts_dataset(self):
        task = 'example_task'
        self._write_archive(task, {f'{task}/src_0.txt': 'hello\n'})

        destination = download_example_data(
            task, self.data_root, self.source_root.as_uri()
        )

        self.assertEqual(destination, self.data_root / task)
        self.assertEqual((destination / 'src_0.txt').read_text(), 'hello\n')

    def test_existing_dataset_is_not_downloaded_again(self):
        destination = self.data_root / 'example_task'
        destination.mkdir(parents=True)

        result = download_example_data(
            'example_task', self.data_root, 'not-a-valid-url'
        )

        self.assertEqual(result, destination)

    def test_rejects_archive_path_traversal(self):
        task = 'example_task'
        archive_path = self._write_archive(task, {
            f'{task}/src_0.txt': 'hello\n',
            '../escaped.txt': 'unsafe\n',
        })
        extracted_root = self.root / 'extracted'
        extracted_root.mkdir()

        with self.assertRaisesRegex(ValueError, 'unsafe path'):
            _safe_extract(archive_path, extracted_root)

        self.assertFalse((extracted_root.parent / 'escaped.txt').exists())

    def test_rejects_invalid_task_name(self):
        with self.assertRaisesRegex(ValueError, 'Invalid task name'):
            download_example_data('../example_task', self.data_root)


if __name__ == '__main__':
    unittest.main()
