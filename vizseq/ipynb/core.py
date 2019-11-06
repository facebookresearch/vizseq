# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Optional

from jinja2 import Environment, PackageLoader, select_autoescape
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display

from vizseq._data import (VizSeqDataSources, PathOrPathsOrDictOfStrList,
                          VizSeqNGrams, VizSeqStats, get_g_translate,
                          set_g_cred_path as _set_g_cred_path)
from vizseq._visualizers import SPAN_HIGHTLIGHT_JS
from vizseq._view import (VizSeqDataPageView, VizSeqWebView, VizSeqSortingType,
                          DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NO)
from vizseq.scorers import get_scorer_ids, get_scorer, get_scorer_name
from vizseq._utils.logger import logger


env = Environment(
    loader=PackageLoader('vizseq', '_templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


# TODO: show id with name
def available_scorers():
    print('Available scorers: {}'.format(', '.join(sorted(get_scorer_ids()))))


def view_examples(
        sources: PathOrPathsOrDictOfStrList,
        references: PathOrPathsOrDictOfStrList,
        hypothesis: Optional[PathOrPathsOrDictOfStrList] = None,
        metrics: Optional[List[str]] = None,
        query: str = '',
        page_sz: int = DEFAULT_PAGE_SIZE,
        page_no: int = DEFAULT_PAGE_NO,
        sorting: VizSeqSortingType = VizSeqSortingType.original,
        need_g_translate: bool = False
):
    _src = VizSeqDataSources(sources)
    _ref = VizSeqDataSources(references)
    _hypo = VizSeqDataSources(hypothesis)
    if _hypo.n_sources == 0:
        metrics = None
    assert len(_src) == len(_ref)
    assert _hypo.n_sources == 0 or len(_ref) == len(_hypo)

    _need_g_translate = need_g_translate and _src.has_text
    view = VizSeqDataPageView.get(
        _src, _ref, _hypo, page_sz, page_no, metrics=metrics, query=query,
        sorting=sorting.value, need_lang_tags=_need_g_translate
    )

    google_translation = []
    if _need_g_translate:
        for i, s in enumerate(view.cur_src_text):
            google_translation.append(get_g_translate(s, view.trg_lang[i]))

    html = env.get_template('ipynb_view.html').render(
        enum_metrics=VizSeqDataPageView.get_enum(metrics),
        enum_models=VizSeqDataPageView.get_enum(_hypo.text_names),
        cur_idx=view.cur_idx, src=view.viz_src, ref=view.viz_ref,
        hypo=view.viz_hypo,
        enum_src_names_and_types=VizSeqDataPageView.get_enum(
            zip(_src.names, [t.name for t in _src.data_types])
        ),
        enum_ref_names=list(enumerate(_ref.names)),
        sent_scores=view.viz_sent_scores,
        google_translation=google_translation,
        span_highlight_js=SPAN_HIGHTLIGHT_JS,
        total_examples=view.total_examples,
        n_samples=view.n_samples,
        n_cur_samples=view.n_cur_samples,
    )
    return HTML(html)


def view_n_grams(data: PathOrPathsOrDictOfStrList, k: int = 64):
    _data = VizSeqDataSources(data, text_merged=True)
    n_grams = VizSeqNGrams.extract(_data, k=k)
    html = env.get_template('ipynb_n_grams.html').render(
        n=list(n_grams.keys()),
        n_grams=n_grams
    )
    return HTML(html)


# TODO: add tag count
def view_stats(
        sources: PathOrPathsOrDictOfStrList,
        references: PathOrPathsOrDictOfStrList,
        tags: Optional[PathOrPathsOrDictOfStrList] = None,
):
    _src = VizSeqDataSources(sources, text_merged=True)
    _ref = VizSeqDataSources(references, text_merged=True)
    _tags = None if tags is None else VizSeqDataSources(tags, text_merged=True)
    stats = VizSeqStats.get(_src, _ref, _tags)

    html = env.get_template('ipynb_stats.html').render(
        stats=stats.to_dict(formatting=True),
        enum_src_names_and_types=VizSeqDataPageView.get_enum(
            zip(_src.names, [t.name.title() for t in _src.data_types]
        )),
        enum_ref_names=VizSeqDataPageView.get_enum(_ref.names)
    )
    display(HTML(html))

    n_src_plots = len(_src.text_indices)
    n_plots = n_src_plots + _ref.n_sources
    fig, ax = plt.subplots(nrows=1, ncols=n_plots, figsize=(7 * n_plots, 5))
    for i, idx in enumerate(_src.text_indices):
        cur_ax = ax if n_plots == 1 else ax[i]
        name = _src.names[idx]
        cur_sent_lens = stats.src_lens[name]
        _ = cur_ax.hist(cur_sent_lens, density=True, bins=25)
        _ = cur_ax.axvline(x=np.mean(cur_sent_lens), color='red', linewidth=3)
        cur_ax.set_title(f'Source {name} Length')
    for i, idx in enumerate(_ref.text_indices):
        cur_ax = ax if n_plots == 1 else ax[n_src_plots + i]
        name = _ref.names[idx]
        cur_sent_lens = stats.ref_lens[name]
        _ = cur_ax.hist(cur_sent_lens, density=True, bins=25)
        _ = cur_ax.axvline(x=np.mean(cur_sent_lens), color='red', linewidth=3)
        cur_ax.set_title(f'Reference {name} Length')
    plt.show()


# TODO: display one by one instead of all together
# TODO: add visualization
# TODO: add sentence scores distribution
def view_scores(
        references: PathOrPathsOrDictOfStrList,
        hypothesis: Optional[PathOrPathsOrDictOfStrList],
        metrics: List[str],
        tags: Optional[PathOrPathsOrDictOfStrList] = None
):
    _ref = VizSeqDataSources(references)
    _hypo = VizSeqDataSources(hypothesis)
    _tags, tag_set = None, []
    if tags is not None:
        _tags = VizSeqDataSources(tags, text_merged=True)
        tag_set = sorted(_tags.unique())
        _tags = _tags.text
    models = _hypo.names
    all_metrics = get_scorer_ids()
    _metrics = []
    for s in metrics:
        if s in all_metrics:
            _metrics.append(s)
        else:
            logger.warn(f'"{s}" is not a valid metric.')

    scores = {
        s: {
            m: get_scorer(s)(corpus_level=True, sent_level=False).score(
                _hypo.data[i].text, _ref.text, tags=_tags
            ) for i, m in enumerate(models)
        } for s in _metrics
    }

    corpus_scores = {
        s: {m: scores[s][m].corpus_score for m in models} for s in _metrics
    }
    group_scores = {
        s: {
            t: {
                m: scores[s][m].group_scores[t] for m in models
            } for t in tag_set
        } for s in _metrics
    }

    metrics_and_names = [[s, get_scorer_name(s)] for s in _metrics]
    html = env.get_template('ipynb_scores.html').render(
        metrics_and_names=metrics_and_names, models=models, tag_set=tag_set,
        corpus_scores=corpus_scores, group_scores=group_scores,
        corpus_and_group_score_latex=VizSeqWebView.latex_corpus_group_scores(
            corpus_scores, group_scores
        ),
        corpus_and_group_score_csv=VizSeqWebView.csv_corpus_group_scores(
            corpus_scores, group_scores
        ),
    )
    return HTML(html)


def set_google_credential_path(path: str) -> None:
    _set_g_cred_path(path)
