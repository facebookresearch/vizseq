---
id: new_metric
title: Adding New Metrics
sidebar_label: Adding New Metrics
---

VizSeq has an open API for adding user-defined metrics. And we welcome you to contribute to enriching VizSeq's collection of scorers!

To start with, first add `new_metric.py` to `vizseq/scorers`, in which a new scorer class is inherited from `VizSeqScorer` and a `score` method is defined.
And then register the new scorer class with an id and a name using `vizseq.scorers.register_scorer`:

```python
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
```

Then we need to get the new scorer class covered by tests. To achieve that, Add a unit test `test_new_metric.py` to `tests/scorers` and run:

```bash
python -m unittest tests.scorers.test_new_metric
```

