"""
Operator Model
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Operator(Base):
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain_url = Column(String(255), unique=True, index=True)
    contact_email = Column(String(255))
    theme_config = Column(JSON, default=dict)
    catalog_selection = Column(JSON, default=dict)
    commission_rate = Column(Numeric(5, 4), default=0)
    pg_fee_rate = Column(Numeric(5, 4), default=0)
    provider_fee_rate = Column(Numeric(5, 4), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

