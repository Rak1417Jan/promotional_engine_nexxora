"""
Import Job Model
"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)  # 'game', 'player', 'payment_gateway', etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)  # S3/MinIO path
    file_format = Column(String(50), nullable=False)  # csv, json, excel, xml
    schema_id = Column(Integer, ForeignKey("operator_schemas.id"))
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    total_records = Column(Integer)
    processed_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    error_log = Column(JSON, default=list)
    config = Column(JSON, default=dict)  # Import configuration
    created_by = Column(Integer, ForeignKey("operator_users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    operator = relationship("Operator", backref="import_jobs")
    schema = relationship("OperatorSchema", foreign_keys=[schema_id])
    creator = relationship("OperatorUser", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index("idx_import_jobs_operator_status", "operator_id", "status"),
        Index("idx_import_jobs_entity_type", "operator_id", "entity_type"),
    )
