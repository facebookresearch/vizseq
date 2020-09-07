---
id: data
title: Data Inputs
sidebar_label: Data Inputs
---

## Input Types
- Sources: Source-side inputs for text generation tasks.
- References: Target-side references for text generation tasks.
- Hypothesis: Model predictions. One sentence per example per model.
- Tags: Per-example tags for example grouping. 

## Data Sources
VizSeq accepts data inputs in various ways.
### Python Variables
VizSeq Jupyter notebook interface accepts Python list of lists of strings as inputs. The inner list is for multiple
inputs of the same type, for example:
```python
ref_1 = ['This is ref #1 for example #1.', 'This is ref #1 for example #2.']
ref_2 = ['This is ref #2 for example #1.', 'This is ref #2 for example #2.']
ref_3 = ['This is ref #3 for example #1.', 'This is ref #3 for example #2.']
references = [ref_1, ref_2, ref_3]
```
### Plain text or ZIP file paths

VizSeq also accepts file paths. For example for Jupyter notebook:
```python
references = ['ref_1.txt', 'ref_2.txt', 'ref_3.txt']
```
 
For the web App interface, it expects data to be organized in the following folder structure:

```
[data_root]/[task_name]/src_*.txt
[data_root]/[task_name]/src_*.zip
[data_root]/[task_name]/ref_*.txt
[data_root]/[task_name]/pred_*.txt
[data_root]/[task_name]/tag_*.txt
```

where

- `src_*.txt`: A text source, one sentence per line.
- `src_*.zip`: A packed source, with a `source.txt` in it, which provides either the sentences or the image/audio/video
filenames per line.
- `ref_*.txt`: A text reference, one sentence per line.
- `pred_*.txt`: A text model prediction, one sentence per line.
- `tag_*.txt`: (Optional) Example tags, one phrase per line.


## File Formats

#### Text
- .txt
- .txt in .zip

#### Image (packed in .zip)
- [.jpg](https://en.wikipedia.org/wiki/JPEG)
- [.png](https://en.wikipedia.org/wiki/Portable_Network_Graphics)
- [.gif](https://en.wikipedia.org/wiki/GIF)
- [.bmp](https://en.wikipedia.org/wiki/BMP_file_format)

#### Audio (packed in .zip)
- [.mp3](https://en.wikipedia.org/wiki/MP3)
- [.wav](https://en.wikipedia.org/wiki/WAV)

#### Video (packed in .zip)
- [.mp4](https://en.wikipedia.org/wiki/MPEG-4_Part_14)
- [.webm](https://en.wikipedia.org/wiki/WebM)
