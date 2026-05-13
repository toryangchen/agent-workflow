from app.repositories.task_repository import TaskRepository
from app.collectors.feisha_log_collector import collect_feisha_logs
from app.collectors.lld_collector import collect_lld_topology
from app.collectors.monitor_collector import collect_monitor_metrics
from app.collectors.release_collector import collect_release_info
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
        project_id = context.project_id or ""
        collectors = [
            ("lld_topology", "LLD 信息获取", collect_lld_topology),
            ("feisha_logs", "飞盟日志获取", collect_feisha_logs),
            ("monitor_metrics", "监控指标获取", collect_monitor_metrics),
            ("release_info", "发布记录获取", collect_release_info),
        ]
        for key, name, collector in collectors:
            if key not in keys:
                continue
            await self.sse_manager.publish(
                task_id,
                EventType.SUB_NODE_STARTED,
                f"{name}开始",
                node_id="common_data",
                payload={"step_id": key, "name": name},
            )
            value = await collector(project_id)
            setattr(context, key, value)
            await self.sse_manager.publish(
                task_id,
                EventType.SUB_NODE_FINISHED,
                f"{name}完成",
                node_id="common_data",
                payload={"step_id": key, "name": name, "status": "success"},
            )
        context.project_info = {
            "project_id": project_id,
            "environment": "prod" if project_id.endswith("-prod") else "unknown",
            "owner": "payment-platform",
        }
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
            },
        )
        return {**state, "context": context}
