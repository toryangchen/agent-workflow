from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    llm_model: str = os.getenv("LLM_MODEL", "")
    runbook_http_allowed_hosts: tuple[str, ...] = tuple(
        host.strip()
        for host in os.getenv("RUNBOOK_HTTP_ALLOWED_HOSTS", "httpbin.org").split(",")
        if host.strip()
    )
    runbook_http_timeout_seconds: float = float(
        os.getenv("RUNBOOK_HTTP_TIMEOUT_SECONDS", "3")
    )
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )


settings = Settings()
