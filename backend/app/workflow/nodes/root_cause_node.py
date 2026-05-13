from app.repositories.task_repository import TaskRepository
from app.schemas.event_schema import EventType
from app.schemas.node_schema import NodeStatus
from app.services.root_cause_service import RootCauseService
from app.services.sse_manager import SSEManager
from app.workflow.state import AgentState


class RootCauseNode:
    def __init__(
        self,
        task_repository: TaskRepository,
        sse_manager: SSEManager,
        root_cause_service: RootCauseService,
    ) -> None:
        self.task_repository = task_repository
        self.sse_manager = sse_manager
        self.root_cause_service = root_cause_service

    async def __call__(self, state: AgentState) -> AgentState:
        task_id = state["task_id"]
        context = state["context"]
        self.task_repository.set_node_status(task_id, "root_cause", NodeStatus.RUNNING)
        await self.sse_manager.publish(
            task_id,
            EventType.NODE_STARTED,
            "根因分析生成开始",
            node_id="root_cause",
        )
        root_cause = await self.root_cause_service.analyze(
            project_id=context.project_id or "",
            error_code=context.error_code or "",
            context=context.runtime_view(),
            runbook_results=context.runbook_results,
        )
        context.root_cause = root_cause
        self.task_repository.set_root_cause(task_id, root_cause)
        self.task_repository.set_context(task_id, context.model_dump(mode="json"))
        self.task_repository.set_node_status(task_id, "root_cause", NodeStatus.SUCCESS)
        await self.sse_manager.publish(
            task_id,
            EventType.NODE_FINISHED,
            "根因分析生成完成",
            node_id="root_cause",
            payload=root_cause,
        )
        return {**state, "context": context}
