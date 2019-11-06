# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import os.path as op
import argparse
from typing import List

from vizseq._utils.logger import logger

from vizseq._view import VizSeqWebView, DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NO
from vizseq._data.zip_file import VizSeqZipFile
from vizseq._data import get_g_translate, VizSeqGlobalConfigManager
from vizseq._visualizers import SPAN_HIGHTLIGHT_JS
from vizseq._utils import VizSeqJson
from vizseq import __version__

from tornado import web, ioloop
from jinja2 import Environment, PackageLoader, select_autoescape

DEFAULT_HOSTNAME = 'localhost'
DEFAULT_PORT = 9001

parser = argparse.ArgumentParser()
parser.add_argument('--hostname', type=str, default=DEFAULT_HOSTNAME,
                    help='server hostname')
parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                    help='server port number')
parser.add_argument('--data-root', type=str, default='./examples/data',
                    help='root path to data')
parser.add_argument('--debug', action='store_true', help='debug mode')
args, _ = parser.parse_known_args()

env = Environment(
    loader=PackageLoader('vizseq', '_templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class VizSeqBaseRequestHandler(web.RequestHandler):
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
        assert len(task) > 0
        return task

    def get_models_arg(self) -> List[str]:
        models = self.get_query_argument('m', '')
        return models.split(',') if len(models) > 0 else []

    def get_page_sz_arg(self) -> int:
        p_sz = self.get_query_argument('p_sz', '')
        if len(p_sz) == 0:
            p_sz = str(DEFAULT_PAGE_SIZE)
        return int(p_sz)

    def get_page_no_arg(self) -> int:
        p_no = self.get_query_argument('p_no', '')
        if len(p_no) == 0:
            p_no = str(DEFAULT_PAGE_NO)
        return int(p_no)

    def get_query_arg(self) -> str:
        return self.get_query_argument('q', '')

    def get_sorting_arg(self) -> int:
        sorting = self.get_query_argument('s', '')
        if len(sorting) == 0:
            sorting = '0'
        return int(sorting)

    def get_sorting_metric_arg(self) -> str:
        return self.get_query_argument('s_metric', '')


class TaskListHandler(VizSeqBaseRequestHandler):
    def get(self):
        enum_tasks_and_names_and_enum_models = \
            VizSeqWebView.get_enum_tasks_and_names_and_enum_models(args.data_root)
        html = env.get_template('tasks.html').render(
            enum_tasks_and_names_and_enum_models=enum_tasks_and_names_and_enum_models
        )
        self.write(html)


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
        html = env.get_template('view.html').render(
            url_args=url_args, task=task, models=models, page_sz=page_sz,
            page_no=page_no, sorting=sorting, query=query, metrics=wv.metrics,
            src_has_text=wv.src_has_text, task_name=wv.task_name,
            enum_src_names_and_types=wv.enum_src_names_and_types,
            enum_ref_names=wv.enum_ref_names, trg_lang=pd.trg_lang,
            span_highlight_js=SPAN_HIGHTLIGHT_JS, page_sizes=wv.page_sizes,
            enum_metrics_and_names=wv.get_enum_metrics_and_names(),
            tag_set=wv.get_tag_set(), tags=wv.get_tags(),
            auto_tags=[[e] for e in pd.trg_lang],
            all_metrics_and_names=wv.all_metrics_and_names, s_metric=s_metric,
            pagination=wv.get_pagination(pd.total_examples, page_sz, page_no),
            cur_idx=pd.cur_idx, viz_src=pd.viz_src, src=pd.cur_src,
            ref=pd.viz_ref, hypo=pd.viz_hypo, n_samples=pd.n_samples,
            cur_sent_scores=pd.viz_sent_scores, description=wv.description,
            tokenization=wv.tokenization, all_tokenization=wv.all_tokenization,
            total_examples=pd.total_examples, n_cur_samples=pd.n_cur_samples
        )
        self.write(html)


class PageDataHandler(VizSeqBaseRequestHandler):
    def get(self):
        wv = VizSeqWebView(
            args.data_root, self.get_task_arg(), models=self.get_models_arg(),
            page_sz=self.get_page_sz_arg(), page_no=self.get_page_no_arg(),
            query=self.get_query_arg(), sorting=self.get_sorting_arg()
        )
        page_data_json = wv.get_page_data_with_pagination()
        self.write(page_data_json)


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
        html = env.get_template('upload.html').render()
        self.write(html)

    def post(self):
        file1 = self.request.files['file1'][0]
        zip_file_path = os.path.join(args.data_root, file1['filename'])
        with open(zip_file_path, 'wb') as f:
            f.write(file1['body'])
        VizSeqZipFile.unzip(
            args.data_root, file1['filename'], remove_after_unpacking=True
        )
        self.redirect('/', status=303)


class ConfigHandler(VizSeqBaseRequestHandler):
    def get(self):
        html = env.get_template('config.html').render(
            g_cred_path=VizSeqGlobalConfigManager().g_cred_path,
        )
        self.write(html)

    def post(self):
        g_cred_path = self.get_argument('g_cred_path', '')
        valid = op.exists(g_cred_path)
        if valid:
            VizSeqGlobalConfigManager().set_g_cred_path(g_cred_path)
        import json
        self.write(json.dumps({'valid': valid}))


class GTranslateHandler(VizSeqBaseRequestHandler):
    def get(self):
        sent = self.get_query_argument('s', None)
        lang = self.get_query_argument('l', None)
        assert sent is not None and lang is not None
        translation = VizSeqJson.dumps(
            {'translation': get_g_translate(sent, lang)}
        )
        self.write(translation)


class StatsHandler(VizSeqBaseRequestHandler):
    def get(self):
        task = self.get_task_arg()
        response = VizSeqWebView(args.data_root, task).get_stats()
        self.write(response)


class ScoresHandler(VizSeqBaseRequestHandler):
    def get(self):
        response = VizSeqWebView(
            args.data_root, self.get_task_arg(), self.get_models_arg()
        ).get_scores()
        self.write(response)


class NGramsHandler(VizSeqBaseRequestHandler):
    def get(self):
        task = self.get_task_arg()
        response = VizSeqWebView(args.data_root, task).get_n_grams()
        self.write(response)


class AboutHandler(VizSeqBaseRequestHandler):
    def get(self):
        html = env.get_template('about.html').render(
            version=__version__
        )
        self.write(html)


def start_server(hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT, debug=False):
    app = web.Application([
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
    ], debug=debug)
    app.listen(port, max_buffer_size=1024 ** 3)
    logger.info("Application Started")
    print(f'You can navigate to http://{hostname}:{port}')
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    start_server(args.hostname, args.port, args.debug)
