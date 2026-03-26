"""
Prediction Model
"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Numeric, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey("players.id"), nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    prediction_type = Column(String(100), nullable=False, index=True)  # churn_risk, ltv, next_deposit, game_preference
    prediction_value = Column(Numeric(15, 4), nullable=False)
    confidence_score = Column(Numeric(5, 4))
    model_id = Column(Integer, ForeignKey("ml_models.id"))
    features_used = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    player = relationship("Player", backref="predictions")
    operator = relationship("Operator", backref="predictions")
    model = relationship("MLModel", backref="predictions")
    
    # Indexes
    __table_args__ = (
        Index("idx_preds_player_type", "player_id", "prediction_type"),
        Index("idx_preds_operator", "operator_id", "prediction_type"),
    )

