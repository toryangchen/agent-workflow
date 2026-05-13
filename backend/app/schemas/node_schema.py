from enum import Enum

from pydantic import BaseModel


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class WorkflowNode(BaseModel):
    node_id: str
    name: str
    status: NodeStatus = NodeStatus.PENDING
