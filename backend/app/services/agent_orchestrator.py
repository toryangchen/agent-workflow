from __future__ import annotations

import asyncio

from app.repositories.context_repository import AgentContextRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.event_schema import EventType
from app.schemas.node_schema import NodeStatus
from app.services.llm_service import LLMService
from app.services.sse_manager import SSEManager
from app.workflow.graph import build_graph


class AgentOrchestrator:
    def __init__(
        self,
        task_repository: TaskRepository,
        sse_manager: SSEManager,
        llm_service,
        context_repository: AgentContextRepository | None = None,
    ) -> None:
        self.task_repository = task_repository
        self.sse_manager = sse_manager
        self.context_repository = context_repository or AgentContextRepository()
        self.llm_service = llm_service or LLMService(force_mock=True)
        self.graph = build_graph(task_repository, sse_manager, self.llm_service)
        self._tasks: dict[str, asyncio.Task] = {}

    async def create_task(self, user_input: str) -> str:
        snapshot = self.task_repository.create(user_input)
        context = self.context_repository.create(snapshot.task_id, user_input)
        self.task_repository.set_context(snapshot.task_id, context.model_dump(mode="json"))
        task = asyncio.create_task(self._run(snapshot.task_id, user_input))
        self._tasks[snapshot.task_id] = task
        return snapshot.task_id

    async def wait_for_task(self, task_id: str) -> None:
        task = self._tasks.get(task_id)
        if task:
            await task

    async def _run(self, task_id: str, user_input: str) -> None:
        await self.sse_manager.publish(
            task_id, EventType.TASK_STARTED, "任务开始", payload={"user_input": user_input}
        )
        try:
            context = self.context_repository.get(task_id)
            await self.graph.ainvoke({"task_id": task_id, "context": context})
            self.task_repository.set_status(task_id, "success")
            await self.sse_manager.publish(task_id, EventType.TASK_COMPLETED, "任务完成")
        except Exception as exc:
            self.task_repository.set_status(task_id, "failed", str(exc))
            for node in self.task_repository.get(task_id).nodes:
                if node.status == NodeStatus.RUNNING:
                    self.task_repository.set_node_status(task_id, node.node_id, NodeStatus.FAILED)
            await self.sse_manager.publish(
                task_id,
                EventType.TASK_FAILED,
                f"任务失败：{exc}",
                payload={"error": str(exc)},
            )
