import asyncio

from app.repositories.task_repository import TaskRepository
from app.runbook_engine.executor import RunbookExecutor
from app.schemas.event_schema import EventType
from app.schemas.node_schema import NodeStatus
from app.services.sse_manager import SSEManager
from app.workflow.state import AgentState


class RunbookExecuteNode:
    def __init__(
        self,
        task_repository: TaskRepository,
        sse_manager: SSEManager,
        executor: RunbookExecutor,
    ) -> None:
        self.task_repository = task_repository
        self.sse_manager = sse_manager
        self.executor = executor

    async def __call__(self, state: AgentState) -> AgentState:
        task_id = state["task_id"]
        context = state["context"]
        runbooks = context.runbooks
        self.task_repository.set_node_status(task_id, "runbook_execute", NodeStatus.RUNNING)
        await self.sse_manager.publish(
            task_id,
            EventType.NODE_STARTED,
            "Runbook 执行开始",
            node_id="runbook_execute",
        )

        async def run_one(runbook):
            await self.sse_manager.publish(
                task_id,
                EventType.SUB_NODE_STARTED,
                f"{runbook.name} 开始",
                node_id="runbook_execute",
                runbook_id=runbook.id,
            )
            result = await self.executor.execute_one(runbook, context)
            await self.sse_manager.publish(
                task_id,
                EventType.SUB_NODE_FINISHED,
                f"{runbook.name} {result.status}",
                node_id="runbook_execute",
                runbook_id=runbook.id,
                payload=result.model_dump(),
            )
            return result

        results = await asyncio.gather(*(run_one(runbook) for runbook in runbooks))
        context.runbook_results = results
        self.task_repository.set_runbook_results(task_id, results)
        self.task_repository.set_context(task_id, context.model_dump(mode="json"))
        self.task_repository.set_node_status(task_id, "runbook_execute", NodeStatus.SUCCESS)
        await self.sse_manager.publish(
            task_id,
            EventType.NODE_FINISHED,
            "Runbook 执行完成",
            node_id="runbook_execute",
            payload={"count": len(results)},
        )
        return {**state, "context": context}
