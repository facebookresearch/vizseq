---
id: overview
title: Overview
sidebar_label: Overview
---

import useBaseUrl from '@docusaurus/useBaseUrl';

VizSeq is a visual analysis toolkit for text generation tasks like machine translation, summarization, image captioning,
speech translation and video description. 

It takes multi-modal sources, text references as well as text model predictions as inputs, and analyzes them visually
in [Jupyter Notebook](ipynb) or in a built-in [Web App](web_app). It also provides a collection of multi-process scorers as a normal
Python package.



<p align="center">
  <img src={useBaseUrl('img/overview.png')} alt="VizSeq Overview" width="480" class="center" />
</p>

Please also check out our [EMNLP paper](https://arxiv.org/pdf/1909.05424.pdf) for more details.

#### Example Tasks
The source modality can be text, image, audio, video or any combination of them. This covers a wide range of text
generation tasks, examples of which are listed below:

| Source | Example Tasks |
| :--- | :--- |
| Text | Machine translation, text summarization, dialog generation, grammatical error correction, open-domain question answering |
| Image | Image captioning, image question answering, optical character recognition                                                |
| Audio | Speech recognition, speech translation                                                                                   |
| Video | Video description                                                                                                        |
| Multimodal | Multimodal machine translation

#### Built-in metrics

| Type | Metrics |
| :--- | :--- |
| N-gram-based * | BLEU ([Papineni et al., 2002](https://www.aclweb.org/anthology/P02-1040)), NIST ([Doddington, 2002](http://www.mt-archive.info/HLT-2002-Doddington.pdf)), METEOR ([Banerjee et al., 2005](https://www.aclweb.org/anthology/W05-0909)), TER ([Snover et al., 2006](http://mt-archive.info/AMTA-2006-Snover.pdf)), RIBES ([Isozaki et al., 2010](https://www.aclweb.org/anthology/D10-1092)), chrF ([Popović et al., 2015](https://www.aclweb.org/anthology/W15-3049)), GLEU ([Wu et al., 2016](https://arxiv.org/pdf/1609.08144.pdf)), ROUGE ([Lin, 2004](https://www.aclweb.org/anthology/W04-1013)), CIDEr ([Vedantam et al., 2015](https://www.cv-foundation.org/openaccess/content_cvpr_2015/papers/Vedantam_CIDEr_Consensus-Based_Image_2015_CVPR_paper.pdf)), WER |
| Embedding-based | LASER ([Artetxe and Schwenk, 2018](https://arxiv.org/pdf/1812.10464.pdf)), BERTScore ([Zhang et al., 2019](https://arxiv.org/pdf/1904.09675.pdf)) |
\* **with multi-process acceleration**