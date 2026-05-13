from __future__ import annotations

from typing import TypedDict

from app.schemas.context_schema import AgentContext


class AgentState(TypedDict, total=False):
    task_id: str
    context: AgentContext
