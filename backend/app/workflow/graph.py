from langgraph.graph import END, START, StateGraph

from app.repositories.task_repository import TaskRepository
from app.runbook_engine.executor import RunbookExecutor
from app.services.context_manager import ContextManager
from app.services.root_cause_service import RootCauseService
from app.services.sse_manager import SSEManager
from app.workflow.nodes.common_data_node import CommonDataNode
from app.workflow.nodes.root_cause_node import RootCauseNode
from app.workflow.nodes.runbook_execute_node import RunbookExecuteNode
from app.workflow.nodes.task_init_node import TaskInitNode
from app.workflow.state import AgentState


def build_graph(
    task_repository: TaskRepository,
    sse_manager: SSEManager,
    llm_service,
):
    graph = StateGraph(AgentState)
    graph.add_node("task_init_step", TaskInitNode(task_repository, sse_manager, llm_service))
    graph.add_node(
        "common_data_step",
        CommonDataNode(task_repository, sse_manager, ContextManager()),
    )
    graph.add_node(
        "runbook_execute_step",
        RunbookExecuteNode(task_repository, sse_manager, RunbookExecutor()),
    )
    graph.add_node(
        "root_cause_step",
        RootCauseNode(
            task_repository,
            sse_manager,
            RootCauseService(llm_service),
        ),
    )
    graph.add_edge(START, "task_init_step")
    graph.add_edge("task_init_step", "common_data_step")
    graph.add_edge("common_data_step", "runbook_execute_step")
    graph.add_edge("runbook_execute_step", "root_cause_step")
    graph.add_edge("root_cause_step", END)
    return graph.compile()
