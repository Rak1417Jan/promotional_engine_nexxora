"""
Export API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.operator_user import OperatorUser
from app.models.export_job import ExportJob
from app.schemas.import_export import ExportJobCreate, ExportJobResponse
from app.services.export_service import ExportService
from app.services.minio_service import MinIOService
from app.utils.logger import logger
from datetime import datetime, timedelta
import uuid
import tempfile
import os

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/", response_model=ExportJobResponse, status_code=status.HTTP_201_CREATED)
async def create_export_job(
    export_data: ExportJobCreate,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new export job"""
    try:
        operator_id = current_user.operator_id
        
        # Create export job
        export_job = ExportJob(
            operator_id=operator_id,
            entity_type=export_data.entity_type,
            export_format=export_data.export_format,
            filters=export_data.filters,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(days=7),  # 7 day retention
            created_by=current_user.id
        )
        db.add(export_job)
        db.commit()
        db.refresh(export_job)
        
        # TODO: Trigger Celery task for async processing
        # from app.tasks.export_tasks import process_export_job
        # process_export_job.delay(export_job.id)
        
        logger.info("Export job created", job_id=export_job.id, operator_id=operator_id)
        return export_job
        
    except Exception as e:
        db.rollback()
        logger.error("Error creating export job", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating export job: {str(e)}"
        )


@router.get("/{job_id}", response_model=ExportJobResponse)
async def get_export_job(
    job_id: int,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get export job status"""
    export_job = db.query(ExportJob).filter(
        ExportJob.id == job_id,
        ExportJob.operator_id == current_user.operator_id
    ).first()
    
    if not export_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found"
        )
    
    return export_job


@router.get("/{job_id}/download")
async def download_export(
    job_id: int,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download export file"""
    export_job = db.query(ExportJob).filter(
        ExportJob.id == job_id,
        ExportJob.operator_id == current_user.operator_id
    ).first()
    
    if not export_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found"
        )
    
    if export_job.status != "completed" or not export_job.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export job not completed"
        )
    
    # Download from MinIO
    file_data = MinIOService.download_file(export_job.file_path)
    
    # Create temporary file
    file_ext = export_job.export_format
    if file_ext == "excel":
        file_ext = "xlsx"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
        tmp_file.write(file_data)
        tmp_file_path = tmp_file.name
    
    return FileResponse(
        tmp_file_path,
        filename=f"export_{job_id}.{file_ext}",
        media_type="application/octet-stream"
    )


@router.get("/", response_model=List[ExportJobResponse])
async def list_export_jobs(
    entity_type: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List export jobs"""
    query = db.query(ExportJob).filter(
        ExportJob.operator_id == current_user.operator_id
    )
    
    if entity_type:
        query = query.filter(ExportJob.entity_type == entity_type)
    if status:
        query = query.filter(ExportJob.status == status)
    
    export_jobs = query.order_by(ExportJob.created_at.desc()).limit(limit).offset(offset).all()
    return export_jobs
