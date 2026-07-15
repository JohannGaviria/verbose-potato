"""This module contains the application configuration settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application metadata
    APP_NAME: str = Field(..., validation_alias="APP_NAME")
    APP_SUMMARY: str = Field(..., validation_alias="APP_SUMMARY")
    APP_DESCRIPTION: str = Field(..., validation_alias="APP_DESCRIPTION")
    APP_VERSION: str = Field(..., validation_alias="APP_VERSION")

    # Backend configuration
    DEBUG: bool = Field(..., validation_alias="DEBUG")
    ENVIRONMENT: str = Field(..., validation_alias="ENVIRONMENT")
    BACKEND_PORT: int = Field(..., validation_alias="BACKEND_PORT")
    BACKEND_WORKERS: int = Field(..., validation_alias="BACKEND_WORKERS")
    CORS_ALLOW_ORIGINS: str = Field(..., validation_alias="CORS_ALLOW_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = Field(..., validation_alias="CORS_ALLOW_CREDENTIALS")

    # PostgreSQL configuration
    POSTGRES_USER: str = Field(..., validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., validation_alias="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., validation_alias="POSTGRES_DB")
    POSTGRES_PORT: int = Field(..., validation_alias="POSTGRES_PORT")

    # Database configuration
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    DATABASE_URL_ALEMBIC: str = Field(..., validation_alias="DATABASE_URL_ALEMBIC")
    DB_POOL_SIZE: int = Field(..., validation_alias="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(..., validation_alias="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(..., validation_alias="DB_POOL_TIMEOUT")
    DB_ECHO: bool = Field(..., validation_alias="DB_ECHO")

    # Redis configuration
    REDIS_URL: str = Field(..., validation_alias="REDIS_URL")
    REDIS_DB: int = Field(..., validation_alias="REDIS_DB")
    REDIS_HOST: str = Field(..., validation_alias="REDIS_HOST")
    REDIS_PASSWORD: str = Field(..., validation_alias="REDIS_PASSWORD")
    REDIS_PORT: int = Field(..., validation_alias="REDIS_PORT")
    REDIS_MAX_CONNECTIONS: int = Field(..., validation_alias="REDIS_MAX_CONNECTIONS")
    REDIS_DECODE_RESPONSES: bool = Field(..., validation_alias="REDIS_DECODE_RESPONSES")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: The application settings instance.
    """
    settings = Settings()  # type: ignore[call-arg]
    return settings


settings = get_settings()
