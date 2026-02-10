"""
Configuration Management - All settings from environment variables.
Never commit secrets. Never hardcode configuration.
"""

import os
from pathlib import Path
from typing import Optional
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field, field_validator
    ConfigDict = SettingsConfigDict
except ImportError:
    try:
        from pydantic import BaseSettings, Field, validator
        field_validator = validator
        ConfigDict = None
    except ImportError:
        # Fallback to even older versions if necessary
        raise


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    CRITICAL RULE: If it's configuration, it comes from env vars.
    If it's a secret, it's in a secure vault.
    If it's neither, it's in code.
    """
    
    # Core Settings
    APP_NAME: str = "MLJ Results Compiler"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False
    ENV: str = "development"  # development, staging, production
    
    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "sqlite:///data/sessions.db"  # SQLite default
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Telegram Bot (REQUIRED if using bot)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    WEBHOOK_BASE_URL: Optional[str] = None
    
    # Groq AI (OPTIONAL - set to enable AI features)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GROQ_TIMEOUT: int = 30
    
    # Feature Flags
    ENABLE_AI_ASSISTANT: bool = False  # Set True if GROQ_API_KEY is set
    ENABLE_TELEGRAM_BOT: bool = False  # Set True if TELEGRAM_BOT_TOKEN is set
    
    # File Uploads
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: Path = Path("temp_uploads")
    OUTPUT_DIR: Path = Path("output")
    
    # Session Management
    SESSION_TIMEOUT: int = 3600  # 1 hour
    CLEANUP_INTERVAL: int = 3600  # 1 hour
    
    # Performance
    WORKERS: int = 4
    RELOAD: bool = False
    
    # Pydantic v2 configuration (preferred)
    try:
        model_config = ConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True
        )
    except NameError:
        # Fallback for Pydantic v1 (when ConfigDict is not available)
        class Config:
            """Pydantic v1 config (fallback)"""
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = True
    
    @field_validator("ENABLE_AI_ASSISTANT", mode="before")
    @classmethod
    def set_ai_enabled(cls, v, info):
        """Enable AI if API key is set"""
        values = info.data if hasattr(info, 'data') else info.values if hasattr(info, 'values') else {}
        return bool(values.get("GROQ_API_KEY"))
    
    @field_validator("ENABLE_TELEGRAM_BOT", mode="before")
    @classmethod
    def set_telegram_enabled(cls, v, info):
        """Enable bot if token is set"""
        values = info.data if hasattr(info, 'data') else info.values if hasattr(info, 'values') else {}
        return bool(values.get("TELEGRAM_BOT_TOKEN"))
    
    @field_validator("ENV")
    @classmethod
    def validate_env(cls, v):
        """Validate environment"""
        valid = ["development", "staging", "production"]
        if v not in valid:
            raise ValueError(f"ENV must be one of {valid}")
        return v
    
    def __init__(self, **data):
        """Initialize settings and validate required fields for production"""
        super().__init__(**data)
        
        # Validate production requirements
        if self.ENV == "production":
            if not self.TELEGRAM_BOT_TOKEN:
                raise ValueError("TELEGRAM_BOT_TOKEN required for production")
            if not self.WEBHOOK_BASE_URL:
                raise ValueError("WEBHOOK_BASE_URL required for production")
            if not self.DATABASE_URL.startswith("postgresql://"):
                raise ValueError("PostgreSQL required for production (not SQLite)")
        
        # Create directories
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings singleton"""
    global settings
    if settings is None:
        settings = Settings()
    return settings


def validate_settings():
    """Validate settings at startup (fail fast)"""
    s = get_settings()
    
    errors = []
    
    # Check required settings
    if s.ENABLE_TELEGRAM_BOT and not s.TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN not set but bot enabled")
    
    if s.ENABLE_TELEGRAM_BOT and not s.WEBHOOK_BASE_URL:
        errors.append("WEBHOOK_BASE_URL not set but bot enabled")
    
    if s.ENABLE_AI_ASSISTANT and not s.GROQ_API_KEY:
        errors.append("GROQ_API_KEY not set but AI enabled")
    
    if errors:
        error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        raise RuntimeError(error_msg)
    
    return True


# Usage:
# from config.settings import get_settings
# settings = get_settings()
# 
# print(settings.DATABASE_URL)
# print(settings.TELEGRAM_BOT_TOKEN)  # Will be None if not set
