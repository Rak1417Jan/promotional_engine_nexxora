"""
ML Model Model
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(100), nullable=False, index=True)  # churn, ltv, propensity, recommendation
    model_name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)  # NULL for global models
    model_path = Column(String(500))
    hyperparameters = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)  # accuracy, precision, recall, AUC, etc.
    training_data_range_start = Column(DateTime(timezone=True))
    training_data_range_end = Column(DateTime(timezone=True))
    status = Column(String(50), default="training", index=True)  # training, active, deprecated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    operator = relationship("Operator", backref="ml_models")
    
    # Indexes
    __table_args__ = (
        Index("idx_type_status", "model_type", "status"),
    )

