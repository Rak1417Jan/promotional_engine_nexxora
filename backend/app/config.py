"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from typing import List
import os
from dotenv import load_dotenv
import json

load_dotenv()


def _parse_cors_origins(value: str) -> List[str]:
    """Parse CORS_ORIGINS from env: comma-separated string or JSON array."""
    if not value or not value.strip():
        return ["*"]
    s = value.strip()
    try:
        parsed = json.loads(s)
        return list(parsed) if isinstance(parsed, list) else [s]
    except json.JSONDecodeError:
        return [origin.strip() for origin in s.split(",") if origin.strip()] or ["*"]


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Promotional Marketing Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    # Default uses current username for macOS Homebrew PostgreSQL
    _default_db_user = os.getenv("USER", "postgres")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{_default_db_user}@localhost:5432/promotional_engine"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/nexora_attributes")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "nexora_attributes")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")  # "openai" or "groq"
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Groq (Free, Fast LLM)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")  # or "llama-3.1-8b-instant", "mixtral-8x7b-32768"
    
    # Email (SendGrid)
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "noreply@example.com")
    SENDGRID_FROM_NAME: str = os.getenv("SENDGRID_FROM_NAME", "Promotional Engine")
    
    # SMS (Twilio)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_CLIENT_ID: str = os.getenv("KAFKA_CLIENT_ID", "promotional_engine")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "promotional_engine_group")
    
    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "promotional-engine-uploads")
    MINIO_USE_SSL: bool = os.getenv("MINIO_USE_SSL", "False").lower() == "true"
    
    # Performance
    MAX_WORKERS: int = 4
    API_RATE_LIMIT: int = 1000
    
    # Feature Flags
    ENABLE_ML_MODELS: bool = os.getenv("ENABLE_ML_MODELS", "True").lower() == "true"
    ENABLE_OPENAI: bool = os.getenv("ENABLE_OPENAI", "True").lower() == "true"
    ENABLE_EMAIL: bool = os.getenv("ENABLE_EMAIL", "True").lower() == "true"
    ENABLE_SMS: bool = os.getenv("ENABLE_SMS", "True").lower() == "true"
    
    # CORS: read as string from env (comma-separated or JSON), exposed as list via computed field
    cors_origins_raw: str = Field(default="*", validation_alias="CORS_ORIGINS")

    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return _parse_cors_origins(self.cors_origins_raw)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_ignore_empty": True,
        "extra": "ignore",
    }


settings = Settings()

