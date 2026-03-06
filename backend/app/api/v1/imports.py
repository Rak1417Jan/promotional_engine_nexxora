"""
Import API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.operator_user import OperatorUser
from app.models.import_job import ImportJob
from app.schemas.import_export import ImportJobCreate, ImportJobResponse
from app.services.import_service import ImportService
from app.services.minio_service import MinIOService
from app.utils.logger import logger
from datetime import datetime
import uuid

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/", response_model=ImportJobResponse, status_code=status.HTTP_201_CREATED)
async def create_import_job(
    file: UploadFile = File(...),
    entity_type: str = None,
    file_format: str = None,
    schema_id: int = None,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new import job"""
    try:
        # Get operator_id from user
        operator_id = current_user.operator_id
        
        # Determine file format
        if not file_format:
            file_format = file.filename.split('.')[-1].lower()
            if file_format not in ['csv', 'json', 'xlsx', 'xls', 'xml']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file format"
                )
        
        # Determine entity type from filename or parameter
        if not entity_type:
            # Try to infer from filename
            entity_type = "custom"  # Default
        
        # Read file content
        file_content = await file.read()
        
        # Upload to MinIO
        file_path = f"imports/{operator_id}/{uuid.uuid4()}/{file.filename}"
        MinIOService.upload_file(file_path, file_content, file.content_type or "application/octet-stream")
        
        # Create import job
        import_job = ImportJob(
            operator_id=operator_id,
            entity_type=entity_type,
            file_name=file.filename,
            file_path=file_path,
            file_format=file_format,
            schema_id=schema_id,
            status="pending",
            created_by=current_user.id
        )
        db.add(import_job)
        db.commit()
        db.refresh(import_job)
        
        # TODO: Trigger Celery task for async processing
        # from app.tasks.import_tasks import process_import_job
        # process_import_job.delay(import_job.id)
        
        logger.info("Import job created", job_id=import_job.id, operator_id=operator_id)
        return import_job
        
    except Exception as e:
        db.rollback()
        logger.error("Error creating import job", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating import job: {str(e)}"
        )


@router.get("/{job_id}", response_model=ImportJobResponse)
async def get_import_job(
    job_id: int,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get import job status"""
    import_job = db.query(ImportJob).filter(
        ImportJob.id == job_id,
        ImportJob.operator_id == current_user.operator_id
    ).first()
    
    if not import_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found"
        )
    
    return import_job


@router.get("/", response_model=List[ImportJobResponse])
async def list_import_jobs(
    entity_type: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List import jobs"""
    query = db.query(ImportJob).filter(
        ImportJob.operator_id == current_user.operator_id
    )
    
    if entity_type:
        query = query.filter(ImportJob.entity_type == entity_type)
    if status:
        query = query.filter(ImportJob.status == status)
    
    import_jobs = query.order_by(ImportJob.created_at.desc()).limit(limit).offset(offset).all()
    return import_jobs
