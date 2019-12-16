---
id: scorer_example
title: Scorer Example
sidebar_label: Scorer Example
---

import useBaseUrl from '@docusaurus/useBaseUrl';

VizSeq scorers provide corpus-level, sentence-level and group-level (groups defined by the sentence tags) scores. They
are implemented with multi-processing.

Here is an example for using BLEU scorer:
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

Please see the <a href={useBaseUrl('docs/features/scorer_api')}>Scorer APIs</a> section for full references.
