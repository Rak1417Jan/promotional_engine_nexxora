"""
SMS Service using Twilio
"""
from twilio.rest import Client
from typing import Optional
from app.config import settings
from app.utils.logger import logger


class SMSService:
    """Service for sending SMS via Twilio"""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get Twilio client (singleton)"""
        if cls._client is None and settings.ENABLE_SMS and settings.TWILIO_ACCOUNT_SID:
            try:
                cls._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                logger.info("Twilio client initialized")
            except Exception as e:
                logger.error(f"Twilio initialization failed: {e}")
        return cls._client
    
    @classmethod
    def send_sms(
        cls,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> Optional[str]:
        """Send an SMS"""
        if not settings.ENABLE_SMS:
            logger.warning("SMS sending is disabled")
            return None
        
        client = cls.get_client()
        if not client:
            logger.error("Twilio client not available")
            return None
        
        try:
            from_number = from_phone or settings.TWILIO_PHONE_NUMBER
            
            message_obj = client.messages.create(
                body=message,
                from_=from_number,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully", to=to_phone, sid=message_obj.sid)
            return message_obj.sid
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return None
    
    @classmethod
    def send_whatsapp(
        cls,
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> Optional[str]:
        """Send a WhatsApp message"""
        if not settings.ENABLE_SMS:
            return None
        
        client = cls.get_client()
        if not client:
            return None
        
        try:
            from_number = from_phone or settings.TWILIO_WHATSAPP_NUMBER
            to_number = f"whatsapp:{to_phone}" if not to_phone.startswith("whatsapp:") else to_phone
            
            message_obj = client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            
            logger.info(f"WhatsApp sent successfully", to=to_phone, sid=message_obj.sid)
            return message_obj.sid
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {e}")
            return None
