"""
Operator API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.operator import OperatorCreate, OperatorUpdate, OperatorResponse
from app.models.operator import Operator
from app.utils.logger import logger

router = APIRouter(prefix="/operators", tags=["operators"])


@router.post("/", response_model=OperatorResponse, status_code=status.HTTP_201_CREATED)
async def create_operator(
    operator: OperatorCreate,
    db: Session = Depends(get_db)
):
    """Create a new operator"""
    try:
        # Check if domain_url already exists
        existing = db.query(Operator).filter(Operator.domain_url == operator.domain_url).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Operator with this domain already exists"
            )
        
        db_operator = Operator(**operator.dict())
        db.add(db_operator)
        db.commit()
        db.refresh(db_operator)
        
        logger.info("Operator created", operator_id=db_operator.id, name=operator.name)
        return db_operator
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Error creating operator", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating operator"
        )


@router.get("/{operator_id}", response_model=OperatorResponse)
async def get_operator(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """Get an operator by ID"""
    operator = db.query(Operator).filter(Operator.id == operator_id).first()
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operator not found"
        )
    return operator


@router.put("/{operator_id}", response_model=OperatorResponse)
async def update_operator(
    operator_id: int,
    operator_update: OperatorUpdate,
    db: Session = Depends(get_db)
):
    """Update an operator"""
    operator = db.query(Operator).filter(Operator.id == operator_id).first()
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operator not found"
        )
    
    update_data = operator_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(operator, field, value)
    
    db.commit()
    db.refresh(operator)
    return operator


@router.get("/", response_model=List[OperatorResponse])
async def list_operators(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all operators"""
    operators = db.query(Operator).limit(limit).offset(offset).all()
    return operators

