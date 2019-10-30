# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import Dict, List

from jinja2 import Markup

from vizseq._aligners import VizseqSrcRefTextAligner, VizseqRefHypoTextAligner

SPAN_HIGHTLIGHT_JS = Markup('''
<script>
    function highlight_span(spanNode, trgSpanId) {
        trgSpanNode = document.getElementById(trgSpanId);
        trgSpanNode.style.backgroundColor = '#D6EAF8';
        spanNode.style.backgroundColor = '#D6EAF8';
    }
    function dehighlight_span(spanNode, trgSpanId) {
        trgSpanNode = document.getElementById(trgSpanId);
        trgSpanNode.style.backgroundColor = trgSpanNode.parentNode.style.backgroundColor;
        spanNode.style.backgroundColor = spanNode.parentNode.style.backgroundColor;
    }
</script>
''')


class VizSeqSrcVisualizer(object):
    @classmethod
    def _visualize_sent(cls, sent: str, data_id: int, example_id: int):
        spans = [
            f'<span id="src_{data_id}_{example_id}_{k}">{t}</span>'
            for k, t in enumerate(sent.split())
        ]
        return Markup(' '.join(spans))

    @classmethod
    def visualize(
            cls, src: List[List[str]], text_data_ids: List[int]
    ) -> List[List[str]]:
        if len(text_data_ids) == 0:
            return src
        visualized = []
        for i, s in enumerate(src):
            if i in text_data_ids:
                visualized.append([
                    cls._visualize_sent(ss, i, j) for j, ss in enumerate(s)
                ])
            else:
                visualized.append([ss for ss in s])
        return visualized


class VizSeqRefVisualizer(object):
    @classmethod
    def visualize(
            cls, src: List[str], ref: List[List[str]], src_idx: int
    ) -> List[List[str]]:
        src_ref = [src] + ref
        rendered = [[] for _ in range(len(ref))]
        for i, (s, *r_list) in enumerate(zip(*src_ref)):
            src_tokens = s.split()
            ref_tokens = {str(ii): r.split() for ii, r in enumerate(r_list)}
            alignments = VizseqSrcRefTextAligner.align(src_tokens, ref_tokens)
            visualized = VizseqSrcRefTextAligner.to_span_html(
                ref_tokens, alignments, 'ref', i, f'src_{src_idx}'
            )
            for ii in range(len(r_list)):
                sent_markup = Markup(' '.join(visualized[str(ii)]))
                rendered[ii].append(sent_markup)
        return rendered


class VizSeqHypoVisualizer(object):
    @classmethod
    def visualize(
            cls, ref: List[str], hypo: Dict[str, List[str]], ref_idx: int
    ) -> Dict[str, List[str]]:
        hypo_ids = sorted(hypo.keys())
        rendered = {k: [] for k in hypo_ids}
        for i, r in enumerate(ref):
            ref_tokens = r.split()
            hypo_tokens = {h_id: hypo[h_id][i].split() for h_id in hypo_ids}
            alignments = VizseqRefHypoTextAligner.align(ref_tokens, hypo_tokens)
            visualized = VizseqRefHypoTextAligner.to_span_html(
                hypo_tokens, alignments, 'hypo', i, f'ref_{ref_idx}'
            )
            for h_id in hypo_ids:
                sent_markup = Markup(' '.join(visualized[h_id]))
                rendered[h_id].append(sent_markup)
        return rendered
