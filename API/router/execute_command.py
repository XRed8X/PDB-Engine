"""
Generic command executor router - handles any PDB Engine command dynamically.
"""
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
import json

from models.models import CommandExecutionResponse, JobInfo
from services.command_builder import GenericCommandService
from utils.workspace_manager import WorkspaceManager
from utils.archive_manager import ArchiveManager
from core.settings import settings
from core.valid_commands import CommandValidator

logger = logging.getLogger(__name__)
router = APIRouter(tags=["commands"])

@router.post("/execute")
async def execute_command(
    background_tasks: BackgroundTasks,
    command: str = Form(...),
    arguments: str = Form("{}"),
    flags: str = Form("[]"),
    file: Optional[UploadFile] = File(None)
):
    """
    Generic endpoint to execute any PDB Engine command.
    
    Args:
        command: Command name (e.g., "ProteinDesign")
        arguments: JSON string of arguments as key-value pairs
        flags: JSON array of flag names
        file: Optional PDB file upload
    """
    logger.info("=== EXECUTE COMMAND CALLED ===")
    logger.info(f"Received command: {command}")
    logger.info(f"Arguments: {arguments}")
    logger.info(f"Flags: {flags}")
    logger.info(f"File: {file.filename if file else 'None'}")

    job_path = None
    zip_path = None
    
    try:
        # Parse JSON strings
        try:
            args_dict = json.loads(arguments)
            flags_list = json.loads(flags)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        logger.info(f"Executing command: {command}")
        logger.info(f"Arguments: {args_dict}")
        logger.info(f"Flags: {flags_list}")

        # Validate command
        if not CommandValidator.is_valid_command(command):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid command: {command}"
            )

        # Create workspace
        job_path = WorkspaceManager.create_workspace()
        job_id = Path(job_path).name

        # Handle file upload if present
        input_filename = None
        if file:
            if not file.filename.lower().endswith(".pdb"):
                raise HTTPException(status_code=400, detail="Only PDB files are allowed")
            
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413, 
                    detail=f"File too large (max {settings.max_file_size_mb:.1f} MB)"
                )
            
            input_filename = file.filename
            input_file = Path(job_path) / input_filename
            
            with open(input_file, "wb") as f:
                f.write(content)
            
            # Add file path to arguments
            args_dict['pdb'] = str(input_file)
            logger.info(f"File uploaded: {input_filename}")

        # Create job info
        job_info = JobInfo(
            job_id=job_id,
            job_path=job_path,
            input_filename=input_filename,
            command=command,
            arguments=args_dict,
            flags=flags_list,
            status="submitted"
        )

        logger.info(f"Created job {job_id} for command {command}")

        # Execute command using generic service
        result = GenericCommandService.execute_command(job_info)
        
        if not result.success:
            logger.error(f"Command failed: {result.stderr}")
            job_info.status = "error"
            job_info.execution_time = result.execution_time
            raise HTTPException(
                status_code=500,
                detail=f"Command execution failed: {result.stderr or 'Unknown error'}"
            )

        # Update job info with execution results
        job_info.status = "finished"
        job_info.execution_time = result.execution_time

        # Create results archive
        zip_name = f"{command.lower()}_results_{job_id}"
        zip_path = ArchiveManager.create_results_zip(job_path, zip_name)

        if not Path(zip_path).exists():
            raise HTTPException(status_code=500, detail="Failed to create results archive")

        logger.info(f"Job {job_id} completed successfully. Archive: {zip_path}")

        # Schedule cleanup
        background_tasks.add_task(WorkspaceManager.cleanup_path, str(zip_path))
        background_tasks.add_task(WorkspaceManager.cleanup_path, job_path)

        # Return file response directly with CORS headers
        response = FileResponse(
            path=zip_path,
            filename=Path(zip_path).name,
            media_type="application/zip"
        )
        
        # Add CORS headers explicitly
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["X-Execution-Time"] = str(result.execution_time)
        response.headers["X-Job-Status"] = job_info.status
        
        return response

    except HTTPException:
        if job_path and Path(job_path).exists():
            background_tasks.add_task(WorkspaceManager.cleanup_path, job_path)
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        if job_path and Path(job_path).exists():
            background_tasks.add_task(WorkspaceManager.cleanup_path, job_path)
        if zip_path and Path(zip_path).exists():
            background_tasks.add_task(WorkspaceManager.cleanup_path, str(zip_path))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")