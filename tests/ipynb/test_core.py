# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from html.parser import HTMLParser

from . import VizSeqIpynbTestCase
from vizseq.ipynb.core import (env, view_stats, view_examples, view_n_grams,
                               view_scores)
from vizseq._visualizers import SPAN_HIGHTLIGHT_JS


class ExportAttributeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.button_targets = []
        self.export_names = []
        self.handlers = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'button':
            self.button_targets.append(attrs.get('data-vizseq-target'))
            self.handlers.append(attrs.get('onclick'))
        elif tag == 'span' and 'data-vizseq-export' in attrs:
            self.export_names.append(attrs['data-vizseq-export'])


class VizSeqIpynbCoreTestCase(VizSeqIpynbTestCase):
    @staticmethod
    def _score_template_context(metric='bleu'):
        return {
            'metrics_and_names': [[metric, 'Metric']],
            'models': ['model'],
            'tag_set': ['tag'],
            'corpus_scores': {metric: {'model': 42.0}},
            'group_scores': {metric: {'tag': {'model': 40.0}}},
            'corpus_and_group_score_latex': {metric: 'latex export'},
            'corpus_and_group_score_csv': {metric: 'csv export'},
        }

    def test_templates_do_not_load_global_stylesheets(self):
        templates = {
            'ipynb_stats.html': ({
                'stats': {
                    'n_examples': 1,
                    'n_src_tokens': {'source': 2},
                    'n_src_chars': {'source': 12},
                    'n_ref_tokens': {'reference': 2},
                    'n_ref_chars': {'reference': 15},
                },
                'enum_src_names_and_types': [[0, 'source', 'Text']],
                'enum_ref_names': [[0, 'reference']],
            }, 'Source source'),
            'ipynb_view.html': ({
                'span_highlight_js': SPAN_HIGHTLIGHT_JS,
                'cur_idx': [0],
                'n_cur_samples': 1,
                'n_samples': 1,
                'total_examples': 1,
                'enum_src_names_and_types': [[0, 'source', 'text']],
                'src': [['example source']],
                'google_translation': [],
                'enum_ref_names': [[0, 'reference']],
                'ref': [['example reference']],
                'enum_models': [[0, 'model']],
                'hypo': {'model': ['example hypothesis']},
                'enum_metrics': [],
                'sent_scores': [],
            }, 'example source'),
            'ipynb_scores.html': (
                self._score_template_context(),
                'data-vizseq-export="csv_bleu"',
            ),
            'ipynb_n_grams.html': ({
                'n': [1],
                'n_grams': {1: [('example n-gram', 1)]},
            }, 'example n-gram'),
        }

        for template_name, (context, rendered_content) in templates.items():
            with self.subTest(template=template_name):
                html = env.get_template(template_name).render(**context)
                self.assertIn('class="vizseq-output"', html)
                self.assertIn('.vizseq-output .table', html)
                self.assertIn('background-color: #fff', html)
                self.assertIn(rendered_content, html)
                self.assertNotIn('bootstrap.min.css', html)
                self.assertNotIn('<script src=', html)
                self.assertNotIn('<body', html.lower())
                self.assertNotRegex(html, r'(?m)^\s*body\s*\{')

        scores_html = env.get_template('ipynb_scores.html').render(
            **templates['ipynb_scores.html'][0]
        )
        self.assertIn("this.closest('.vizseq-output')", scores_html)
        self.assertIn('.vizseq-output .btn-sm', scores_html)
        self.assertIn('if (source)', scores_html)
        self.assertNotIn('id="csv_bleu"', scores_html)
        self.assertNotIn('<script>', scores_html)

    def test_score_export_names_are_not_interpolated_into_javascript(self):
        metric = 'o\'brien"]'
        html = env.get_template('ipynb_scores.html').render(
            **self._score_template_context(metric)
        )
        parser = ExportAttributeParser()
        parser.feed(html)

        expected = {f'csv_{metric}', f'latex_{metric}'}
        self.assertEqual(set(parser.button_targets), expected)
        self.assertEqual(set(parser.export_names), expected)
        for handler in parser.handlers:
            self.assertNotIn(metric, handler)
            self.assertIn('this.dataset.vizseqTarget', handler)

    def test_view_stats(self):
        _ = view_stats(self.source, self.references)

    def test_view_examples(self):
        _ = view_examples(self.source, self.references, self.hypothesis)

    def test_view_scores(self):
        _ = view_scores(self.references, self.hypothesis, ['bleu'])
        _ = view_scores(self.references, self.hypothesis, ['rouge_1'],
                        tags=self.tags)

    def test_view_n_grams(self):
        _ = view_n_grams(self.references)
