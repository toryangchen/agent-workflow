from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.node_schema import WorkflowNode
from app.schemas.runbook_schema import RunbookResult


class TaskCreateRequest(BaseModel):
    user_input: str = Field(min_length=1)


class TaskCreateResponse(BaseModel):
    task_id: str
    status: str


class TaskSnapshot(BaseModel):
    task_id: str
    user_input: str
    status: str
    project_id: str | None = None
    error_code: str | None = None
    nodes: list[WorkflowNode] = Field(default_factory=list)
    runbook_results: list[RunbookResult] = Field(default_factory=list)
    root_cause: dict | None = None
    context: dict | None = None
    error_message: str | None = None
