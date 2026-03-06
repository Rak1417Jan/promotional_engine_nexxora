"""
Player Model
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Player(Base):
    __tablename__ = "players"
    
    id = Column(BigInteger, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    external_player_id = Column(String(255), index=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    registration_date = Column(DateTime(timezone=True))
    last_active_date = Column(DateTime(timezone=True))
    status = Column(String(50), default="new")  # new, active, inactive, churned
    total_deposits = Column(Numeric(15, 2), default=0)
    total_withdrawals = Column(Numeric(15, 2), default=0)
    total_bets = Column(Numeric(15, 2), default=0)
    lifetime_value = Column(Numeric(15, 2), default=0)
    churn_risk_score = Column(Numeric(5, 4))
    ltv_prediction = Column(Numeric(15, 2))
    segment_id = Column(Integer, ForeignKey("segments.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    operator = relationship("Operator", backref="players")
    segment = relationship("Segment", backref="players")
    
    # Indexes
    __table_args__ = (
        Index("idx_operator_player", "operator_id", "external_player_id"),
        Index("idx_status", "status"),
        Index("idx_segment", "segment_id"),
    )

