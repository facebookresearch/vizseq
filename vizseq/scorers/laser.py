# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Optional, Dict

import numpy as np

from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore

setup_flag = False


def set_up():
    global setup_flag
    if setup_flag:
        return
    try:
        import laserembeddings
        laserembeddings.Laser().embed_sentences(['This is a test.'], lang='en')
    except FileNotFoundError:
        import runpy
        import sys
        argv = [v for v in sys.argv]
        sys.argv = [sys.argv[0], 'download-models']
        runpy.run_module('laserembeddings', run_name='__main__')
        sys.argv = argv
        setup_flag = True


def _get_sent_laser(
        hypothesis: List[str], references: List[List[str]],
        extra_args: Optional[Dict[str, str]] = None
) -> List[float]:
    set_up()

    import laserembeddings
    import langid
    import logging
    logging.getLogger('langid').setLevel(logging.WARNING)
    lang = langid.classify(references[0][0])[0]

    laser = laserembeddings.Laser()
    hypo_emb = laser.embed_sentences(hypothesis, lang=lang)
    ref_emb = laser.embed_sentences(references[0], lang=lang)

    inner_product = np.sum(hypo_emb * ref_emb, axis=1)
    hypo_l2 = np.linalg.norm(hypo_emb, axis=1)
    ref_l2 = np.linalg.norm(ref_emb, axis=1)
    return (inner_product / (hypo_l2 * ref_l2)).tolist()


@register_scorer('laser', 'LASER')
class LaserScorer(VizSeqScorer):
    def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore:
        corpus_score, group_scores, sent_scores = None, None, None

        sent_scores = _get_sent_laser(hypothesis, references)

        if self.corpus_level:
            corpus_score = np.mean(sent_scores)

        if tags is not None:
            tag_set = self._unique(tags)
            group_scores = {}
            for t in tag_set:
                indices = [i for i, cur in enumerate(tags) if t in cur]
                group_scores[t] = np.mean([sent_scores[i] for i in indices])

        return VizSeqScore.make(
                corpus_score=corpus_score, sent_scores=sent_scores,
                group_scores=group_scores
            )
