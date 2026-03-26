"""
Campaign Execution Model
"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CampaignExecution(Base):
    __tablename__ = "campaign_executions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    campaign_id = Column(BigInteger, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(String(255), nullable=False)  # External player ID (from MongoDB)
    channel = Column(String(50), nullable=False)  # email, sms, push, whatsapp
    status = Column(String(50), default="pending", index=True)  # pending, sent, delivered, opened, clicked, converted, failed
    message_data = Column(JSON, nullable=False)  # Personalized message content
    delivery_metadata = Column(JSON, default=dict)  # Provider response, timestamps
    sent_at = Column(DateTime(timezone=True), index=True)
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("Campaign", backref="executions")
    operator = relationship("Operator", backref="campaign_executions")
    
    # Indexes
    __table_args__ = (
        Index("idx_campaign_exec_campaign_status", "campaign_id", "status"),
        Index("idx_campaign_exec_operator_player", "operator_id", "player_id"),
        Index("idx_campaign_exec_sent_at", "sent_at"),
    )

