Scorers
=======

N-gram-based metrics
--------------------

- BLEU (`Papineni et al., 2002 <https://www.aclweb.org/anthology/P02-1040>`__): `sacreBLEU <https://github.com/mjpost/sacreBLEU>`__ implementation
- NIST (`Doddington, 2002 <http://www.mt-archive.info/HLT-2002-Doddington.pdf>`__): `NLTK <https://github.com/nltk/nltk>`__ implementation
- METEOR (`Banerjee et al., 2005 <https://www.aclweb.org/anthology/W05-0909>`__): `NLTK <https://github.com/nltk/nltk>`__ implementation
- TER (`Snover et al., 2006 <http://mt-archive.info/AMTA-2006-Snover.pdf>`__)
- RIBES (`Isozaki et al., 2010 <https://www.aclweb.org/anthology/D10-1092>`__): `NLTK <https://github.com/nltk/nltk>`__ implementation
- chrF (`Popović et al., 2015 <https://www.aclweb.org/anthology/W15-3049>`__): `sacreBLEU <https://github.com/mjpost/sacreBLEU>`__ implementation
- GLEU (`Wu et al., 2016 <https://arxiv.org/pdf/1609.08144.pdf>`__): `NLTK <https://github.com/nltk/nltk>`__ implementation
- ROUGE (`Lin, 2004 <https://www.aclweb.org/anthology/W04-1013>`__): `py-rouge <https://github.com/Diego999/py-rouge>`__ implementation
- CIDEr (`Vedantam et al., 2015 <https://www.cv-foundation.org/openaccess/content_cvpr_2015/papers/Vedantam_CIDEr_Consensus-Based_Image_2015_CVPR_paper.pdf>`__): `pycocoevalcap <https://github.com/tylin/coco-caption/tree/master/pycocoevalcap/cider>`__ implementation
- WER (`Word Error Rate <https://en.wikipedia.org/wiki/Word_error_rate>`__)




Embedding-based metrics
-----------------------

- LASER (`Artetxe and Schwenk, 2018 <https://arxiv.org/pdf/1812.10464.pdf>`__): official `LASER <https://github.com/facebookresearch/LASER>`__ implementation
- BERTScore (`Zhang et al., 2019 <https://arxiv.org/pdf/1904.09675.pdf>`__): official `BERTScore <https://github.com/Tiiiger/bert_score>`__ implementation



Adding user-defined metric
--------------------------

First, add ``<new_metric>.py`` file to ``vizseq/scorers``, and then register the scoring function::

    from typing import Optional, List

    from vizseq.scorers import register_scorer, VizSeqScorer, VizSeqScore

    @register_scorer('new_metric_id', 'New Metric Name')
    class NewMetricScorer(VizSeqScorer):
        def score(
                self, hypothesis: List[str], references: List[List[str]],
                tags: Optional[List[List[str]]] = None
        ) -> VizSeqScore:
            # calculate the number of workers by number of examples
            self._update_n_workers(len(hypothesis))

            corpus_score, group_scores, sent_scores = None, None, None

            if self.corpus_level:
                # implement corpus-level score
                corpus_score = 99.9
            if self.sent_level:
                # implement sentence-level score
                sent_scores=[99.9, 99.9]
            if tags is not None:
                tag_set = self._unique(tags)
                # implement group-level (by sentence tags) score
                group_scores={t: 99.9 for t in tag_set}

            return VizSeqScore.make(
                corpus_score=corpus_score, sent_scores=sent_scores,
                group_scores=group_scores
            )

Add a unit test to ``tests/scorers/test_new_metric.py`` and run::

    python -m unittest tests.scorers.test_new_metric
