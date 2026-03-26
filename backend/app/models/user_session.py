"""
User Session Model
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("operator_users.id", ondelete="CASCADE"), nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    refresh_token_hash = Column(String(255), index=True)
    ip_address = Column(INET)
    user_agent = Column(Text)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("OperatorUser", backref="sessions")
    operator = relationship("Operator", backref="sessions")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_sess_token", "token_hash"),
        Index("idx_user_sess_refresh", "refresh_token_hash"),
        Index("idx_user_sess_expires", "expires_at"),
    )
