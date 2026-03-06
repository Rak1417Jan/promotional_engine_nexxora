"""
Operator Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class OperatorBase(BaseModel):
    name: str
    domain_url: str
    contact_email: Optional[EmailStr] = None
    theme_config: Optional[Dict[str, Any]] = {}
    catalog_selection: Optional[Dict[str, Any]] = {}
    commission_rate: Optional[Decimal] = Decimal("0")
    pg_fee_rate: Optional[Decimal] = Decimal("0")
    provider_fee_rate: Optional[Decimal] = Decimal("0")


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    domain_url: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    theme_config: Optional[Dict[str, Any]] = None
    catalog_selection: Optional[Dict[str, Any]] = None
    commission_rate: Optional[Decimal] = None
    pg_fee_rate: Optional[Decimal] = None
    provider_fee_rate: Optional[Decimal] = None


class OperatorResponse(OperatorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

