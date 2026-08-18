---
id: installation
title: Installation
sidebar_label: Installation
---

import useBaseUrl from '@docusaurus/useBaseUrl';

VizSeq requires **Python 3.11+** and currently runs on **Unix/Linux** and **macOS/OS X**. It will support **Windows** as
well in the future.

You can install VizSeq from PyPI repository:
```bash
$ pip install vizseq
```
Or install it from source:
```bash
$ git clone https://github.com/facebookresearch/vizseq
$ cd vizseq
$ pip install -e .
```

## Optional Dependencies
The base install keeps the dependency footprint small. It covers all
the <a href={useBaseUrl('docs/features/metrics')}>n-gram-based metrics</a>, both the Jupyter Notebook and Web App
interfaces, and the Fairseq integration. Heavier features live behind extras:

| Extra | Install | Enables |
| :--- | :--- | :--- |
| `embeddings` | `pip install "vizseq[embeddings]"` | Embedding-based metrics: LASER and BERTScore (pulls in PyTorch and Transformers) |
| `audio` | `pip install "vizseq[audio]"` | Audio sources for speech recognition and speech translation tasks |
| `translate` | `pip install "vizseq[translate]"` | <a href={useBaseUrl('docs/features/g_translate')}>Google Translate integration</a> |
| `all` | `pip install "vizseq[all]"` | All of the above |

Extras can be combined, and they work with source installs too:
```bash
$ pip install "vizseq[embeddings,audio]"
$ pip install -e ".[all]"
```

`vizseq.available_scorers()` lists every built-in scorer regardless of which extras are installed.
Scorers that need an extra raise an `ImportError` naming the extra when you actually use them, so
`bert_score` and `laser` are listed even without the `embeddings` extra.

## Citation
If you find VizSeq useful in your research, please cite as
```bibtex
@inproceedings{wang2019vizseq,
  title = {VizSeq: A Visual Analysis Toolkit for Text Generation Tasks},
  author = {Wang, Changhan and Jain, Anirudh and Chen, Danlu and Gu, Jiatao},
  booktitle = {In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing: System Demonstrations},
  year = {2019},
}
```
