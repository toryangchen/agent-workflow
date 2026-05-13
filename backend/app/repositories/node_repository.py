from app.repositories.task_repository import TaskRepository
from app.schemas.node_schema import NodeStatus


class NodeRepository:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    def set_status(self, task_id: str, node_id: str, status: NodeStatus) -> None:
        self.task_repository.set_node_status(task_id, node_id, status)

