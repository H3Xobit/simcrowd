"""Environment settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://sc:sc@localhost:25432/simcrowd"
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    census_api_key: str | None = None
    sc_log_level: str = "INFO"
    sc_seed: int = 42
    sc_offline_llm: bool = True
    sc_panel_size: int = 200


@lru_cache
def get_settings() -> Settings:
    return Settings()
