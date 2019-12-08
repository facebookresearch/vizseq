---
id: ipynb_example
title: Jupyter Notebook Example
sidebar_label: Jupyter Notebook Example
---

import useBaseUrl from '@docusaurus/useBaseUrl';

## Example Data
To get the data for the following examples:
```bash
$ git clone https://github.com/facebookresearch/vizseq
$ cd vizseq
$ bash get_example_data.sh
```
The data will be available in `examples/data`.

## Data Sources
VizSeq accepts data from various types of sources: plain text file paths, ZIP file paths and Python dictionaries.
(See also the [data inputs](../features/data) section for more details.)

Here is an example for plain text file paths as inputs:
```python
from glob import glob
root = 'examples/data/translation_wmt14_en_de_test'
src, ref, hypo = glob(f'{root}/src_*.txt'), glob(f'{root}/ref_*.txt'), glob(f'{root}/pred_*.txt')
```
An example for Python dictionaries as inputs:
```python
from typing import List, Dict
import os.path as op
from glob import glob

def reader(paths: List[str]) -> Dict[str, List[str]]:
    data = {}
    for path in paths:
        name = str(op.splitext(op.basename(path))[0]).split('_', 1)[1]
        with open(path) as f:
            data[name] = [l.strip() for l in f]
    return data

root = 'examples/data/translation_wmt14_en_de_test'
src = reader(glob(f'{root}/src_*.txt'))
ref = reader(glob(f'{root}/ref_*.txt'))
hypo = reader(glob(f'{root}/pred_*.txt'))
```

## Viewing Examples and Statistics 
Please see the [Jupyter Notebook APIs](features/ipynb_api) section for full references.

First, load the `vizseq` package:
```python
import vizseq
```
To view dataset statistics:
```python
%matplotlib inline
vizseq.view_stats(src, ref)
```

<p align="center"><img src={useBaseUrl('img/view_stats.png')} alt="View Statistics" /></p>

To view source-side n-grams:
```python
vizseq.view_n_grams(src)
```

<p align="center"><img src={useBaseUrl('img/view_n_grams.png')} alt="View N Grams" /></p>

To view corpus-level scores (BLEU and METEOR):
```python
vizseq.view_scores(ref, hypo, ['bleu', 'meteor'])
```

<p align="center"><img src={useBaseUrl('img/view_scores.png')} alt="View Scores" /></p>

To check the IDs of available scorers in VizSeq:
```python
vizseq.available_scorers()
```

```
Available scorers: bert_score, bleu, bp, chrf, cider, gleu, laser, meteor, nist, ribes, rouge_1, rouge_2, rouge_l, ter, wer, wer_del, wer_ins, wer_sub
```

We can view examples in pages with sorting:
```python
import vizseq.VizSeqSortingType
vizseq.view_examples(src, ref, hypo, ['bleu'], page_sz=2, page_no=12, sorting=VizSeqSortingType.src_len)
```

<p align="center"><img src={useBaseUrl('img/view_examples.png')} alt="View Examples" /></p>

## Google Translate Integration
VizSeq integrates Google Translate using Google Cloud API, to use which you need a Google Cloud credential and let VizSeq know the credential JSON file path:
```python
vizseq.set_google_credential_path('path to google credential json file')
```
Then in example viewing API, simply switch the `need_g_translate` argument on:
```python
vizseq.view_examples(src, ref, hypo, ['bleu'], need_g_translate=True)
```

## [Fairseq Integration](fairseq_example)

## More Examples
- [Multimodal Machine Translation](https://github.com/facebookresearch/vizseq/blob/master/examples/multimodal_machine_translation.ipynb)
- [Multilingual Machine Translation](https://github.com/facebookresearch/vizseq/blob/master/examples/multilingual_machine_translation.ipynb)
- [Speech Translation](https://github.com/facebookresearch/vizseq/blob/master/examples/speech_translation.ipynb)