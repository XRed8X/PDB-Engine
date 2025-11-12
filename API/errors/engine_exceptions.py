"""
Specific exception types for the PDB Engine.
"""

from typing import Optional, List
from .base_exceptions import PDBEngineError


class ConfigurationError(PDBEngineError):
    """Raised when there's a configuration problem."""
    pass


class FileValidationError(PDBEngineError):
    """Raised when file validation fails."""
    pass


class SecurityViolationError(PDBEngineError):
    """Raised when a security violation is detected."""
    pass


class PDBEngineExecutionError(PDBEngineError):
    """Raised when PDB Engine execution fails."""
    
    def __init__(self, message: str, command: Optional[List[str]] = None,
                 exit_code: Optional[int] = None, stderr: Optional[str] = None,
                 timeout: bool = False):
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        self.timeout = timeout
        
        # Add details for context
        self.details = {
            "command": command,
            "exit_code": exit_code,
            "timeout": timeout
        }
        if stderr:
            self.details["stderr"] = stderr[:1000]  # Limit stderr output


class PDBEngineNotFoundError(PDBEngineExecutionError):
    """Raised when PDB Engine binary is not found."""
    pass


class PDBEngineTimeoutError(PDBEngineExecutionError):
    """Raised when PDB Engine execution times out."""
    pass


class JobNotFoundError(PDBEngineError):
    """Raised when a job is not found."""
    pass


class ValidationError(PDBEngineError):
    """Raised when input validation fails."""
    pass


class WorkspaceError(PDBEngineError):
    """Raised when workspace operations fail."""
    pass
