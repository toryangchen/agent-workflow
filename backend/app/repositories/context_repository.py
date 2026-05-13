from __future__ import annotations

from app.schemas.context_schema import AgentContext


class AgentContextRepository:
    def __init__(self) -> None:
        self._contexts: dict[str, AgentContext] = {}

    def create(self, task_id: str, user_input: str) -> AgentContext:
        context = AgentContext(task_id=task_id, user_input=user_input)
        self._contexts[task_id] = context
        return context

    def get(self, task_id: str) -> AgentContext | None:
        return self._contexts.get(task_id)

    def save(self, context: AgentContext) -> None:
        self._contexts[context.task_id] = context

