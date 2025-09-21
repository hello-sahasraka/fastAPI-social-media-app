from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseClass(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class GlobalConfig(BaseClass):
    DATABASE_URL: Optional[str] = None
    BD_FORCE_RELOAD: bool = False


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")
    pass


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")
    pass


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    BD_FORCE_RELOAD: bool = True
    model_config = SettingsConfigDict(env_prefix="TEST_")
    pass


@lru_cache()
def get_config(env_state: str):
    configs = {
        "dev": DevConfig(),
        "prod": ProdConfig(),
        "test": TestConfig(),
    }
    return configs.get(env_state)


config = get_config(BaseClass().ENV_STATE)
