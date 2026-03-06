"""
Recommendation Model
"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Numeric, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(BigInteger, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey("players.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    recommendation_type = Column(String(100), nullable=False, index=True)  # next_best_action, game, bonus, content
    recommended_item = Column(String(255), nullable=False)
    score = Column(Numeric(5, 4), nullable=False)
    reasoning = Column(Text)  # AI-generated explanation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    player = relationship("Player", backref="recommendations")
    operator = relationship("Operator", backref="recommendations")
    
    # Indexes
    __table_args__ = (
        Index("idx_player", "player_id", "recommendation_type"),
        Index("idx_operator", "operator_id"),
    )

