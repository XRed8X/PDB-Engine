"""
High-level orchestration service for the Protein Design process.
"""

from pathlib import Path
from models.models import JobInfo, PDBEngineExecutionResult
from services.command_builder import PDBCommandBuilder
from services.engine_executor import PDBEngineExecutor


class ProteinDesignService:
    """Coordinates the full protein design workflow using the PDB Engine."""

    @classmethod
    def process_request(cls, job_info: JobInfo) -> PDBEngineExecutionResult:
        """Process complete protein design request."""
        input_pdb_path = Path(job_info.job_path) / job_info.input_filename

        command = PDBCommandBuilder.build_secure_command(input_pdb_path, job_info.options)
        result = PDBEngineExecutor.execute(command, Path(job_info.job_path))

        if not result.success:
            print(f"Stderr: {result.stderr}")
            print(f"Stdout: {result.stdout}")

        return result
