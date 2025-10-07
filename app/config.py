from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


# -----------------------------
# Base class only cares about ENV_STATE
# -----------------------------
class BaseClass(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unknown env vars
    )


# -----------------------------
# Global config for DB and flags
# -----------------------------
class GlobalConfig(BaseSettings):
    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///./dev.db"
    BD_FORCE_RELOAD: bool = False
    SECRET_KEY: Optional[str] = None
    MAILGUN_API_KEY: Optional[str] = "test key"
    MAILGUN_DOMAIN: Optional[str] = "test domain"
    B2_KEY_ID: Optional[str] = None
    B2_APPLICATION_KEY: Optional[str] = None
    B2_BUCKET_NAME: Optional[str] = None
    DEEPAI_API_KEY: Optional[str] = None
    SENTRY_DNS: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # important to ignore unknown vars
    )


# -----------------------------
# Environment-specific configs
# -----------------------------
class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="DEV_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="PROD_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    BD_FORCE_RELOAD: bool = True
    model_config = SettingsConfigDict(
        env_prefix="TEST_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# -----------------------------
# Load config once using LRU cache
# -----------------------------
@lru_cache()
def get_config():
    env_state = (BaseClass().ENV_STATE or "dev").lower()

    configs = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig,
    }

    config_class = configs.get(env_state, DevConfig)
    return config_class()


config = get_config()
