"""
Service responsible for executing the PDB Engine command and capturing results.
"""

import subprocess
import time
import logging
from pathlib import Path
from typing import List
from core.settings import settings
from core.security import SecurityError
from models.models2 import PDBEngineExecutionResult

logger = logging.getLogger(__name__)


class PDBEngineExecutor:
    """Executes PDB Engine commands in a controlled and secure environment."""

    @staticmethod
    def execute(command: List[str], working_directory: Path) -> PDBEngineExecutionResult:
        """
        Execute PDB Engine command using Docker or local binary.
        
        Args:
            command: Command arguments
            working_directory: Working directory for execution
            
        Returns:
            PDBEngineExecutionResult with execution details
        """
        logger.info(f"Executing command: {' '.join(command)}")
        logger.info(f"Working directory: {working_directory}")
        logger.info(f"Use Docker: {settings.USE_DOCKER}")
        
        if settings.USE_DOCKER:
            from services.docker_executor import DockerExecutor
            logger.info("Using Docker executor")
            return DockerExecutor.execute(command, working_directory)
        else:
            logger.info("Using local executor")
            return PDBEngineExecutor._execute_local(command, working_directory)

    @staticmethod
    def _execute_local(command: List[str], working_directory: Path) -> PDBEngineExecutionResult:
        """Execute PDB Engine command with local binary (original implementation)."""
        logger.info(f"Executing locally: {' '.join(command)}")
        logger.info(f"Execution started...")

        start_time = time.time()
        try:
            process = subprocess.run(
                command,
                cwd=working_directory.absolute(),
                capture_output=True,
                text=True,
                timeout=settings.PDBENGINE_TIMEOUT,
                shell=False
            )

            execution_time = time.time() - start_time
            logger.info(f"Execution completed in {execution_time:.2f} seconds")

            return PDBEngineExecutionResult(
                success=process.returncode == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                execution_time=execution_time
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"Execution terminated due to timeout after {execution_time:.2f} seconds")
            return PDBEngineExecutionResult(
                success=False,
                stdout="",
                stderr=f"Process exceeded timeout of {settings.PDBENGINE_TIMEOUT} seconds",
                return_code=-1,
                execution_time=execution_time
            )

        except SecurityError as e:
            execution_time = time.time() - start_time
            logger.error(f"Security error: {e}")
            return PDBEngineExecutionResult(
                success=False,
                stdout="",
                stderr=f"Security violation: {str(e)}",
                return_code=-2,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Unexpected error during local execution: {e}", exc_info=True)
            return PDBEngineExecutionResult(
                success=False,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                return_code=-3,
                execution_time=execution_time
            )
