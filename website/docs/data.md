---
id: data
title: Data
sidebar_label: Data
---

## Input Types
- Source:
- Reference:
- Hypothesis:
- Tags: per-example tags for example grouping. 

## Data Types
VizSeq gets data from Python variables (Jupyter Notebook only) or local files. Specifically, VizSeq web app expects data
to be organized in the following folder structure:

```
<data_root>/<task_name>/src_*.txt
<data_root>/<task_name>/src_*.zip
<data_root>/<task_name>/ref_*.txt
<data_root>/<task_name>/pred_*.txt
<data_root>/<task_name>/tag_*.txt
```

where

- `src_*.txt`: a text source, one sentence per line
- `src_*.zip`: a packed/compressed source, with one `source.txt` in it which provides either the sentences or the image/audio/video filenames
- `ref_*.txt`: a text reference, one sentence per line
- `pred_*.txt`: a text model prediction, one sentence per line
- `tag_*.txt`: optional, sentence-level tags, one sentence per line


## File Formats

#### Text
- txt
- txt in .zip

#### Image
- [.jpg](https://en.wikipedia.org/wiki/JPEG)
- [.png](https://en.wikipedia.org/wiki/Portable_Network_Graphics)
- [.gif](https://en.wikipedia.org/wiki/GIF)
- [.bmp](https://en.wikipedia.org/wiki/BMP_file_format)

#### Audio
- [.mp3](https://en.wikipedia.org/wiki/MP3)
- [.wav](https://en.wikipedia.org/wiki/WAV)

#### Video
- [.mp4](https://en.wikipedia.org/wiki/MPEG-4_Part_14)
- [.webm](https://en.wikipedia.org/wiki/WebM)
