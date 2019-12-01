---
id: scorer_example
title: Scorer Example
sidebar_label: Scorer Example
---

VizSeq scorers provide corpus-level, sentence-level and group-level (defined by sentence tags) scores. They are
implemented with multiprocessing.

Here is an example for BLEU:
```python
from vizseq.scorers.bleu import BLEUScorer

scorer = BLEUScorer(corpus_level=True, sent_level=True, n_workers=2, verbose=False, extra_args=None)

ref = [['This is a sample #1 reference.', 'This is a sample #2 reference.']]
hypo = ['This is a sample #1 prediction.', 'This is a sample #2 model prediction.']
tags = [['Test Group 1', 'Test Group 2']]

scores = scorer.score(hypo, ref, tags=tags)

print(f'Corpus-level BLEU: {scores.corpus_score}')
print(f'Sentence-level BLEU: {scores.sent_scores}')
print(f'Group BLEU: {scores.group_scores}')
```

```
Corpus-level BLEU: 67.945
Sentence-level BLEU: [75.984, 61.479]
Group BLEU: {'Test Group 2': 75.984, 'Test Group 1': 75.984}
```
