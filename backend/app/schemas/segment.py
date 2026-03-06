"""
Segment Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class SegmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    segment_type: str = "custom"  # rfm, behavioral, predictive, custom
    criteria: Optional[Dict[str, Any]] = None


class SegmentCreate(SegmentBase):
    pass


class SegmentResponse(SegmentBase):
    id: int
    operator_id: int
    player_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
