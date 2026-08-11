---
id: g_translate
title: Google Translate Integration
sidebar_label: Google Translate Integration
---

import useBaseUrl from '@docusaurus/useBaseUrl';

Requires the <a href={useBaseUrl('docs/getting_started/installation')}>`translate` extra</a>
(`pip install "vizseq[translate]"`).

## Jupyter Notebook

Before enabling Google Translate in `view_examples()`, set the credential JSON path:

```python
vizseq.set_google_credential_path('path to google credential json file')
```

## Web App

Go to `Configuration` page and update the credential JSON path:
<p align="center">
    <img src={useBaseUrl('img/web_app_config.png')} alt="Configuration" />
</p>
