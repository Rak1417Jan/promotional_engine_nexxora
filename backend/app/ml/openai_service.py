"""
OpenAI Service for Content Generation
DEPRECATED: Use LLMService instead (supports OpenAI and Groq)
This file is kept for backward compatibility
"""
from typing import Optional, Dict, Any, List
from app.ml.llm_service import LLMService
from app.config import settings
from app.utils.logger import logger

# Create LLM service instance
_llm_service = LLMService()


class OpenAIService:
    """Service for LLM integration (OpenAI or Groq)
    DEPRECATED: Use LLMService directly for new code
    This class wraps LLMService for backward compatibility
    """
    
    def __init__(self):
        # Use the shared LLM service
        self.llm_service = _llm_service
        self.client = _llm_service.client  # For backward compatibility
    
    def generate_email_content(
        self,
        player_name: str,
        campaign_objective: str,
        player_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate personalized email content"""
        return self.llm_service.generate_email_content(
            player_name=player_name,
            campaign_objective=campaign_objective,
            player_context=player_context
        )
    
    def generate_sms_content(
        self,
        player_name: str,
        campaign_objective: str,
        player_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate personalized SMS content"""
        return self.llm_service.generate_sms_content(
            player_name=player_name,
            campaign_objective=campaign_objective,
            player_context=player_context
        )
    
    def generate_campaign_from_objective(
        self,
        objective: str,
        operator_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate campaign configuration from natural language objective"""
        return self.llm_service.generate_campaign_from_objective(
            objective=objective,
            operator_context=operator_context
        )
    
    def generate_insight_summary(self, insights: Dict[str, Any]) -> str:
        """Generate natural language summary of insights"""
        return self.llm_service.generate_insight_summary(insights)

