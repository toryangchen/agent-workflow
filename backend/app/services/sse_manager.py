from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any

from app.repositories.event_repository import EventRepository
from app.schemas.event_schema import AgentEvent, EventType


class SSEManager:
    def __init__(self, event_repository: EventRepository | None = None) -> None:
        self.event_repository = event_repository or EventRepository()
        self._subscribers: dict[str, set[asyncio.Queue[AgentEvent]]] = {}

    async def publish(
        self,
        task_id: str,
        event_type: EventType,
        message: str,
        node_id: str | None = None,
        runbook_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> AgentEvent:
        event = AgentEvent(
            task_id=task_id,
            type=event_type,
            node_id=node_id,
            runbook_id=runbook_id,
            message=message,
            payload=payload or {},
        )
        self.event_repository.append(event)
        for queue in self._subscribers.get(task_id, set()):
            await queue.put(event)
        return event

    def get_events(self, task_id: str) -> list[AgentEvent]:
        return self.event_repository.list_by_task(task_id)

    async def subscribe(self, task_id: str) -> AsyncGenerator[AgentEvent, None]:
        queue: asyncio.Queue[AgentEvent] = asyncio.Queue()
        self._subscribers.setdefault(task_id, set()).add(queue)
        try:
            for event in self.get_events(task_id):
                yield event
            while True:
                yield await queue.get()
        finally:
            self._subscribers.get(task_id, set()).discard(queue)

    @staticmethod
    def format_sse(event: AgentEvent) -> str:
        data = event.model_dump(mode="json")
        return f"event: {event.type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

