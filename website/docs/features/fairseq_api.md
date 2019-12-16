---
id: fairseq_api
title: Fairseq Integration APIs
sidebar_label: Fairseq Integration APIs
---

import useBaseUrl from '@docusaurus/useBaseUrl';

## `vizseq.ipynb.fairseq_viz.*`
VizSeq can directly import and analyze model predictions generated
by <a href="https://github.com/pytorch/fairseq/blob/master/generate.py" target="_blank">fairseq-generate</a> or <a href="https://github.com/pytorch/fairseq/blob/master/interactive.py" target="_blank">fairseq-interactive</a> in
Jupyter Notebook. The APIs are almost the same
as <a href={useBaseUrl('docs/features/ipynb_api')}>the normal Jupyter Notebook APIs</a>.
### `view_stats()`
#### Arguments
- **`log_path`: str**: The path to `fairseq-generate` or `fairseq-interactive` log file.
### `view_scores()`
#### Arguments
- **`log_path`: str**: The path to `fairseq-generate` or `fairseq-interactive` log file.
- **`metrics`: List[str]**: List of scorer IDs. Use [`available_scorers()`](#available_scorers) to check all the
available ones.
### `view_examples()`
#### Arguments
- **`log_path`: str**: The path to `fairseq-generate` or `fairseq-interactive` log file.
- **`metrics`: Optional[List[str]] = None**: List of scorer IDs. Default to `None`. Use
[`available_scorers()`](#available_scorers) to check all the available ones.
- **`query`: str = ''**: The keyword(s) for example filtering. Default to `''`.
- **`page_sz`: int = 10**: Page size. Default to `10`.
- **`page_no`: int = 1**: Page number. Default to `1`.
- **`sorting`: VizSeqSortingType = VizSeqSortingType.original**
- **`need_g_translate`: bool = False**:
To show Google Translate results or not. Default to `False`.
- **`disable_alignment`: bool = False**:
Not to show source-reference and reference-hypothesis alignments for rendering speedup. Default to `False`.

### `view_n_grams()`
#### Arguments
- **`log_path`: str**: The path to `fairseq-generate` or `fairseq-interactive` log file.
- **`k`: int = 64**:
Number of n-grams to be shown. Default to `64`.
