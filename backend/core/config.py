from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# App settings are loaded from the environment
class Settings(BaseSettings):
    # -------------------------------------------------------
    # Application
    # -------------------------------------------------------
    app_name: str = "McKinsey AI Research Engine"
    environment: str = "development"
    debug: bool = True

    # -------------------------------------------------------
    # Supabase
    # -------------------------------------------------------
    supabase_url: str = Field(...)
    supabase_key: str = Field(...)

    # -------------------------------------------------------
    # Gemini AI
    # -------------------------------------------------------
    gemini_api_key: str = Field(...)

    # Fast model for Planner, Research, Extraction, Validation
    gemini_fast_model: str = "gemini-3.5-flash-lite"

    # Stronger model for Report generation
    gemini_report_model: str = "gemini-3.5-flash"

    # Retry configuration
    gemini_max_retries: int = 5
    gemini_initial_delay: int = 2

    # Request timeout (seconds)
    request_timeout: int = 120

    # -------------------------------------------------------
    # CORS
    # -------------------------------------------------------
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()