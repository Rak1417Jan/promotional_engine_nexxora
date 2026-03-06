"""
Operator Schema Registry Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class OperatorSchema(Base):
    __tablename__ = "operator_schemas"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)  # 'game', 'player', 'payment_gateway', etc.
    schema_name = Column(String(255), nullable=False)
    schema_definition = Column(JSON, nullable=False)  # Field definitions, types, constraints
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Default schema for entity type
    created_by = Column(Integer, ForeignKey("operator_users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    operator = relationship("Operator", backref="schemas")
    creator = relationship("OperatorUser", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index("idx_operator_entity", "operator_id", "entity_type"),
        Index("idx_active_schema", "operator_id", "entity_type", "is_active"),
        Index("idx_default_schema", "operator_id", "entity_type", "is_default"),
    )
