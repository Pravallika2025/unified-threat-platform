from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Threat Detection Platform"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-change-me"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./threat_platform.db"
    AUTO_CREATE_TABLES: bool = True

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = ""

    FIRST_ADMIN_EMAIL: str = "admin@threatplatform.dev"
    FIRST_ADMIN_PASSWORD: str = "Admin@12345"

    DETECTION_CONTENT_PATH: str = "../detection-content"
    CORS_ORIGINS: str = "http://localhost:5173"

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
