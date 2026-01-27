# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import zipfile

# Maximum total uncompressed size allowed (1 GB)
MAX_UNCOMPRESSED_SIZE = 1024 * 1024 * 1024
# Maximum compression ratio allowed (to detect zip bombs)
MAX_COMPRESSION_RATIO = 100


class ZipExtractionError(Exception):
    """Exception raised for ZIP extraction security issues."""
    pass


class VizSeqZipFile(object):
    @classmethod
    def _validate_zip_member(cls, member: zipfile.ZipInfo, root: str) -> str:
        """Validate a ZIP member to prevent path traversal attacks.

        Args:
            member: ZipInfo object for the member to validate
            root: The root directory for extraction

        Returns:
            The safe absolute path for extraction

        Raises:
            ZipExtractionError: If the member path is unsafe
        """
        # Get the member filename and normalize it
        member_path = member.filename

        # Check for path traversal attempts
        if '..' in member_path:
            raise ZipExtractionError(
                f'Path traversal detected in ZIP member: {member_path}'
            )

        # Check for absolute paths
        if os.path.isabs(member_path):
            raise ZipExtractionError(
                f'Absolute path not allowed in ZIP member: {member_path}'
            )

        # Compute the absolute target path
        target_path = os.path.normpath(os.path.join(root, member_path))
        root_abs = os.path.abspath(root)

        # Ensure the target is within the root directory
        if not target_path.startswith(root_abs + os.sep) and target_path != root_abs:
            raise ZipExtractionError(
                f'ZIP member would extract outside target directory: {member_path}'
            )

        return target_path

    @classmethod
    def _check_zip_bomb(cls, zip_f: zipfile.ZipFile) -> None:
        """Check for potential zip bomb attacks.

        Args:
            zip_f: The ZipFile object to check

        Raises:
            ZipExtractionError: If the ZIP appears to be a zip bomb
        """
        total_uncompressed = sum(info.file_size for info in zip_f.infolist())
        total_compressed = sum(info.compress_size for info in zip_f.infolist())

        if total_uncompressed > MAX_UNCOMPRESSED_SIZE:
            raise ZipExtractionError(
                f'ZIP file too large: {total_uncompressed} bytes '
                f'(max: {MAX_UNCOMPRESSED_SIZE} bytes)'
            )

        if total_compressed > 0:
            ratio = total_uncompressed / total_compressed
            if ratio > MAX_COMPRESSION_RATIO:
                raise ZipExtractionError(
                    f'Suspicious compression ratio ({ratio:.1f}:1) - '
                    f'possible zip bomb detected'
                )

    @classmethod
    def unzip(cls, root, file_name, remove_after_unpacking=True):
        """Safely extract a ZIP file to the specified root directory.

        Args:
            root: The root directory for extraction
            file_name: The name of the ZIP file within root
            remove_after_unpacking: Whether to delete the ZIP after extraction

        Raises:
            ZipExtractionError: If the ZIP file fails security validation
            zipfile.BadZipFile: If the ZIP file is corrupted
        """
        zip_file_path = os.path.join(root, file_name)
        if not zip_file_path.endswith('.zip'):
            raise ZipExtractionError('File must have .zip extension')

        root_abs = os.path.abspath(root)

        with zipfile.ZipFile(zip_file_path) as zip_f:
            # Test ZIP integrity
            bad_file = zip_f.testzip()
            if bad_file is not None:
                raise ZipExtractionError(
                    f'ZIP file is corrupted, bad file: {bad_file}'
                )

            # Check for zip bomb
            cls._check_zip_bomb(zip_f)

            # Validate all members before extracting any
            for member in zip_f.infolist():
                cls._validate_zip_member(member, root_abs)

            # Safe to extract - all members validated
            zip_f.extractall(root)

        if remove_after_unpacking:
            os.remove(zip_file_path)
