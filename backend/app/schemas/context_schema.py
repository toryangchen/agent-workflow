from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.runbook_schema import RunbookDefinition, RunbookResult


class AgentContext(BaseModel):
    task_id: str
    user_input: str
    project_id: str | None = None
    error_code: str | None = None
    runbooks: list[RunbookDefinition] = Field(default_factory=list)

    project_info: dict[str, Any] = Field(default_factory=dict)
    lld_topology: dict[str, Any] = Field(default_factory=dict)
    feisha_logs: list[Any] = Field(default_factory=list)
    monitor_metrics: dict[str, Any] = Field(default_factory=dict)
    release_info: dict[str, Any] = Field(default_factory=dict)

    runbook_results: list[RunbookResult] = Field(default_factory=list)
    root_cause: dict[str, Any] = Field(default_factory=dict)
    scratchpad: dict[str, Any] = Field(default_factory=dict)

    def runtime_view(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "user_input": self.user_input,
            "project_id": self.project_id,
            "error_code": self.error_code,
            "project_info": self.project_info,
            "lld_topology": self.lld_topology,
            "feisha_logs": self.feisha_logs,
            "monitor_metrics": self.monitor_metrics,
            "release_info": self.release_info,
            "scratchpad": self.scratchpad,
        }

