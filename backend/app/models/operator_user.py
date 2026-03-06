"""
Operator User Model (Authentication)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class OperatorUser(Base):
    __tablename__ = "operator_users"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), nullable=False, default="analyst")  # owner, admin, manager, analyst
    permissions = Column(JSON, default=dict)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    
    # Relationships
    operator = relationship("Operator", backref="users")
    
    # Indexes
    __table_args__ = (
        Index("idx_operator_email", "operator_id", "email", unique=True),
        Index("idx_email", "email"),
        Index("idx_role", "operator_id", "role"),
    )
