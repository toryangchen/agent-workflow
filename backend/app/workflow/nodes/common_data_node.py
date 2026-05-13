from app.repositories.task_repository import TaskRepository
from app.runbook_engine.context_injector import required_context_keys
from app.schemas.event_schema import EventType
from app.schemas.node_schema import NodeStatus
from app.services.context_manager import ContextManager
from app.services.sse_manager import SSEManager
from app.workflow.state import AgentState


class CommonDataNode:
    def __init__(
        self,
        task_repository: TaskRepository,
        sse_manager: SSEManager,
        context_manager: ContextManager,
    ) -> None:
        self.task_repository = task_repository
        self.sse_manager = sse_manager
        self.context_manager = context_manager

    async def __call__(self, state: AgentState) -> AgentState:
        task_id = state["task_id"]
        context = state["context"]
        self.task_repository.set_node_status(task_id, "common_data", NodeStatus.RUNNING)
        await self.sse_manager.publish(
            task_id, EventType.NODE_STARTED, "通用数据获取开始", node_id="common_data"
        )
        keys = required_context_keys(context.runbooks)
        context = await self.context_manager.collect(context, keys)
        self.task_repository.set_context(task_id, context.model_dump(mode="json"))
        self.task_repository.set_node_status(task_id, "common_data", NodeStatus.SUCCESS)
        await self.sse_manager.publish(
            task_id,
            EventType.NODE_FINISHED,
            "通用数据获取完成",
            node_id="common_data",
            payload={
                "keys": sorted(keys),
                "context": context.runtime_view(),
                "sub_steps": [
                    {"name": "LLD 信息获取", "status": "success", "duration": "00:00:05"},
                    {"name": "飞盟日志获取", "status": "success", "duration": "00:00:12"},
                    {"name": "监控指标获取", "status": "success", "duration": "00:00:08"},
                    {"name": "发布记录获取", "status": "success", "duration": "00:00:04"},
                ],
            },
        )
        return {**state, "context": context}
