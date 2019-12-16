---
id: fairseq_example
title: Fairseq Integration
sidebar_label: Fairseq Integration
---

import useBaseUrl from '@docusaurus/useBaseUrl';

<a href="https://github.com/pytorch/fairseq" target="_blank">Fairseq</a> is a popular sequence modeling toolkit
developed by Facebook AI Research. VizSeq can directly import and analyze model predictions generated
by <a href="https://github.com/pytorch/fairseq/blob/master/generate.py" target="_blank">fairseq-generate</a> or <a href="https://github.com/pytorch/fairseq/blob/master/interactive.py" target="_blank">fairseq-interactive</a> in
Jupyter Notebook. <a href={useBaseUrl('docs/features/fairseq_api')}>The APIs</a> are almost the same
as <a href={useBaseUrl('docs/getting_started/ipynb_example')}>the normal Jupyter Notebook APIs</a>:

```python
from vizseq.ipynb import fairseq_viz as vizseq_fs

log_path = 'examples/data/wmt14_fr_en_test.fairseq_generate.log'

vizseq_fs.view_stats(log_path)
vizseq_fs.view_examples(log_path, ['bleu', 'meteor'], need_g_translate=True)
vizseq_fs.view_scores(log_path, ['bleu', 'meteor'])
vizseq_fs.view_n_grams(log_path)
```

<p align="center"><img src={useBaseUrl('img/fairseq_view_examples.png')} alt="Fairseq View" /></p>
