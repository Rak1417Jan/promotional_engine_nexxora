"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class OperatorRegister(BaseModel):
    """Operator registration (creates operator + first owner user) - Phase 1"""
    name: str = Field(..., min_length=1, description="Company/operator name")
    domain_url: str = Field(..., min_length=1, description="Unique domain URL")
    contact_email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserRegister(BaseModel):
    """User registration schema (add user to existing operator)"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = Field(default="analyst", pattern="^(owner|admin|manager|analyst)$")


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    operator_id: int
    mfa_enabled: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset schema"""
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str = Field(..., min_length=8)
