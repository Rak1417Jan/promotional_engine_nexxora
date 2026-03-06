"""
LLM Service - Supports OpenAI and Groq (Open Source LLMs)
"""
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.logger import logger
import json


class LLMService:
    """Unified LLM service supporting OpenAI and Groq"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.client = None
        
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "groq":
            self._init_groq()
        else:
            logger.warning(f"Unknown LLM provider: {self.provider}, defaulting to Groq")
            self.provider = "groq"
            self._init_groq()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            self.client = None
            return
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            self.client = None
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
            self.client = None
    
    def _init_groq(self):
        """Initialize Groq client (Free, Fast LLM)"""
        if not settings.GROQ_API_KEY:
            logger.warning("Groq API key not configured. Get free API key at: https://console.groq.com")
            self.client = None
            return
        
        try:
            from groq import Groq
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info("Groq client initialized")
        except ImportError:
            logger.error("Groq package not installed. Install with: pip install groq")
            self.client = None
        except Exception as e:
            logger.error(f"Groq initialization failed: {e}")
            self.client = None
    
    def _get_model(self) -> str:
        """Get the model name based on provider"""
        if self.provider == "openai":
            return settings.OPENAI_MODEL
        else:
            return settings.GROQ_MODEL
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate text using configured LLM provider"""
        if not self.client:
            logger.warning("LLM client not available, returning default response")
            return "LLM service not configured. Please set API key."
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            if self.provider == "openai":
                params = {
                    "model": self._get_model(),
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if response_format:
                    params["response_format"] = response_format
                
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content
            
            elif self.provider == "groq":
                # Groq API is similar to OpenAI
                params = {
                    "model": self._get_model(),
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating text with {self.provider}: {e}")
            return f"Error: {str(e)}"
    
    def generate_email_content(
        self,
        player_name: str,
        campaign_objective: str,
        player_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate personalized email content"""
        if not self.client:
            return {
                "subject": "Welcome to our platform!",
                "body": "Thank you for joining us!"
            }
        
        try:
            context_str = ""
            if player_context:
                context_str = f"\nPlayer Context: {json.dumps(player_context, indent=2)}"
            
            prompt = f"""Generate a personalized email for a player named {player_name}.
Campaign Objective: {campaign_objective}
{context_str}

Generate:
1. A compelling subject line (max 60 characters)
2. Email body (max 500 words) that is engaging and personalized

Format your response as:
SUBJECT: [subject line]
BODY: [email body]"""
            
            system_prompt = "You are an expert email marketing copywriter for iGaming platforms."
            content = self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            subject = ""
            body = ""
            
            if "SUBJECT:" in content:
                parts = content.split("SUBJECT:")
                if len(parts) > 1:
                    subject_part = parts[1].split("BODY:")[0].strip()
                    subject = subject_part
                    if "BODY:" in parts[1]:
                        body = parts[1].split("BODY:")[1].strip()
            else:
                # Fallback parsing
                lines = content.split("\n")
                subject = lines[0] if lines else "Welcome!"
                body = "\n".join(lines[1:]) if len(lines) > 1 else content
            
            return {
                "subject": subject[:60],
                "body": body[:2000]
            }
            
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            return {
                "subject": "Welcome to our platform!",
                "body": "Thank you for joining us!"
            }
    
    def generate_sms_content(
        self,
        player_name: str,
        campaign_objective: str,
        player_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate personalized SMS content"""
        if not self.client:
            return "Thank you for joining us!"
        
        try:
            context_str = ""
            if player_context:
                context_str = f"\nPlayer Context: {json.dumps(player_context, indent=2)}"
            
            prompt = f"""Generate a personalized SMS message for a player named {player_name}.
Campaign Objective: {campaign_objective}
{context_str}

Generate a short, engaging SMS message (max 160 characters)."""
            
            system_prompt = "You are an expert SMS marketing copywriter for iGaming platforms."
            content = self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=100
            )
            
            return content.strip()[:160]
            
        except Exception as e:
            logger.error(f"Error generating SMS content: {e}")
            return "Thank you for joining us!"
    
    def generate_campaign_from_objective(
        self,
        objective: str,
        operator_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate campaign configuration from natural language objective"""
        if not self.client:
            return {
                "name": "Generated Campaign",
                "description": objective,
                "campaign_type": "email"
            }
        
        try:
            context_str = ""
            if operator_context:
                context_str = f"\nOperator Context: {json.dumps(operator_context, indent=2)}"
            
            prompt = f"""Based on this campaign objective, generate a campaign configuration:
Objective: {objective}
{context_str}

Provide a JSON response with:
- name: Campaign name
- description: Campaign description
- campaign_type: email, sms, push, or whatsapp
- target_segment: Suggested target segment
- key_message: Key message for the campaign"""
            
            system_prompt = "You are an expert marketing campaign strategist for iGaming platforms. Always respond with valid JSON."
            
            # Request JSON format
            response_format = {"type": "json_object"} if self.provider == "openai" else None
            
            content = self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                response_format=response_format if response_format else None
            )
            
            # Parse JSON response
            try:
                if self.provider == "groq":
                    # Groq may return JSON in markdown code blocks
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                raise
            
        except Exception as e:
            logger.error(f"Error generating campaign from objective: {e}")
            return {
                "name": "Generated Campaign",
                "description": objective,
                "campaign_type": "email"
            }
    
    def generate_insight_summary(self, insights: Dict[str, Any]) -> str:
        """Generate natural language summary of insights"""
        if not self.client:
            return "Insights generated successfully."
        
        try:
            prompt = f"""Summarize these business insights in plain English (2-3 paragraphs):
{json.dumps(insights, indent=2)}

Provide a clear, actionable summary that an operator can understand."""
            
            system_prompt = "You are a business intelligence analyst for iGaming platforms. Explain insights clearly and concisely."
            
            summary = self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=500
            )
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating insight summary: {e}")
            return "Insights generated successfully."
