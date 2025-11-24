from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CommandExecutionResponse(BaseModel):
    """Generic response model for command execution"""
    job_id: str
    status: str
    message: str
    command: str
    download_url: Optional[str] = None

class PDBEngineExecutionResult(BaseModel):
    """Result of PDB Engine execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int

class JobInfo(BaseModel):
    """Generic information about a submitted job."""
    job_id: str
    job_path: str
    input_filename: Optional[str] = None
    command: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    flags: List[str] = Field(default_factory=list)
    status: str
    download_url: Optional[str] = None
    message: Optional[str] = None