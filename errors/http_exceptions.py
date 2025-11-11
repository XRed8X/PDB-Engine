"""
HTTP exception classes and error mapping for PDB Engine API.
"""

from typing import Optional, Dict
from fastapi import HTTPException, status
from .base_exceptions import PDBEngineError
from .engine_exceptions import (
    ConfigurationError, FileValidationError, SecurityViolationError,
    ValidationError, WorkspaceError, JobNotFoundError,
    PDBEngineNotFoundError, PDBEngineTimeoutError, PDBEngineExecutionError
)


class PDBEngineHTTPException(HTTPException):
    """Base HTTP exception for PDB Engine API."""
    
    def __init__(self, status_code: int, error: PDBEngineError, headers: Optional[Dict[str, str]] = None):
        self.pdb_error = error
        detail = error.to_dict()
        super().__init__(status_code=status_code, detail=detail, headers=headers)


def handle_pdb_engine_error(error: PDBEngineError) -> PDBEngineHTTPException:
    """
    Convert a PDBEngineError to an appropriate HTTPException.
    """
    error_mapping = {
        ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        FileValidationError: status.HTTP_400_BAD_REQUEST,
        SecurityViolationError: status.HTTP_400_BAD_REQUEST,
        ValidationError: status.HTTP_400_BAD_REQUEST,
        WorkspaceError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        JobNotFoundError: status.HTTP_404_NOT_FOUND,
        PDBEngineNotFoundError: status.HTTP_503_SERVICE_UNAVAILABLE,
        PDBEngineTimeoutError: status.HTTP_408_REQUEST_TIMEOUT,
        PDBEngineExecutionError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = error_mapping.get(type(error), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return PDBEngineHTTPException(status_code=status_code, error=error)
