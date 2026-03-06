"""
Segment Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Segment(Base):
    __tablename__ = "segments"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    segment_type = Column(String(50), nullable=False)  # rfm, behavioral, predictive, custom
    criteria = Column(JSON, default=dict)  # Dynamic criteria definition
    player_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    operator = relationship("Operator", backref="segments")
    
    # Indexes
    __table_args__ = (
        Index("idx_operator", "operator_id"),
    )

