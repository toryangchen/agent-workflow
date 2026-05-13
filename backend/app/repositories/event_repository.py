from __future__ import annotations

from app.schemas.event_schema import AgentEvent


class EventRepository:
    def __init__(self) -> None:
        self._events: dict[str, list[AgentEvent]] = {}

    def append(self, event: AgentEvent) -> None:
        self._events.setdefault(event.task_id, []).append(event)

    def list_by_task(self, task_id: str) -> list[AgentEvent]:
        return list(self._events.get(task_id, []))

