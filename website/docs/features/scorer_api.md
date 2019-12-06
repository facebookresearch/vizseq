---
id: scorer_api
title: Scorer APIs
sidebar_label: Scorer APIs
---

## Parent Class: vizseq.scorer.VizSeqScorer
All scorers are inherited from this class and implement the `score()` interface.

### Constructor
#### Arguments
- **corpus_level: bool = True**: calculating corpus-level score. Default to `True`.
- **sent_level: bool = False**: calculating sentence-level score. Default to `False`.
- **n_workers: Optional[int] = None**: the number of processes to be used. `None` for automatic configuration. Default to `None`.
- **verbose: bool = False**: printing detailed logs.
- **extra_args: Optional[Dict[str, str]] = None**: a key-value dictionary for metric-specific parameters. Default to `None`.



### score()
#### Arguments
- **hypothesis: List[str]**: The model predictions.
- **references: List[List[str]]**: The references. Inner list #1 for the 1st set of references, #2 for the 2nd set of references, and so on. (See also the [example](../getting_started/scorer_example).) 
- **tags: Optional[List[List[str]]] = None**: The sentence tags. Inner list #1 for the 1st set of tags, #2 for the 2nd set of tags, and so on. Default to `None`.

#### Returns
- **score: vizseq.scorers.VizSeqScore**: `VizSeqScore` is a namedtuple, whose definition is as follows:
```python
class VizSeqScore(NamedTuple):
    corpus_score: Optional[float] = None
    sent_scores: Optional[List[float]] = None
    group_scores: Optional[Dict[str, float]] = None
```
