---
id: metrics
title: Built-In Metrics
sidebar_label: Built-In Metrics
---

import useBaseUrl from '@docusaurus/useBaseUrl';

Here is the list of VizSeq built-in metrics. They are all accelerated with multi-processing/multi-threading.

### N-gram-based

- BLEU ([Papineni et al., 2002](https://www.aclweb.org/anthology/P02-1040)): [sacreBLEU](https://github.com/mjpost/sacreBLEU) implementation
- NIST ([Doddington, 2002](http://www.mt-archive.info/HLT-2002-Doddington.pdf)): [NLTK](https://github.com/nltk/nltk) implementation
- METEOR ([Banerjee et al., 2005](https://www.aclweb.org/anthology/W05-0909)): [NLTK](https://github.com/nltk/nltk) implementation
- TER ([Snover et al., 2006](http://mt-archive.info/AMTA-2006-Snover.pdf)): VizSeq implementation
- RIBES ([Isozaki et al., 2010](https://www.aclweb.org/anthology/D10-1092)): [NLTK](https://github.com/nltk/nltk) implementation
- chrF ([Popović et al., 2015](https://www.aclweb.org/anthology/W15-3049)): [sacreBLEU](https://github.com/mjpost/sacreBLEU) implementation
- GLEU ([Wu et al., 2016](https://arxiv.org/pdf/1609.08144.pdf)): [NLTK](https://github.com/nltk/nltk) implementation
- ROUGE ([Lin, 2004](https://www.aclweb.org/anthology/W04-1013)): [py-rouge](https://github.com/Diego999/py-rouge) implementation
- CIDEr ([Vedantam et al., 2015](https://www.cv-foundation.org/openaccess/content_cvpr_2015/papers/Vedantam_CIDEr_Consensus-Based_Image_2015_CVPR_paper.pdf)): [pycocoevalcap](https://github.com/tylin/coco-caption/tree/master/pycocoevalcap/cider) implementation
- WER ([Word Error Rate](https://en.wikipedia.org/wiki/Word_error_rate>)): VizSeq implementation




### Embedding-based


- LASER ([Artetxe and Schwenk, 2018](https://arxiv.org/pdf/1812.10464.pdf)): official [LASER](https://github.com/facebookresearch/LASER) implementation
- BERTScore ([Zhang et al., 2019](https://arxiv.org/pdf/1904.09675.pdf)): official [BERTScore](https://github.com/Tiiiger/bert_score) implementation


### User-defined Metrics
VizSeq opens the API for user-defined metrics. Refer to the <a href={useBaseUrl('docs/new_metric')}>adding new metrics</a> section
for more details.
