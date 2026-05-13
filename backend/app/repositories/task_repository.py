from __future__ import annotations

from uuid import uuid4

from app.schemas.node_schema import NodeStatus, WorkflowNode
from app.schemas.runbook_schema import RunbookResult
from app.schemas.task_schema import TaskSnapshot


DEFAULT_NODES = [
    ("task_init", "任务初始化"),
    ("common_data", "通用数据获取"),
    ("runbook_execute", "Runbook 执行"),
    ("root_cause", "根因分析生成"),
]


class TaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskSnapshot] = {}

    def create(self, user_input: str) -> TaskSnapshot:
        task_id = str(uuid4())
        snapshot = TaskSnapshot(
            task_id=task_id,
            user_input=user_input,
            status="running",
            nodes=[
                WorkflowNode(node_id=node_id, name=name, status=NodeStatus.PENDING)
                for node_id, name in DEFAULT_NODES
            ],
        )
        self._tasks[task_id] = snapshot
        return snapshot

    def get(self, task_id: str) -> TaskSnapshot | None:
        return self._tasks.get(task_id)

    def set_status(self, task_id: str, status: str, error_message: str | None = None) -> None:
        task = self._tasks[task_id]
        task.status = status
        task.error_message = error_message

    def set_node_status(self, task_id: str, node_id: str, status: NodeStatus) -> None:
        task = self._tasks[task_id]
        for node in task.nodes:
            if node.node_id == node_id:
                node.status = status
                return

    def set_task_info(self, task_id: str, project_id: str, error_code: str) -> None:
        task = self._tasks[task_id]
        task.project_id = project_id
        task.error_code = error_code

    def set_runbook_results(self, task_id: str, results: list[RunbookResult]) -> None:
        self._tasks[task_id].runbook_results = results

    def set_root_cause(self, task_id: str, root_cause: dict) -> None:
        self._tasks[task_id].root_cause = root_cause

    def set_context(self, task_id: str, context: dict) -> None:
        self._tasks[task_id].context = context
