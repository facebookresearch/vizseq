Data Sources
============

VizSeq gets data from Python variables (Jupyter Notebook only) or local files. Specifically, VizSeq web app expects data
to be organized in the following folder structure::

    <data_root>/<task_or_dataset_name>/src_*.txt
    <data_root>/<task_or_dataset_name>/src_*.zip
    <data_root>/<task_or_dataset_name>/ref_*.txt
    <data_root>/<task_or_dataset_name>/pred_*.txt
    <data_root>/<task_or_dataset_name>/tag_*.txt

where

- ``src_*.txt``: a text source, one sentence per line
- ``src_*.zip``: a packed/compressed source, with one ``source.txt`` in it which provides either the sentences or the image/audio/video filenames
- ``ref_*.txt``: a text reference, one sentence per line
- ``pred_*.txt``: a text model prediction, one sentence per line
- ``tag_*.txt``: optional, sentence-level tags, one sentence per line


Supported File Formats
----------------------

Zip File
^^^^^^^^
- zip

Image
^^^^^^^^
- jpg
- png
- gif
- bmp

Audio
^^^^^^^^
- mp3
- wav

Video
^^^^^^^^
- mp4
- webm
