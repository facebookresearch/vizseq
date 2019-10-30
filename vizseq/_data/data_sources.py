# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


import os
import os.path as op
import zipfile
from typing import List, Dict, Union, Optional, Tuple, Set
from collections import Counter
from enum import Enum
import base64

import numpy as np
import soundfile as sf

TXT_EXT = '.txt'
ZIP_EXT = '.zip'

PathOrPathsOrDictOfStrList = Union[str, List[str], Dict[str, List[str]]]


class VizSeqDataType(Enum):
    text = 1
    image = 2
    audio = 3
    video = 4


# TODO: add sph file support?
NON_TXT_FILE_EXT_TO_DATA_TYPE = {
    '.jpg': VizSeqDataType.image,
    '.png': VizSeqDataType.image,
    '.gif': VizSeqDataType.image,
    '.bmp': VizSeqDataType.image,
    '.svg': VizSeqDataType.image,
    '.mp3': VizSeqDataType.audio,
    '.wav': VizSeqDataType.audio,
    '.mp4': VizSeqDataType.video,
    '.webm': VizSeqDataType.video,
}

NON_TXT_FILE_EXT_TO_MEDIA_TYPE = {
    '.jpg': 'data:image/jpeg',
    '.png': 'data:image/png',
    '.gif': 'data:image/gif',
    '.bmp': 'data:image/bmp',
    '.svg': 'data:image/svg+xml',
    '.mp3': 'data:audio/mp3',
    '.wav': 'data:audio/wav',
    '.mp4': 'data:video/mp4',
    '.webm': 'data:video/webm',
}

RESERVED_FILE_PREFIXES = {'src_', 'ref_', 'pred_', 'tag_'}

SOUNDFILE_FILE_EXTS = {'.wav', '.flac', '.sph'}


def _get_file_ext(path: str) -> str:
    return str(op.splitext(os.path.basename(path))[1])


def get_name_from_path(path: str) -> Optional[str]:
    filename = str(op.splitext(op.basename(path))[0])
    if any(filename.startswith(p) for p in RESERVED_FILE_PREFIXES):
        return filename.split('_', 1)[1]
    return None


def _get_data_source_names(
        path_or_paths: Union[str, List[str]]
) -> Union[str, List[str]]:
    if len(path_or_paths) == 0:
        return []

    _paths = path_or_paths
    if isinstance(path_or_paths, str):
        _paths = [_paths]

    if get_name_from_path(_paths[0]) is not None:
        names = []
        for p in _paths:
            name = get_name_from_path(p)
            assert name is not None
            names.append(name)
        assert len(names) == len(set(names))
        return names
    else:
        return [str(i) for i, _ in enumerate(_paths)]


def _get_base64_from_fp(fp, media_type: str) -> str:
    encoded = base64.b64encode(fp.read())
    return f'{media_type};base64,' + encoded.decode('utf-8')


def _get_base64_from_path(path: str, media_type: str) -> str:
    with open(path, 'rb') as f:
        return _get_base64_from_fp(f, media_type)


def get_file_type_from_list(paths: List[str]) -> VizSeqDataType:
    file_extensions = list(set(_get_file_ext(p) for p in paths))
    file_types = list(
        set(NON_TXT_FILE_EXT_TO_DATA_TYPE.get(e, None) for e in file_extensions)
    )
    assert len(file_types) == 1 and file_types[0] is not None
    return file_types[0]


class VizSeqDataSourceBase(object):
    def __init__(self):
        self.data = []

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, i) -> str:
        return self.data[i]

    @property
    def data_type(self) -> VizSeqDataType:
        if len(self.data) > 0 and os.path.exists(self.data[0]):
            return get_file_type_from_list(self.data)
        return VizSeqDataType.text

    @property
    def is_text(self) -> bool:
        return self.data_type == VizSeqDataType.text

    @property
    def is_audio(self) -> bool:
        return self.data_type == VizSeqDataType.audio

    @property
    def text(self) -> List[str]:
        if not self.is_text:
            return []
        return self.data

    def cached(self, ids: List[int]) -> List[str]:
        assert all(0 <= i < len(self) for i in ids)
        result = [self.data[i] for i in ids]
        if self.data_type != VizSeqDataType.text:
            for k, i in enumerate(ids):
                file_ext = _get_file_ext(self.data[i])
                media_type = NON_TXT_FILE_EXT_TO_MEDIA_TYPE.get(file_ext, None)
                assert media_type is not None
                result[k] = _get_base64_from_path(self.data[i], media_type)
        return result

    def get_len(self, idx: int, finer=False) -> int:
        if not 0 <= idx <= len(self):
            raise ValueError(f'Invalid index {idx}')
        if self.is_text:
            return len(self.data[idx]) if finer else len(self.data[idx].split())
        elif self.is_audio:
            if any(self.data[idx].endswith(e) for e in SOUNDFILE_FILE_EXTS):
                sound, sr = sf.read(self.data[idx])
                duration_ms = int(len(sound) / sr * 1000)
                n_frames = int(1 + (duration_ms - 25) / 10)
                return duration_ms if finer else n_frames
        return 0

    @property
    def vocab(self) -> List[Tuple[str, int]]:
        if not self.is_text:
            return []
        _vocab = Counter()
        for s in self.data:
            _vocab.update(s.split())
        return _vocab.most_common()

    def get_audio(self, idx) -> Optional[Tuple[np.ndarray, int]]:
        if not self.is_audio:
            return None
        sound, sample_rate = sf.read(self.data[idx])
        return sound, sample_rate

    @property
    def unique(self) -> Set[str]:
        return set(self.data)


class VizSeqListSource(VizSeqDataSourceBase):
    def __init__(self, str_list: List[str]):
        assert all(isinstance(s, str) for s in str_list)
        self.data = str_list


class VizSeqTextFileSource(VizSeqDataSourceBase):
    def __init__(self, path: str):
        assert os.path.exists(path)
        with open(path) as f:
            self.data = [l.strip() for l in f]


class VizSeqZipFileSource(VizSeqDataSourceBase):
    def __init__(self, path: str):
        assert os.path.exists(path) and path.endswith(ZIP_EXT)
        self.path = path
        self.data = None

        with zipfile.ZipFile(path) as zip_f:
            name_list = zip_f.namelist()

            if len(name_list) == 1:
                self._data_type = VizSeqDataType.text
                assert name_list[0].endswith(TXT_EXT)
                with zip_f.open(name_list[0]) as f:
                    self.data = [l.decode('utf-8').strip() for l in f]
            else:
                metadata_txt_name = None
                for name in name_list:
                    if name.endswith(TXT_EXT):
                        # only one txt file for metadata
                        assert metadata_txt_name is None
                        metadata_txt_name = name
                with zip_f.open(metadata_txt_name) as f:
                    self.data = [l.decode('utf-8').strip() for l in f]
                self._data_type = get_file_type_from_list(self.data)
                assert all(fn in name_list for fn in self.data)

    @property
    def data_type(self) -> VizSeqDataType:
        return self._data_type

    def cached(self, ids: List[int]) -> List[str]:
        assert all(0 <= i < len(self) for i in ids)
        if self.data_type == VizSeqDataType.text:
            return [self.data[i] for i in ids]
        else:
            result = []
            with zipfile.ZipFile(self.path) as zip_f:
                for i in ids:
                    file_ext = _get_file_ext(self.data[i])
                    media_type = NON_TXT_FILE_EXT_TO_MEDIA_TYPE.get(
                        file_ext, None
                    )
                    assert media_type is not None
                    with zip_f.open(self.data[i], 'r') as f:
                        result.append(_get_base64_from_fp(f, media_type))
            return result

    def get_len(self, idx: int, finer=False) -> int:
        if not 0 <= idx <= len(self):
            raise ValueError(f'Invalid index {idx}')
        if self.is_text:
            return len(self.data[idx]) if finer else len(self.data[idx].split())
        elif self.is_audio:
            if any(self.data[idx].endswith(e) for e in SOUNDFILE_FILE_EXTS):
                with zipfile.ZipFile(self.path) as zip_f:
                    with zip_f.open(self.data[idx], 'r') as f:
                        sound, sr = sf.read(f)
                        duration_ms = int(len(sound) / sr * 1000)
                        n_frames = int(1 + (duration_ms - 25) / 10)
                        return duration_ms if finer else n_frames
        return 0

    def get_audio(self, idx) -> Optional[Tuple[np.ndarray, int]]:
        if not self.is_audio:
            return None
        with zipfile.ZipFile(self.path) as zip_f:
            with zip_f.open(self.data[idx], 'r') as f:
                sound, sample_rate = sf.read(f)
        return sound, sample_rate


class VizSeqDataSource(object):
    def __init__(self, name: str, path_or_list: Union[str, List[str]]):
        self.name = name
        if isinstance(path_or_list, str) and path_or_list.endswith(ZIP_EXT):
            self.data_source = VizSeqZipFileSource(path_or_list)
        elif isinstance(path_or_list, str):
            self.data_source = VizSeqTextFileSource(path_or_list)
        elif isinstance(path_or_list, list):
            self.data_source = VizSeqListSource(path_or_list)
        else:
            raise Exception('Unknown data source')

    def __len__(self) -> int:
        return len(self.data_source)

    def __getitem__(self, i) -> str:
        return self.data_source[i]

    @property
    def data_type(self) -> VizSeqDataType:
        return self.data_source.data_type

    @property
    def is_text(self) -> bool:
        return self.data_source.is_text

    @property
    def is_audio(self) -> bool:
        return self.data_source.is_audio

    @property
    def text(self) -> List[str]:
        return self.data_source.text

    def cached(self, ids: List[int]) -> List[str]:
        return self.data_source.cached(ids)

    def get_len(self, idx: int, finer=False) -> int:
        return self.data_source.get_len(idx, finer=finer)

    @property
    def vocab(self) -> List[Tuple[str, int]]:
        return self.data_source.vocab

    def get_audio(self, idx) -> Optional[Tuple[np.ndarray, int]]:
        return self.data_source.get_audio(idx)

    @property
    def unique(self) -> Set[str]:
        return self.data_source.unique


class VizSeqDataSources(object):
    def __init__(self, path_or_paths_or_dict: PathOrPathsOrDictOfStrList,
                 text_merged: bool = False):
        self.text_merged = text_merged
        self.names = []
        self.data = []
        if path_or_paths_or_dict is None:
            pass
        elif isinstance(path_or_paths_or_dict, str):
            if len(path_or_paths_or_dict) > 0:
                self.names = _get_data_source_names(path_or_paths_or_dict)
                self.data = [
                    VizSeqDataSource(self.names[0], path_or_paths_or_dict)
                ]
        elif isinstance(path_or_paths_or_dict, list):
            assert all(isinstance(p, str) for p in path_or_paths_or_dict)
            self.names = _get_data_source_names(path_or_paths_or_dict)
            self.data = [
                VizSeqDataSource(n, p)
                for n, p in zip(self.names, path_or_paths_or_dict)
            ]
        elif isinstance(path_or_paths_or_dict, dict):
            self.names = sorted(path_or_paths_or_dict)
            self.data = [
                VizSeqDataSource(n, path_or_paths_or_dict[n])
                for n in self.names
            ]
        else:
            raise ValueError('Unknown type of data source')

        self.n_examples = len(self.data[0]) if len(self.data) > 0 else 0
        assert all(len(d) == self.n_examples for d in self.data)

    def __len__(self) -> int:
        return self.n_examples

    def __getitem__(self, i) -> List[str]:
        return [d[i] for d in self.data]

    @property
    def n_sources(self) -> int:
        return len(self.names)

    @property
    def data_types(self) -> List[VizSeqDataType]:
        return [d.data_type for d in self.data]

    @property
    def text(self) -> List[List[str]]:
        text = [d.text for d in self.data if d.is_text]
        if self.text_merged:
            return [list(t) for t in zip(*text)]
        return text

    @property
    def text_names(self) -> List[str]:
        return [n for n, d in zip(self.names, self.data) if d.is_text]

    @property
    def text_indices(self) -> List[int]:
        indices = [i for i, d in enumerate(self.data) if d.is_text]
        return indices

    @property
    def main_text_idx(self) -> Optional[int]:
        for i, d in enumerate(self.data):
            if d.is_text:
                return i
        return None

    @property
    def main_text(self) -> Optional[List[str]]:
        idx = self.main_text_idx
        if idx is None:
            return None
        return self.data[idx].text

    def cached(self, ids: List[int]) -> List[List[str]]:
        assert all(0 <= i < len(self) for i in ids)
        return [d.cached(ids) for d in self.data]

    @property
    def has_text(self):
        return any(d.is_text for d in self.data)

    @property
    def has_audio(self):
        return any(d.is_audio for d in self.data)

    def unique(
            self, text=True, image=False, audio=False, video=False
    ) -> Set[str]:
        _unique = set()
        for d in self.data:
            if d.data_type == VizSeqDataType.text and not text:
                continue
            elif d.data_type == VizSeqDataType.image and not image:
                continue
            elif d.data_type == VizSeqDataType.audio and not audio:
                continue
            elif d.data_type == VizSeqDataType.video and not video:
                continue
            _unique.update(d.unique)
        return _unique
