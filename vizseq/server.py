# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import json
import os
import os.path as op
import argparse
import re
import math
import zipfile
from typing import List

from vizseq._utils.logger import logger

from vizseq._view import (VizSeqWebView, DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NO,
                          MAX_PAGE_SZ, VizSeqSortingType)
from vizseq._data.zip_file import VizSeqZipFile, ZipExtractionError
from vizseq._data import (get_g_translate, set_g_cred_path,
                          VizSeqGlobalConfigManager)
from vizseq._visualizers import SPAN_HIGHTLIGHT_JS
from vizseq._utils import VizSeqJson
from vizseq import __version__
from vizseq.scorers import get_scorer_ids

from tornado import web, ioloop
from jinja2 import Environment, PackageLoader, select_autoescape

DEFAULT_HOSTNAME = 'localhost'
DEFAULT_PORT = 9001


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname', type=str, default=DEFAULT_HOSTNAME,
                        help='address to bind to. Defaults to localhost, so '
                             'the server is only reachable from this machine; '
                             'pass 0.0.0.0 to expose it on the network')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help='server port number')
    parser.add_argument('--data-root', type=str, default='./examples/data',
                        help='root path to data')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    return parser.parse_args()


args = argparse.Namespace(data_root='./examples/data')

env = Environment(
    loader=PackageLoader('vizseq', '_templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Pattern for safe path components: alphanumeric, underscore, hyphen, dot (but not ..)
SAFE_PATH_COMPONENT = re.compile(r'^[a-zA-Z0-9_\-\.]+$')


def validate_path_component(value: str, name: str = 'parameter') -> str:
    """Validate a path component to prevent directory traversal attacks."""
    if not value:
        raise web.HTTPError(400, f'Empty {name}')
    if '..' in value or '/' in value or '\\' in value:
        raise web.HTTPError(400, f'Invalid {name}: path traversal not allowed')
    if not SAFE_PATH_COMPONENT.match(value):
        raise web.HTTPError(400, f'Invalid {name}: contains disallowed characters')
    return value


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent directory traversal."""
    # Extract just the filename, removing any path components
    filename = op.basename(filename)
    if not filename:
        raise web.HTTPError(400, 'Invalid filename')
    if '..' in filename:
        raise web.HTTPError(400, 'Invalid filename: path traversal not allowed')
    # Only allow safe characters in filenames
    if not SAFE_PATH_COMPONENT.match(filename):
        raise web.HTTPError(400, 'Invalid filename: contains disallowed characters')
    return filename


class VizSeqBaseRequestHandler(web.RequestHandler):
    def write_json(self, value: str) -> None:
        self.set_header('Content-Type', 'application/json')
        self.write(value)

    def render_template(self, template_name: str, **kwargs) -> None:
        # Reading xsrf_token is what sets the _xsrf cookie; check_xsrf_cookie()
        # compares that cookie against the copy embedded in the page below.
        self.write(
            env.get_template(template_name).render(
                xsrf_token=self.xsrf_token.decode('ascii'), **kwargs
            )
        )

    def get_url_args(self):
        return {
            't': self.get_task_arg(), 'm': ','.join(self.get_models_arg()),
            'q': self.get_query_arg(), 'p_sz': str(self.get_page_sz_arg()),
            'p_no': str(self.get_page_no_arg()),
            's': str(self.get_sorting_arg()),
            's_metric': self.get_sorting_metric_arg(),
        }

    def get_task_arg(self) -> str:
        task = self.get_query_argument('t', '')
        if not task:
            raise web.HTTPError(400, 'Task parameter is required')
        return validate_path_component(task, 'task')

    def get_models_arg(self) -> List[str]:
        models = self.get_query_argument('m', '')
        if not models:
            return []
        model_list = models.split(',')
        return [validate_path_component(m, 'model') for m in model_list]

    def get_page_sz_arg(self) -> int:
        p_sz = self.get_query_argument('p_sz', '')
        if len(p_sz) == 0:
            return DEFAULT_PAGE_SIZE
        try:
            value = int(p_sz)
            if value <= 0:
                raise web.HTTPError(400, 'Page size must be a positive integer')
            if value > MAX_PAGE_SZ:
                raise web.HTTPError(
                    400, f'Page size must not exceed {MAX_PAGE_SZ}'
                )
            return value
        except ValueError:
            raise web.HTTPError(400, f'Invalid page size: {p_sz!r} is not a valid integer')

    def get_page_no_arg(self) -> int:
        p_no = self.get_query_argument('p_no', '')
        if len(p_no) == 0:
            return DEFAULT_PAGE_NO
        try:
            value = int(p_no)
            if value <= 0:
                raise web.HTTPError(400, 'Page number must be a positive integer')
            return value
        except ValueError:
            raise web.HTTPError(400, f'Invalid page number: {p_no!r} is not a valid integer')

    def get_query_arg(self) -> str:
        return self.get_query_argument('q', '')

    def get_sorting_arg(self) -> int:
        sorting = self.get_query_argument('s', '')
        if len(sorting) == 0:
            return 0
        try:
            value = int(sorting)
            valid_values = {sorting_type.value for sorting_type in VizSeqSortingType}
            if value not in valid_values:
                raise web.HTTPError(
                    400, f'Sorting value must be one of {sorted(valid_values)}'
                )
            return value
        except ValueError:
            raise web.HTTPError(400, f'Invalid sorting value: {sorting!r} is not a valid integer')

    def get_sorting_metric_arg(self) -> str:
        metric = self.get_query_argument('s_metric', '')
        if self.get_sorting_arg() == VizSeqSortingType.metric.value:
            if metric not in get_scorer_ids():
                raise web.HTTPError(400, f'Invalid sorting metric: {metric!r}')
        return metric


class TaskListHandler(VizSeqBaseRequestHandler):
    def get(self):
        enum_tasks_and_names_and_enum_models = \
            VizSeqWebView.get_enum_tasks_and_names_and_enum_models(args.data_root)
        self.render_template(
            'tasks.html',
            enum_tasks_and_names_and_enum_models=enum_tasks_and_names_and_enum_models
        )


class ViewHandler(VizSeqBaseRequestHandler):
    def get(self):
        url_args = self.get_url_args()
        models = self.get_models_arg()
        task = self.get_task_arg()
        page_sz, page_no = self.get_page_sz_arg(), self.get_page_no_arg()
        query = self.get_query_arg()
        sorting = self.get_sorting_arg()
        s_metric = self.get_sorting_metric_arg()
        wv = VizSeqWebView(
            args.data_root, task, models=models, page_sz=page_sz,
            page_no=page_no, query=query, sorting=sorting,
            sorting_metric=s_metric
        )
        pd = wv.get_page_data()
        page_no = min(page_no, max(1, math.ceil(pd.n_samples / page_sz)))
        url_args['p_no'] = str(page_no)
        all_tags = wv.get_tags()
        page_tags = [
            all_tags[i] if i < len(all_tags) else [] for i in pd.cur_idx
        ]
        self.render_template(
            'view.html',
            url_args=url_args, task=task, models=models, page_sz=page_sz,
            page_no=page_no, sorting=sorting, query=query, metrics=wv.metrics,
            src_has_text=wv.src_has_text, task_name=wv.task_name,
            enum_src_names_and_types=wv.enum_src_names_and_types,
            enum_ref_names=wv.enum_ref_names, trg_lang=pd.trg_lang,
            span_highlight_js=SPAN_HIGHTLIGHT_JS, page_sizes=wv.page_sizes,
            enum_metrics_and_names=wv.get_enum_metrics_and_names(),
            tag_set=wv.get_tag_set(), tags=page_tags,
            auto_tags=[[e] for e in pd.trg_lang],
            all_metrics_and_names=wv.all_metrics_and_names, s_metric=s_metric,
            pagination=wv.get_pagination(pd.n_samples, page_sz, page_no),
            cur_idx=pd.cur_idx, viz_src=pd.viz_src, src=pd.cur_src,
            ref=pd.viz_ref, hypo=pd.viz_hypo, n_samples=pd.n_samples,
            cur_sent_scores=pd.viz_sent_scores, description=wv.description,
            tokenization=wv.tokenization, all_tokenization=wv.all_tokenization,
            total_examples=pd.total_examples, n_cur_samples=pd.n_cur_samples
        )


class PageDataHandler(VizSeqBaseRequestHandler):
    def get(self):
        wv = VizSeqWebView(
            args.data_root, self.get_task_arg(), models=self.get_models_arg(),
            page_sz=self.get_page_sz_arg(), page_no=self.get_page_no_arg(),
            query=self.get_query_arg(), sorting=self.get_sorting_arg(),
            sorting_metric=self.get_sorting_metric_arg()
        )
        page_data_json = wv.get_page_data_with_pagination()
        self.write_json(page_data_json)


class TaskCfgHandler(VizSeqBaseRequestHandler):
    def post(self):
        task = self.get_task_arg()
        cfg = VizSeqWebView(args.data_root, task).cfg
        task_name = self.get_query_argument('n', task)
        cfg.set_task_name(task_name)
        description = self.get_query_argument('d', '')
        cfg.set_description(description)
        cfg_metrics = self.get_query_argument('m', '')
        cfg_metrics = cfg_metrics.split(',') if len(cfg_metrics) > 0 else []
        cfg.set_metrics(cfg_metrics)
        tokenization = self.get_query_argument('tkn', '')
        cfg.set_tokenization(tokenization)
        self.finish(f'Task "{task}" Config updated.')


class UploadHandler(VizSeqBaseRequestHandler):
    def get(self):
        self.render_template('upload.html')

    def post(self):
        files = self.request.files.get('file1', [])
        if not files:
            raise web.HTTPError(400, 'A ZIP file is required')
        file1 = files[0]
        filename = sanitize_filename(file1['filename'])
        zip_file_path = os.path.join(args.data_root, filename)
        with open(zip_file_path, 'wb') as f:
            f.write(file1['body'])
        try:
            VizSeqZipFile.unzip(
                args.data_root, filename, remove_after_unpacking=True
            )
        except (ZipExtractionError, zipfile.BadZipFile) as e:
            # Clean up the uploaded file if extraction fails
            if os.path.exists(zip_file_path):
                os.remove(zip_file_path)
            raise web.HTTPError(400, str(e))
        self.redirect('/', status=303)


class ConfigHandler(VizSeqBaseRequestHandler):
    def get(self):
        self.render_template(
            'config.html',
            g_cred_path=VizSeqGlobalConfigManager().g_cred_path,
        )

    def post(self):
        g_cred_path = self.get_argument('g_cred_path', '')
        # set_g_cred_path() accepts only a readable JSON file, which keeps this
        # endpoint from doubling as a probe for arbitrary filesystem paths. It
        # also applies the credentials to this process, so /g_translate picks
        # them up without a restart.
        try:
            set_g_cred_path(g_cred_path)
        except (OSError, ValueError):
            self.write_json(json.dumps({'valid': False}))
            return
        VizSeqGlobalConfigManager().set_g_cred_path(g_cred_path)
        self.write_json(json.dumps({'valid': True}))


class GTranslateHandler(VizSeqBaseRequestHandler):
    def get(self):
        sent = self.get_query_argument('s', None)
        lang = self.get_query_argument('l', None)
        if sent is None or lang is None:
            raise web.HTTPError(400, 'Missing required parameters: s (sentence) and l (language)')
        translation = VizSeqJson.dumps(
            {'translation': get_g_translate(sent, lang)}
        )
        self.write_json(translation)


class StatsHandler(VizSeqBaseRequestHandler):
    def get(self):
        task = self.get_task_arg()
        response = VizSeqWebView(args.data_root, task).get_stats()
        self.write_json(response)


class ScoresHandler(VizSeqBaseRequestHandler):
    def get(self):
        response = VizSeqWebView(
            args.data_root, self.get_task_arg(), self.get_models_arg()
        ).get_scores()
        self.write_json(response)


class NGramsHandler(VizSeqBaseRequestHandler):
    def get(self):
        task = self.get_task_arg()
        response = VizSeqWebView(args.data_root, task).get_n_grams()
        self.write_json(response)


class AboutHandler(VizSeqBaseRequestHandler):
    def get(self):
        self.render_template('about.html', version=__version__)


ROUTES = [
    (r'/', TaskListHandler),
    (r'/view', ViewHandler),
    (r'/config', ConfigHandler),
    (r'/upload', UploadHandler),
    (r'/about', AboutHandler),
    (r'/g_translate', GTranslateHandler),
    (r'/stats', StatsHandler),
    (r'/scores', ScoresHandler),
    (r'/ngrams', NGramsHandler),
    (r'/page_data', PageDataHandler),
    (r'/task_cfg', TaskCfgHandler),
]


def make_app(debug=False):
    return web.Application(
        ROUTES, debug=debug,
        # /upload, /config and /task_cfg all mutate state without
        # authentication, so they must not be reachable from another origin.
        xsrf_cookies=True,
        xsrf_cookie_kwargs={'samesite': 'Strict'},
    )


def start_server(hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT, debug=False):
    app = make_app(debug=debug)
    # Bind to hostname rather than every interface: an unauthenticated upload
    # endpoint should not be exposed to the network unless asked for.
    app.listen(port, address=hostname, max_buffer_size=1024 ** 3)
    logger.info("Application Started")
    logger.info(f'You can navigate to http://{hostname}:{port}')
    ioloop.IOLoop.current().start()


def main():
    global args
    args = parse_args()
    start_server(args.hostname, args.port, args.debug)


if __name__ == '__main__':
    main()
