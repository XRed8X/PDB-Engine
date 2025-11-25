"""
Service responsible for executing the PDB Engine command and capturing results.
"""

import subprocess
import time
from pathlib import Path
from typing import List
from core import settings, SecurityError
from models.models2 import PDBEngineExecutionResult


class PDBEngineExecutor:
    """Executes PDB Engine commands in a controlled and secure environment."""

    @staticmethod
    def execute(command: List[str], working_directory: Path) -> PDBEngineExecutionResult:
        """Execute PDB Engine command with security measures."""
        print(f"Executing: {' '.join(command)}")
        print(f"Execution started...")

        start_time = time.time()
        try:
            process = subprocess.run(
                command,
                cwd=working_directory.absolute(),
                capture_output=True,
                text=True,
                timeout=settings.PDBENGINE_TIMEOUT,
                shell=False  # Security-critical
            )

            execution_time = time.time() - start_time
            print(f"Execution completed in {execution_time:.2f} seconds")

            return PDBEngineExecutionResult(
                success=process.returncode == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                execution_time=execution_time
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"Execution terminated due to timeout after {execution_time:.2f} seconds")
            return PDBEngineExecutionResult(
                success=False,
                stdout="",
                stderr=f"Process exceeded timeout of {settings.PDBENGINE_TIMEOUT} seconds",
                return_code=-1,
                execution_time=execution_time
            )

        except SecurityError as e:
            execution_time = time.time() - start_time
            print(f"Security error: {e}")
            print(f"Execution terminated due to security error after {execution_time:.2f} seconds")
            return PDBEngineExecutionResult(
                success=False,
                stdout="",
                stderr=f"Security violation: {str(e)}",
                return_code=-2,
                execution_time=execution_time
            )
