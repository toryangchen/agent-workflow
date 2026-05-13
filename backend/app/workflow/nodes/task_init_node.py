from pathlib import Path

from app.core.exceptions import RunbookNotFoundError
from app.repositories.task_repository import TaskRepository
from app.runbook_engine.registry import RunbookRegistry
from app.schemas.event_schema import EventType
from app.schemas.node_schema import NodeStatus
from app.services.sse_manager import SSEManager
from app.workflow.state import AgentState


class TaskInitNode:
    def __init__(
        self,
        task_repository: TaskRepository,
        sse_manager: SSEManager,
        llm_service,
    ) -> None:
        self.task_repository = task_repository
        self.sse_manager = sse_manager
        self.llm_service = llm_service
        self.registry = RunbookRegistry(
            runbooks_dir=Path("runbooks"),
            mapping_file=Path("app/mappings/error_code_mapping.yaml"),
        )

    async def __call__(self, state: AgentState) -> AgentState:
        task_id = state["task_id"]
        context = state["context"]
        self.task_repository.set_node_status(task_id, "task_init", NodeStatus.RUNNING)
        await self.sse_manager.publish(
            task_id, EventType.NODE_STARTED, "任务初始化开始", node_id="task_init"
        )
        parsed = await self.llm_service.extract_task_info(context.user_input)
        runbooks = self.registry.get_by_error_code(parsed.error_code)
        if not runbooks:
            raise RunbookNotFoundError(f"未找到错误码 {parsed.error_code} 对应的 Runbook")
        self.task_repository.set_task_info(task_id, parsed.project_id, parsed.error_code)
        context.project_id = parsed.project_id
        context.error_code = parsed.error_code
        context.runbooks = runbooks
        self.task_repository.set_context(task_id, context.model_dump(mode="json"))
        self.task_repository.set_node_status(task_id, "task_init", NodeStatus.SUCCESS)
        await self.sse_manager.publish(
            task_id,
            EventType.NODE_FINISHED,
            "任务初始化完成",
            node_id="task_init",
            payload={
                "project_id": parsed.project_id,
                "error_code": parsed.error_code,
                "runbooks": [runbook.id for runbook in runbooks],
            },
        )
        return {
            **state,
            "context": context,
        }
