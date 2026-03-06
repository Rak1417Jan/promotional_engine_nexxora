"""
Import/Export Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ImportJobCreate(BaseModel):
    """Import job creation schema"""
    entity_type: str = Field(..., description="Type of entity: game, player, payment_gateway, etc.")
    file_format: str = Field(..., pattern="^(csv|json|excel|xml)$")
    schema_id: Optional[int] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class ImportJobResponse(BaseModel):
    """Import job response schema"""
    id: int
    operator_id: int
    entity_type: str
    file_name: str
    file_format: str
    status: str
    total_records: Optional[int]
    processed_records: int
    failed_records: int
    error_log: List[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ExportJobCreate(BaseModel):
    """Export job creation schema"""
    entity_type: str
    export_format: str = Field(..., pattern="^(csv|json|excel)$")
    filters: Dict[str, Any] = Field(default_factory=dict)


class ExportJobResponse(BaseModel):
    """Export job response schema"""
    id: int
    operator_id: int
    entity_type: str
    export_format: str
    status: str
    file_path: Optional[str]
    total_records: Optional[int]
    file_size_bytes: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SchemaCreate(BaseModel):
    """Schema creation schema"""
    entity_type: str
    schema_name: str
    schema_definition: Dict[str, Any]
    is_default: bool = False


class SchemaResponse(BaseModel):
    """Schema response schema"""
    id: int
    operator_id: int
    entity_type: str
    schema_name: str
    schema_definition: Dict[str, Any]
    version: int
    is_active: bool
    is_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
