"""
Campaign Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(50), nullable=False)  # email, sms, push, in_app, whatsapp
    status = Column(String(50), default="draft", index=True)  # draft, scheduled, active, paused, completed
    trigger_type = Column(String(50), nullable=False)  # manual, event_based, scheduled, ai_optimized
    target_segment_id = Column(Integer, ForeignKey("segments.id"))
    template_id = Column(Integer)
    ai_generated = Column(Boolean, default=False)
    ai_objective = Column(Text)  # Natural language objective for AI campaigns
    schedule_config = Column(JSON, default=dict)
    personalization_config = Column(JSON, default=dict)
    created_by = Column(Integer)  # User ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    operator = relationship("Operator", backref="campaigns")
    target_segment = relationship("Segment", backref="campaigns")
    
    # Indexes
    __table_args__ = (
        Index("idx_operator_status", "operator_id", "status"),
    )

