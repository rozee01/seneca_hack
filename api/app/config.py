"""
Configuration management for the API.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "sparkuser"
    POSTGRES_PASSWORD: str = "sparkpass"
    POSTGRES_DB: str = "sparkdb"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "sentiment-api-group"
    KAFKA_TOPIC_SENTIMENT: str = "sentiment_analysis"
    KAFKA_TOPIC_RAW: str = "raw_social_media"
    
    # Optional additional settings
    EXTERNAL_API_ENABLED: Optional[bool] = False
    EXTERNAL_API_REQUIRE_AUTH: Optional[bool] = False
    WEBSOCKET_ENABLED: Optional[bool] = False
    WEBSOCKET_MAX_CONNECTIONS: Optional[int] = 1000
    BACKEND_CORS_ORIGINS: Optional[str] = '["http://localhost:3000", "http://localhost:8080"]'
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
