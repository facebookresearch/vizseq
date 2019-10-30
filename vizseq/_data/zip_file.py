# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import zipfile


class VizSeqZipFile(object):
    @classmethod
    def unzip(cls, root, file_name, remove_after_unpacking=True):
        zip_file_path = os.path.join(root, file_name)
        assert zip_file_path.endswith('.zip')
        with zipfile.ZipFile(zip_file_path) as zip_f:
            zip_f.extractall(root)
        # TODO: to add integrity check
        if remove_after_unpacking:
            os.remove(zip_file_path)
