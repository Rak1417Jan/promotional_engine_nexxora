"""
Email Service using SendGrid
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logger import logger


class EmailService:
    """Service for sending emails via SendGrid"""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get SendGrid client (singleton)"""
        if cls._client is None and settings.ENABLE_EMAIL and settings.SENDGRID_API_KEY:
            try:
                cls._client = SendGridAPIClient(settings.SENDGRID_API_KEY)
                logger.info("SendGrid client initialized")
            except Exception as e:
                logger.error(f"SendGrid initialization failed: {e}")
        return cls._client
    
    @classmethod
    def send_email(
        cls,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """Send an email"""
        if not settings.ENABLE_EMAIL:
            logger.warning("Email sending is disabled")
            return False
        
        client = cls.get_client()
        if not client:
            logger.error("SendGrid client not available")
            return False
        
        try:
            from_addr = from_email or settings.SENDGRID_FROM_EMAIL
            from_name_val = from_name or settings.SENDGRID_FROM_NAME
            
            message = Mail(
                from_email=(from_addr, from_name_val),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            if text_content:
                message.plain_text_content = text_content
            
            response = client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully", to=to_email, status=response.status_code)
                return True
            else:
                logger.error(f"Email send failed", to=to_email, status=response.status_code)
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    @classmethod
    def send_template_email(
        cls,
        to_email: str,
        template_id: str,
        template_data: Dict[str, Any],
        from_email: Optional[str] = None
    ) -> bool:
        """Send email using SendGrid template"""
        if not settings.ENABLE_EMAIL:
            return False
        
        client = cls.get_client()
        if not client:
            return False
        
        try:
            from_addr = from_email or settings.SENDGRID_FROM_EMAIL
            
            message = Mail(
                from_email=from_addr,
                to_emails=to_email
            )
            message.template_id = template_id
            message.dynamic_template_data = template_data
            
            response = client.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"Error sending template email: {e}")
            return False
