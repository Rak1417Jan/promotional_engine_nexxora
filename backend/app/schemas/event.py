"""
Event Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EventCreate(BaseModel):
    player_id: int
    operator_id: int
    event_type: str  # registration, deposit, bet, withdrawal, game_play, etc.
    event_data: Optional[Dict[str, Any]] = {}
    source_utm: Optional[str] = None
    medium_utm: Optional[str] = None
    campaign_utm: Optional[str] = None
    timestamp: Optional[datetime] = None


class EventResponse(BaseModel):
    id: int
    player_id: int
    operator_id: int
    event_type: str
    event_data: Dict[str, Any]
    source_utm: Optional[str] = None
    medium_utm: Optional[str] = None
    campaign_utm: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

