"""
Utility for compressing and archiving PDB Engine job results.
"""

import os
import zipfile
import logging
from core.settings import settings

logger = logging.getLogger(__name__)


class ArchiveManager:
    """Handles creation of ZIP archives from job workspaces."""

    @staticmethod
    def create_results_zip(workspace_path: str, zip_name: str) -> str:
        """
        Create a ZIP archive of all files in the workspace.

        Args:
            workspace_path: Path to workspace directory.
            zip_name: Desired name for the ZIP file (without extension).

        Returns:
            str: Path to the created ZIP file.
        """
        os.makedirs(settings.WORKING_DIR, exist_ok=True)
        zip_path = os.path.join(settings.WORKING_DIR, f"{zip_name}.zip")

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(workspace_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, workspace_path)
                        zipf.write(file_path, arcname)

            logger.info(f"Created results archive: {zip_path}")
            return zip_path

        except Exception as e:
            logger.error(f"Failed to create ZIP archive: {e}")
            raise
