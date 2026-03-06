"""
Player Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PlayerBase(BaseModel):
    operator_id: Optional[int] = None  # Set from auth when omitted
    external_player_id: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class PlayerCreate(PlayerBase):
    registration_date: Optional[datetime] = None


class PlayerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    last_active_date: Optional[datetime] = None
    status: Optional[str] = None
    segment_id: Optional[int] = None


class PlayerResponse(PlayerBase):
    id: int
    registration_date: Optional[datetime] = None
    last_active_date: Optional[datetime] = None
    status: str
    total_deposits: Decimal
    total_withdrawals: Decimal
    total_bets: Decimal
    lifetime_value: Decimal
    churn_risk_score: Optional[Decimal] = None
    ltv_prediction: Optional[Decimal] = None
    segment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedPlayersResponse(BaseModel):
    items: List["PlayerResponse"]
    total: int
    limit: int
    offset: int

