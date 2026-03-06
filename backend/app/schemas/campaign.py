"""
Campaign Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class CampaignBase(BaseModel):
    operator_id: Optional[int] = None  # Set from auth token when not provided
    name: str
    description: Optional[str] = None
    campaign_type: str  # email, sms, push, in_app, whatsapp
    trigger_type: str  # manual, event_based, scheduled, ai_optimized
    target_segment_id: Optional[int] = None
    template_id: Optional[int] = None
    schedule_config: Optional[Dict[str, Any]] = {}
    personalization_config: Optional[Dict[str, Any]] = {}


class CampaignCreate(CampaignBase):
    ai_objective: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    target_segment_id: Optional[int] = None
    schedule_config: Optional[Dict[str, Any]] = None
    personalization_config: Optional[Dict[str, Any]] = None


class CampaignResponse(CampaignBase):
    id: int
    status: str
    ai_generated: bool
    ai_objective: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

