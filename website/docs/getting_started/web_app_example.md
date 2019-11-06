---
id: web_app_example
title: Web App Example
sidebar_label: Web App Example
---

import useBaseUrl from '@docusaurus/useBaseUrl';

Example data is provided to test the VizSeq Web App, which can be acquired by:
```bash
$ git clone https://github.com/facebookresearch/vizseq
$ cd vizseq
$ bash get_example_data.sh
```
The data will be available in `examples/data`, including the use cases for (multimodal) machine translation,
text summarization and speech translation.

To view these examples in the web App, first launch the backend server:
```bash
$ python -m vizseq.server --port 9001 --data-root examples/data
```
And then, navigate to the following URL in your web browser:
```
http://localhost:9001
```
<p align="center"><img src={useBaseUrl('img/view_tasks.png')} alt="View Tasks" /></p>

To view your data instead, just point `--data-root` to the corresponding data root path.
