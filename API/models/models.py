from pydantic import BaseModel, Field
from fastapi import Form
from typing import List, Optional, Dict

class ProteinDesignRequest(BaseModel):
    ppint: bool = Field(False, description="ppint value (optional)")
    interface_only: bool = Field(False, description="Just design the interface")
    iterations: int = Field(1, description="Number of design iterations")
    
    @classmethod
    def as_form(
        cls,
        ppint: bool = Form(False),
        interface_only: bool = Form(False),
        iterations: int = Form(1),
    ) -> "ProteinDesignRequest":
        return cls(
            ppint=ppint,
            interface_only=interface_only,
            iterations=iterations,
        )
class PDBEngineExecutionResult(BaseModel):
    """Result of PDB Engine execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float = 0.0

class JobInfo(BaseModel):
    """Information about a submitted job."""
    job_id: str
    job_path: str
    input_filename: str
    options: Dict[str, Optional[bool]]
    status: str
    download_url: Optional[str] = None
    message: Optional[str] = None
    flags_used: Optional[List[str]] = None