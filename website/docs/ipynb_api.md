---
id: ipynb_api
title: Jupyter Notebook APIs
sidebar_label: Jupyter Notebook APIs
---

## `view_stats()`
#### Arguments
##### `sources`: Union[str, List[str], Dict[str, List[str]]]
Source-side data source. Can be a path, paths or lists of sentences. Refer to [Data](data) section for more details.
##### `references`: Union[str, List[str], Dict[str, List[str]]]
Target-side data source. Can be a path, paths or lists of sentences. Refer to [Data](data) section for more details.
##### `tags`: Optional[Union[str, List[str], Dict[str, List[str]]]] = None

## available_scorers()
Show the IDs of available scorers in VizSeq.

## `view_scores()`
#### Arguments
##### `references`: Union[str, List[str], Dict[str, List[str]]]
Target-side data source. Can be a path, paths or lists of sentences. Refer to [Data](data) section for more details.
##### `hypothesis`: Optional[Union[str, List[str], Dict[str, List[str]]]] = None
Model prediction data source. Can be a path, paths or lists of sentences. Refer to [Data](data) section for more details. Default to `None`.
##### `metrics`: List[str]
##### `tags`: Optional[Union[str, List[str], Dict[str, List[str]]]] = None

## `view_examples()`
#### Arguments
##### `sources`: Union[str, List[str], Dict[str, List[str]]]
Source-side data source. Can be a path, paths or lists of sentences. Refer to [Data](data) section for more details.
##### `references`: Union[str, List[str], Dict[str, List[str]]]
Target-side data source. Can be a path, paths or lists of sentences. Refer to [Data](data) section for more details.
##### `hypothesis`: Optional[Union[str, List[str], Dict[str, List[str]]]] = None
Model prediction data source. Can be a path, paths or lists of sentences. Refer to [Data](data) section for more details. Default to `None`.
##### `metrics`: Optional[List[str]] = None
##### `query`: str = ''
##### `page_sz`: int = 10
##### `page_no`: int = 1
##### `sorting`: VizSeqSortingType = VizSeqSortingType.original
##### `need_g_translate`: bool = False
To show Google Translate results or not. Default to `False`. 

## `view_n_grams()`
#### Arguments
##### `data`: Union[str, List[str], Dict[str, List[str]]]
The data source. Can be a path, paths or lists of sentences. Refer to [Data](data) section for more details.
##### `k`: int = 64
Number of n-grams to be shown. Default to `64`.
