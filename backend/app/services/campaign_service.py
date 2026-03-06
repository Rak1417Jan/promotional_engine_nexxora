"""
Campaign Service
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from jinja2 import Template
from app.models.campaign import Campaign
from app.models.campaign_execution import CampaignExecution
from app.models.player import Player
from app.models.segment import Segment
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.utils.logger import logger


class CampaignService:
    """Service for campaign management and execution"""
    
    @staticmethod
    def create_campaign(
        db: Session,
        campaign_data: Dict[str, Any],
        operator_id: int,
        created_by: Optional[int] = None
    ) -> Campaign:
        """Create a new campaign"""
        campaign = Campaign(
            operator_id=operator_id,
            name=campaign_data.get("name"),
            description=campaign_data.get("description"),
            campaign_type=campaign_data.get("campaign_type"),
            trigger_type=campaign_data.get("trigger_type", "manual"),
            target_segment_id=campaign_data.get("target_segment_id"),
            template_id=campaign_data.get("template_id"),
            schedule_config=campaign_data.get("schedule_config", {}),
            personalization_config=campaign_data.get("personalization_config", {}),
            ai_generated=campaign_data.get("ai_generated", False),
            ai_objective=campaign_data.get("ai_objective"),
            created_by=created_by,
            status="draft"
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign
    
    @staticmethod
    def get_campaign_targets(
        db: Session,
        campaign_id: int
    ) -> List[Player]:
        """Get target players for a campaign"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return []
        
        if campaign.target_segment_id:
            # Get players from segment
            segment = db.query(Segment).filter(Segment.id == campaign.target_segment_id).first()
            if segment:
                # Apply segment criteria (simplified - full implementation would parse criteria)
                players = db.query(Player).filter(
                    Player.operator_id == campaign.operator_id,
                    Player.segment_id == campaign.target_segment_id
                ).all()
                return players
        
        # If no segment, return all players for operator (not recommended for large datasets)
        return db.query(Player).filter(
            Player.operator_id == campaign.operator_id
        ).limit(10000).all()  # Safety limit
    
    @staticmethod
    def execute_campaign(
        db: Session,
        campaign_id: int
    ) -> int:
        """Execute a campaign - create execution records and send messages"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign.status not in ("active", "draft"):
            raise ValueError("Campaign cannot be executed in its current state")
        if campaign.status == "draft":
            campaign.status = "active"
            db.commit()
            db.refresh(campaign)

        targets = CampaignService.get_campaign_targets(db, campaign_id)
        execution_count = 0
        sent_count = 0
        
        for player in targets:
            # Personalize message
            personalized_content = CampaignService._personalize_message(
                campaign, player
            )
            
            # Create execution record
            execution = CampaignExecution(
                campaign_id=campaign_id,
                operator_id=campaign.operator_id,
                player_id=str(player.external_player_id) if hasattr(player, 'external_player_id') else str(player.id),
                channel=campaign.campaign_type,
                status="pending",
                message_data=personalized_content
            )
            db.add(execution)
            db.flush()  # Get execution ID
            
            # Send message based on channel
            try:
                success = CampaignService._send_message(
                    campaign, player, personalized_content, execution.id
                )
                
                if success:
                    execution.status = "sent"
                    execution.sent_at = datetime.utcnow()
                    sent_count += 1
                else:
                    execution.status = "failed"
                    execution.delivery_metadata = {"error": "Failed to send message"}
            except Exception as e:
                logger.error(f"Error sending message: {e}", execution_id=execution.id)
                execution.status = "failed"
                execution.delivery_metadata = {"error": str(e)}
            
            execution_count += 1
        
        db.commit()
        logger.info(
            "Campaign execution completed",
            campaign_id=campaign_id,
            total=execution_count,
            sent=sent_count
        )
        return execution_count
    
    @staticmethod
    def _personalize_message(
        campaign: Campaign,
        player: Player
    ) -> Dict[str, Any]:
        """Personalize message content for a player"""
        config = campaign.personalization_config or {}
        template = config.get("template", "Hello {{first_name}}, {{message}}")
        
        # Get player data for personalization
        player_data = {
            "first_name": getattr(player, 'first_name', 'Player'),
            "last_name": getattr(player, 'last_name', ''),
            "email": getattr(player, 'email', ''),
            "message": campaign.description or "Thank you for being with us!"
        }
        
        # Render template
        jinja_template = Template(template)
        personalized_text = jinja_template.render(**player_data)
        
        return {
            "subject": config.get("subject", campaign.name),
            "body": personalized_text,
            "player_data": player_data
        }
    
    @staticmethod
    def _send_message(
        campaign: Campaign,
        player: Player,
        content: Dict[str, Any],
        execution_id: int
    ) -> bool:
        """Send message via appropriate channel"""
        channel = campaign.campaign_type
        
        if channel == "email":
            email = getattr(player, 'email', None)
            if not email:
                logger.warning(f"No email for player {player.id}")
                return False
            
            return EmailService.send_email(
                to_email=email,
                subject=content.get("subject", campaign.name),
                html_content=content.get("body", ""),
                text_content=content.get("body", "")
            )
        
        elif channel == "sms":
            phone = getattr(player, 'phone', None)
            if not phone:
                logger.warning(f"No phone for player {player.id}")
                return False
            
            message_id = SMSService.send_sms(
                to_phone=phone,
                message=content.get("body", "")
            )
            return message_id is not None
        
        elif channel == "whatsapp":
            phone = getattr(player, 'phone', None)
            if not phone:
                return False
            
            message_id = SMSService.send_whatsapp(
                to_phone=phone,
                message=content.get("body", "")
            )
            return message_id is not None
        
        else:
            logger.warning(f"Unsupported channel: {channel}")
            return False
    
    @staticmethod
    def update_execution_status(
        db: Session,
        execution_id: int,
        status: str,
        **kwargs
    ) -> CampaignExecution:
        """Update campaign execution status"""
        execution = db.query(CampaignExecution).filter(
            CampaignExecution.id == execution_id
        ).first()
        
        if not execution:
            raise ValueError("Execution not found")
        
        execution.status = status
        
        if status == "sent" and "sent_at" in kwargs:
            execution.sent_at = kwargs["sent_at"]
        elif status == "delivered" and "delivered_at" in kwargs:
            execution.delivered_at = kwargs["delivered_at"]
        elif status == "opened" and "opened_at" in kwargs:
            execution.opened_at = kwargs["opened_at"]
        elif status == "clicked" and "clicked_at" in kwargs:
            execution.clicked_at = kwargs["clicked_at"]
        elif status == "converted" and "converted_at" in kwargs:
            execution.converted_at = kwargs["converted_at"]
        elif status == "failed":
            error_msg = kwargs.get("error_message", "Unknown error")
            execution.delivery_metadata = execution.delivery_metadata or {}
            execution.delivery_metadata["error"] = error_msg
        
        db.commit()
        db.refresh(execution)
        return execution
    
    @staticmethod
    def get_campaign_analytics(
        db: Session,
        campaign_id: int
    ) -> Dict[str, Any]:
        """Get campaign analytics"""
        executions = db.query(CampaignExecution).filter(
            CampaignExecution.campaign_id == campaign_id
        ).all()
        
        total = len(executions)
        sent = len([e for e in executions if e.status == "sent"])
        delivered = len([e for e in executions if e.delivered_at is not None])
        opened = len([e for e in executions if e.opened_at is not None])
        clicked = len([e for e in executions if e.clicked_at is not None])
        converted = len([e for e in executions if e.clicked_at is not None])  # Simplified
        
        return {
            "campaign_id": campaign_id,
            "metrics": {
                "total": total,
                "sent": sent,
                "delivered": delivered,
                "opened": opened,
                "clicked": clicked,
                "converted": converted
            },
            "rates": {
                "delivery_rate": delivered / sent if sent > 0 else 0,
                "open_rate": opened / delivered if delivered > 0 else 0,
                "click_rate": clicked / opened if opened > 0 else 0,
                "conversion_rate": converted / clicked if clicked > 0 else 0
            }
        }

