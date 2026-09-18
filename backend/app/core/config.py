from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Threat Detection Platform"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-change-me"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./threat_platform.db"
    AUTO_CREATE_TABLES: bool = True

    # Database pooling options (PostgreSQL)
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 300

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = ""

    FIRST_ADMIN_EMAIL: str = "admin@threatplatform.dev"
    FIRST_ADMIN_PASSWORD: str = "Admin@12345"

    DETECTION_CONTENT_PATH: str = "../detection-content"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:4173,https://pravallika2025.github.io"

    ENABLE_BACKGROUND_SCHEDULER: bool = True
    SCHEDULER_INTERVAL_SECONDS: int = 60

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY in ("dev-secret-change-me", "", "change-this-in-production"):
                raise ValueError(
                    "SECRET_KEY must be set to a cryptographically secure value in production."
                )
            if self.FIRST_ADMIN_PASSWORD in ("Admin@12345", "password", "admin"):
                raise ValueError(
                    "Default seed password must be changed prior to production deployment."
                )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def detection_content_dir(self) -> Path:
        return Path(self.DETECTION_CONTENT_PATH).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

