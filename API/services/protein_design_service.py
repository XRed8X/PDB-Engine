"""
High-level orchestration service for the Protein Design process.
"""

import logging
from pathlib import Path
from models.models import JobInfo, PDBEngineExecutionResult
from services.command_builder import PDBCommandBuilder
from services.engine_executor import PDBEngineExecutor
from services.pdb_cleaner_service import PDBCleanerService
from core.settings import settings

logger = logging.getLogger(__name__)


class ProteinDesignService:
    """Coordinates the full protein design workflow using the PDB Engine."""

    def __init__(self):
        self.pdb_cleaner = PDBCleanerService()

    @classmethod
    def process_request(cls, job_info: JobInfo) -> PDBEngineExecutionResult:
        """
        Process complete protein design request with optional PDB preprocessing.
        
        Flow:
        1. Create workspace (already done in router)
        2. Save original file (already done in router) 
        3. Apply PDB cleaning if enabled
        4. Build command using cleaned/original PDB
        5. Execute PDB Engine
        6. Return results
        """
        logger.info(f"Processing protein design request for job: {job_info.job_id}")
        
        service_instance = cls()
        return service_instance._process_request_internal(job_info)
    
    def _process_request_internal(self, job_info: JobInfo) -> PDBEngineExecutionResult:
        """Internal processing method with access to instance methods."""
        input_pdb_path = Path(job_info.job_path) / job_info.input_filename
        
        logger.info(f"Original PDB file: {input_pdb_path}")
        
        # Apply PDB cleaning/preprocessing if enabled
        try:
            # Determine if we should keep all chains for protein-protein interface analysis
            keep_all_chains = getattr(settings, 'PREPROCESSING_KEEP_ALL_CHAINS_BY_DEFAULT', True)
            
            # Get options to check for interface_only flag
            options = job_info.options
            if isinstance(options, dict):
                interface_only = options.get('interface_only', False)
            else:
                interface_only = getattr(options, 'interface_only', False)
            
            # For interface analysis, we definitely want to keep all protein chains
            if interface_only:
                keep_all_chains = True
                logger.info("Interface analysis requested - ensuring all protein chains are kept")
            
            # Clean PDB file if preprocessing is enabled
            processed_pdb_path = self.pdb_cleaner.validate_and_clean(
                str(input_pdb_path), 
                keep_all_chains=keep_all_chains
            )
            
            if processed_pdb_path != str(input_pdb_path):
                logger.info(f"Using cleaned PDB file: {processed_pdb_path}")
                # Update the path to use the cleaned version
                final_pdb_path = Path(processed_pdb_path)
            else:
                logger.info("Using original PDB file (no cleaning needed)")
                final_pdb_path = input_pdb_path
                
        except Exception as e:
            logger.error(f"PDB preprocessing failed: {e}")
            logger.warning("Falling back to original PDB file")
            final_pdb_path = input_pdb_path

        # Build command using final PDB path (cleaned or original)
        command = PDBCommandBuilder.build_secure_command(final_pdb_path, job_info.options)
        
        # Execute PDB Engine
        result = PDBEngineExecutor.execute(command, Path(job_info.job_path))

        if not result.success:
            logger.error(f"PDB Engine execution failed:")
            logger.error(f"Stderr: {result.stderr}")
            logger.error(f"Stdout: {result.stdout}")
        else:
            logger.info("PDB Engine execution completed successfully")

        return result
