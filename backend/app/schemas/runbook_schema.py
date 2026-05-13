from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RunbookDefinition(BaseModel):
    id: str
    name: str
    description: str = ""
    requires: list[str] = Field(default_factory=list)
    timeout: int = 30
    tags: list[str] = Field(default_factory=list)
    script_path: str


class RunbookResult(BaseModel):
    runbook_id: str
    name: str
    status: str
    summary: str = ""
    evidence: list[str] = Field(default_factory=list)
    suggestion: str = ""
    error: str | None = None
    elapsed_ms: int = 0
    raw: dict[str, Any] = Field(default_factory=dict)

