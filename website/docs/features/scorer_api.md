---
id: scorer_api
title: Scorer APIs
sidebar_label: Scorer APIs
---

## vizseq.scorer.VizSeqScorer

```python
def __init__(
            self, corpus_level: bool = True, sent_level: bool = False,
            n_workers: Optional[int] = None, verbose: bool = False,
            extra_args: Optional[Dict[str, str]] = None
    )

```


```python

def score(
            self, hypothesis: List[str], references: List[List[str]],
            tags: Optional[List[List[str]]] = None
    ) -> VizSeqScore
```
