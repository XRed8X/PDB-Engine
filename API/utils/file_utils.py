"""
General-purpose file utilities: validation, sanitization, and extension checking.
"""

import os
import re
from typing import List


class FileUtils:
    """Provides file-related utility functions."""

    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """
        Check if the file has an allowed extension.

        Returns:
            bool: True if the file extension is allowed.
        """
        file_ext = os.path.splitext(filename)[1].lower()
        return file_ext in [ext.lower() for ext in allowed_extensions]

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal or injection attacks.

        Returns:
            str: Safe filename.
        """
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        if len(sanitized) > 100:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:95] + ext

        return sanitized
