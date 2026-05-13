from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    TASK_STARTED = "task_started"
    NODE_STARTED = "node_started"
    NODE_FINISHED = "node_finished"
    SUB_NODE_STARTED = "sub_node_started"
    SUB_NODE_FINISHED = "sub_node_finished"
    LOG = "log"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"


class AgentEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    node_id: str | None = None
    runbook_id: str | None = None
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
