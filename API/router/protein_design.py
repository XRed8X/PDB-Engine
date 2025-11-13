"""
Protein design router handles incoming requests and delegates to service layer.
"""
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from models.models import JobInfo

from utils.archive_manager import ArchiveManager
from services.protein_design_service import ProteinDesignService
from utils.workspace_manager import WorkspaceManager
from core.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["protein_design"])

@router.post("/protein_design")
async def design_protein(
    background_tasks: BackgroundTasks,
    pdb_file: UploadFile = File(...),
    ppint: bool = Form(False),
    interface_only: bool = Form(False)
):
    """
    Handles a protein design request and returns a ZIP of the results.
    Delegates all processing logic to the service layer.
    """
    job_path = None
    try:
        # --- Basic file validation ---
        if not pdb_file.filename.lower().endswith(".pdb"):
            raise HTTPException(status_code=400, detail="Only PDB files are allowed")

        content = await pdb_file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File too large (max {settings.max_file_size_mb:.1f} MB)")

        # --- Create workspace and save file ---
        job_path = WorkspaceManager.create_workspace()
        job_id = Path(job_path).name
        input_file = Path(job_path) / pdb_file.filename

        with open(input_file, "wb") as f:
            f.write(content)

        logger.info(f"Created job {job_id} with file: {pdb_file.filename}")

        # --- Create job info and delegate to service ---
        job_info = JobInfo(
            job_id=job_id,
            job_path=str(job_path),
            input_filename=pdb_file.filename,
            status="submitted",
            options={
                "ppint": ppint,
                "interface_only": interface_only
            }
        )

        # --- Delegate all processing to service (including PDB cleaning) ---
        result = ProteinDesignService.process_request(job_info)
        
        if not result.success:
            raise HTTPException(
                status_code=500, 
                detail=f"Protein design failed: {result.stderr or 'Unknown error'}"
            )

        # --- Create results archive ---
        zip_name = f"protein_design_results_{job_id}"  # ArchiveManager adds .zip extension
        zip_path = ArchiveManager.create_results_zip(str(job_path), zip_name)

        if not Path(zip_path).exists():
            raise HTTPException(status_code=500, detail="Failed to create results archive")

        logger.info(f"Job {job_id} completed successfully. Results: {zip_path}")

        # --- Schedule cleanup ---
        background_tasks.add_task(WorkspaceManager.cleanup_path, str(zip_path))
        background_tasks.add_task(WorkspaceManager.cleanup_path, str(job_path))

        return FileResponse(
            path=zip_path,
            filename=Path(zip_path).name,
            media_type="application/zip"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in protein design: {e}")
        if job_path and Path(job_path).exists():
            background_tasks.add_task(WorkspaceManager.cleanup_path, str(job_path))
        raise HTTPException(status_code=500, detail="Internal server error")