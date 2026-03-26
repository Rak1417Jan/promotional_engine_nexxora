"""
Event Model
"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Event(Base):
    __tablename__ = "events"
    
    id = Column(BigInteger, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey("players.id"), nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # registration, deposit, bet, withdrawal, etc.
    event_data = Column(JSON, default=dict)
    source_utm = Column(String(255), index=True)
    medium_utm = Column(String(255), index=True)
    campaign_utm = Column(String(255), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    player = relationship("Player", backref="events")
    operator = relationship("Operator", backref="events")
    
    # Indexes
    __table_args__ = (
        Index("idx_events_player_time", "player_id", "timestamp"),
        Index("idx_events_operator_type", "operator_id", "event_type", "timestamp"),
        Index("idx_events_utm", "source_utm", "medium_utm", "campaign_utm"),
    )

