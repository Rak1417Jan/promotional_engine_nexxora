"""
Export Job Model
"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    export_format = Column(String(50), nullable=False)  # csv, json, excel
    filters = Column(JSON, default=dict)  # Export filters
    file_path = Column(Text)  # S3/MinIO path (after completion)
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    total_records = Column(Integer)
    file_size_bytes = Column(BigInteger)
    expires_at = Column(DateTime(timezone=True))  # File retention
    created_by = Column(Integer, ForeignKey("operator_users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    operator = relationship("Operator", backref="export_jobs")
    creator = relationship("OperatorUser", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index("idx_export_jobs_operator_status", "operator_id", "status"),
        Index("idx_export_jobs_entity_type", "operator_id", "entity_type"),
    )
