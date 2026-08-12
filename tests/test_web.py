# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import io
import json
import os
import tempfile
import unittest
import urllib.parse
import zipfile

from tornado.testing import AsyncHTTPTestCase

from vizseq import server
from vizseq._data import VizSeqDataSources
from vizseq._view.data_view import VizSeqDataPageView
from vizseq._view import mem_cached_data_getters


XSS_PAYLOAD = '</script><script>alert("vizseq-xss")</script>'


def _clear_data_caches():
    mem_cached_data_getters._get_src.cache_clear()
    mem_cached_data_getters._get_ref.cache_clear()
    mem_cached_data_getters._get_tag.cache_clear()
    mem_cached_data_getters._get_scores.cache_clear()
    mem_cached_data_getters.__get_hypo.cache_clear()


class VizSeqDataPageViewTestCase(unittest.TestCase):
    def setUp(self):
        lines = ['zero', 'one', 'two', 'three', 'four', 'five']
        self.sources = VizSeqDataSources({'source': lines})
        self.references = VizSeqDataSources({'reference': lines})
        self.hypothesis = VizSeqDataSources({'model': lines})

    def test_empty_search_returns_an_empty_page(self):
        page = VizSeqDataPageView.get(
            self.sources,
            self.references,
            self.hypothesis,
            page_sz=2,
            page_no=1,
            query='not present',
            disable_alignment=True,
        )

        self.assertEqual(page.cur_idx, [])
        self.assertEqual(page.n_samples, 0)
        self.assertEqual(page.n_cur_samples, 0)

    def test_out_of_range_page_is_clamped_to_the_last_full_page(self):
        page = VizSeqDataPageView.get(
            self.sources,
            self.references,
            self.hypothesis,
            page_sz=2,
            page_no=99,
            disable_alignment=True,
        )

        self.assertEqual(page.cur_idx, [4, 5])


class VizSeqWebTestCase(AsyncHTTPTestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir.name
        self.data_root = os.path.join(self.temp_dir.name, 'data')
        self.task_root = os.path.join(self.data_root, 'test_task')
        os.makedirs(self.task_root)

        sources = ['zero', XSS_PAYLOAD, 'two', 'three', 'four', 'five']
        references = ['zero', 'one', 'two', 'three', 'four', 'five']
        predictions = ['wrong', 'one', 'wrong', 'three', 'wrong', 'five']
        tags = ['safe', XSS_PAYLOAD, 'safe', 'safe', 'safe', 'safe']
        self._write_lines('src_0.txt', sources)
        self._write_lines('ref_0.txt', references)
        self._write_lines('pred_model.txt', predictions)
        self._write_lines('tag_0.txt', tags)

        server.args = argparse.Namespace(data_root=self.data_root)
        _clear_data_caches()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        _clear_data_caches()
        if self.old_home is None:
            os.environ.pop('HOME', None)
        else:
            os.environ['HOME'] = self.old_home
        self.temp_dir.cleanup()

    def get_app(self):
        return server.make_app()

    def _write_lines(self, filename, lines):
        with open(os.path.join(self.task_root, filename), 'w') as file:
            file.write('\n'.join(lines) + '\n')

    def _view_url(self, **params):
        query = {'t': 'test_task', 'm': 'model'}
        query.update(params)
        return '/view?' + urllib.parse.urlencode(query)

    @staticmethod
    def _multipart_zip(filename, zip_bytes):
        boundary = b'vizseq-test-boundary'
        body = b'\r\n'.join([
            b'--' + boundary,
            b'Content-Disposition: form-data; name="file1"; filename="'
            + filename.encode('ascii') + b'"',
            b'Content-Type: application/zip',
            b'',
            zip_bytes,
            b'--' + boundary + b'--',
            b'',
        ])
        content_type = 'multipart/form-data; boundary=' + boundary.decode('ascii')
        return body, content_type

    def test_view_escapes_script_payloads_in_html_and_javascript(self):
        response = self.fetch(self._view_url(q=XSS_PAYLOAD))
        body = response.body.decode('utf-8')

        self.assertEqual(response.code, 200)
        self.assertNotIn(XSS_PAYLOAD, body)
        self.assertIn(r'\u003c/script\u003e', body)
        self.assertIn('&lt;/script&gt;', body)
        self.assertNotIn('javascript:getGTranslate', body)

    def test_empty_search_renders_a_valid_empty_state(self):
        response = self.fetch(self._view_url(q='not present'))

        self.assertEqual(response.code, 200)
        self.assertIn(
            b'No examples match the current search.', response.body
        )

    def test_invalid_pagination_and_sorting_return_400(self):
        for params in ({'p_no': 0}, {'p_sz': 101}, {'s': 999}):
            with self.subTest(params=params):
                response = self.fetch(self._view_url(**params))
                self.assertEqual(response.code, 400)

    def test_page_data_forwards_metric_sorting_and_returns_json(self):
        query = urllib.parse.urlencode({
            't': 'test_task',
            'm': 'model',
            's': 6,
            's_metric': 'wer',
        })
        response = self.fetch('/page_data?' + query)
        payload = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertTrue(
            response.headers['Content-Type'].startswith('application/json')
        )
        self.assertEqual(payload['cur_idx'][:3], [1, 3, 5])

    def test_page_tags_follow_paginated_indices(self):
        response = self.fetch(self._view_url(p_sz=2, p_no=2))
        body = response.body.decode('utf-8')

        self.assertEqual(response.code, 200)
        self.assertNotIn('badge badge-primary">&lt;/script', body)

    def test_upload_rejects_path_traversal_and_removes_temporary_zip(self):
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w') as zip_file:
            zip_file.writestr('../escaped.txt', 'unsafe')
        body, content_type = self._multipart_zip('malicious.zip', archive.getvalue())

        response = self.fetch(
            '/upload',
            method='POST',
            headers={'Content-Type': content_type},
            body=body,
            follow_redirects=False,
        )

        self.assertEqual(response.code, 400)
        self.assertFalse(os.path.exists(os.path.join(self.data_root, 'malicious.zip')))
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir.name, 'escaped.txt')))

    def test_upload_rejects_corrupt_archives_and_missing_files(self):
        body, content_type = self._multipart_zip('corrupt.zip', b'not a zip')
        corrupt_response = self.fetch(
            '/upload',
            method='POST',
            headers={'Content-Type': content_type},
            body=body,
            follow_redirects=False,
        )
        missing_response = self.fetch('/upload', method='POST', body=b'')

        self.assertEqual(corrupt_response.code, 400)
        self.assertEqual(missing_response.code, 400)
        self.assertFalse(os.path.exists(os.path.join(self.data_root, 'corrupt.zip')))


if __name__ == '__main__':
    unittest.main()
