from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "SUPPLYMIND"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    database_url: str = "postgresql+psycopg://postgres@localhost:5433/supplymind"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24 * 7

    groq_api_key: Optional[str] = None
    groq_model: str = "openai/gpt-oss-120b"
    groq_fallback_model: Optional[str] = "llama-3.3-70b-versatile"
    groq_timeout_seconds: float = 60.0
    agent_max_tool_iterations: int = 8
    agent_max_retries: int = 3

    hindsight_base_url: str = "http://localhost:8888"
    hindsight_timeout_seconds: float = 180.0
    hindsight_top_k: int = 12
    hindsight_budget: str = "mid"

    band_enabled: bool = False
    band_agent_config: str = "agent_config.yaml"
    band_room_id: Optional[str] = None

    scheduler_enabled: bool = True
    scheduler_interval_seconds: int = 60
    seed_demo_on_startup: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
