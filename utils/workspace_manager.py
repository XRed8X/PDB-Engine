"""
Utility for managing temporary workspace directories for PDB Engine jobs.
"""

import os
import uuid
import shutil
import logging
from typing import List
from pathlib import Path
from core.settings import settings

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """Handles workspace creation, cleanup, and listing."""

    @staticmethod
    def create_workspace() -> str:
        """
        Create a unique workspace directory for job processing.
        Returns:
            str: Path to the created workspace directory.
        """
        workspace_id = str(uuid.uuid4())
        workspace_path = os.path.join(settings.WORKING_DIR, workspace_id)
        os.makedirs(workspace_path, exist_ok=True)
        logger.info(f"Created workspace: {workspace_path}")
        return workspace_path

    @staticmethod
    def cleanup_path(path: str):
        """
        Delete a file or directory (recursive if directory).
        """
        try:
            p = Path(path)
            if p.exists():
                if p.is_file():
                    p.unlink()
                    logger.info(f"Cleaned up file: {path}")
                elif p.is_dir():
                    shutil.rmtree(p)
                    logger.info(f"Cleaned up directory: {path}")
        except Exception as e:
            logger.error(f"Failed to cleanup {path}: {e}")

    @staticmethod
    def get_workspace_files(workspace_path: str) -> List[str]:
        """
        List all files within a workspace.
        Returns:
            List[str]: List of file paths.
        """
        files = []
        if os.path.exists(workspace_path):
            for root, _, filenames in os.walk(workspace_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        return files