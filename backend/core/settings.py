"""Centralized backend configuration.

Single source of truth for application-level settings (metadata, environment,
CORS). Values are read from the environment (and an optional local ``.env``)
via Pydantic Settings, so nothing is hard-coded and no secret ever lives in
source.

Deliberately out of scope here: Databricks host/token/endpoint configuration.
The RAG pipeline (``orchestration.query_pipeline``) owns its own Databricks
authentication; duplicating it in this API layer would create two sources of
truth. See ``dependencies/rag.py``.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, overridable via ``Pravnislav*`` environment variables.

    Example: ``PRAVNISLAV_ENVIRONMENT=production``,
    ``PRAVNISALV_CORS_ALLOW_ORIGINS="https://pravnislav.rs,https://www.pravnisalv.rs"``.
    """

    model_config = SettingsConfigDict(
        env_prefix="PRAVNISLAV_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application metadata (shown in OpenAPI) ---------------------------
    app_name: str = "Pravnislav API"
    app_description: str = (
        "REST API за Pravnislav — правни RAG асистент за српско законодавство."
    )
    app_version: str = "1.0.0"

    # --- Runtime environment ---------------------------------------------
    # "development" enables the Swagger/OpenAPI docs; anything else disables them.
    environment: str = "development"

    # --- CORS -------------------------------------------------------------
    # Default targets the local Vite dev server (pravnislav-fe). Override per
    # environment. Accepts a JSON array or a comma-separated string.
    cors_allow_origins: list[str] = Field(default=["http://localhost:5173"])

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Allow ``A,B,C`` in addition to a JSON array for env-var ergonomics."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped.startswith("["):
                return [item.strip() for item in stripped.split(",") if item.strip()]
        return value

    @property
    def is_development(self) -> bool:
        return self.environment.strip().lower() == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (read once per process)."""
    return Settings()
