"""
Generic command service - executes any PDB Engine command dynamically.
"""
import logging
from pathlib import Path

from models.models import PDBEngineExecutionResult, JobInfo
from services.engine_executor import PDBEngineExecutor
from services.pdb_cleaner_service import PDBCleanerService
from core.valid_commands import build_command_from_dict
from errors.engine_exceptions import PDBEngineExecutionError as EngineExecutionError

logger = logging.getLogger(__name__)

class GenericCommandService:
    """Service for executing any PDB Engine command"""
    
    @staticmethod
    def execute_command(job_info: JobInfo) -> PDBEngineExecutionResult:
        """
        Execute any PDB Engine command dynamically.
        
        Args:
            job_info: Job information containing command, arguments, and flags
            
        Returns:
            PDBEngineExecutionResult with execution details
        """
        try:
            job_path = Path(job_info.job_path)
            
            logger.info(f"Executing command '{job_info.command}' for job {job_info.job_id}")
            logger.info(f"Working directory: {job_path}")
            
            # Clean PDB file if present
            if job_info.input_filename and 'pdb' in job_info.arguments:
                input_file = Path(job_info.arguments['pdb'])
                if input_file.exists():
                    logger.info(f"Cleaning PDB file: {input_file}")
                    cleaner = PDBCleanerService()
                    cleaned_file = cleaner.validate_and_clean(str(input_file))
                    job_info.arguments['pdb'] = cleaned_file
                    logger.info(f"PDB cleaned: {cleaned_file}")
            
            # Build command dynamically
            command_args = build_command_from_dict(
                command=job_info.command,
                arguments=job_info.arguments,
                flags=job_info.flags
            )
            
            logger.info(f"Executing: {' '.join(command_args)}")
            
            # Execute command
            result = PDBEngineExecutor.execute(command_args, job_path)
            
            if result.success:
                logger.info(f"Command '{job_info.command}' executed successfully for job {job_info.job_id}")
            else:
                logger.error(f"Command '{job_info.command}' failed for job {job_info.job_id}: {result.stderr}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing command '{job_info.command}': {e}", exc_info=True)
            raise EngineExecutionError(f"Failed to execute command '{job_info.command}': {str(e)}")