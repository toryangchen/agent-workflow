import asyncio

from app.repositories.task_repository import TaskRepository
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.llm_service import ParsedTaskInfo, RootCauseAnalysis
from app.services.sse_manager import SSEManager


class FakeLLMService:
    async def extract_task_info(self, user_input: str) -> ParsedTaskInfo:
        return ParsedTaskInfo(
            project_id="payment-service-prod",
            error_code="JAVA_HEAP_OOM",
        )

    async def generate_root_cause(self, **kwargs) -> RootCauseAnalysis:
        return RootCauseAnalysis(
            summary="当前故障疑似由 Redis 连接池耗尽导致，并伴随 JVM 堆内存压力上升。",
            evidence=["Redis timeout 次数异常", "JVM heap usage 持续高位"],
            suggestions=["优先检查 Redis 连接释放逻辑", "回滚最近可疑发布"],
        )


def test_workflow_happy_path_updates_snapshot_and_events():
    async def run():
        task_repo = TaskRepository()
        sse = SSEManager()
        orchestrator = AgentOrchestrator(
            task_repository=task_repo,
            sse_manager=sse,
            llm_service=FakeLLMService(),
        )

        task_id = await orchestrator.create_task(
            "payment-service-prod 最近 Redis timeout 很严重，错误码 JAVA_HEAP_OOM"
        )
        await orchestrator.wait_for_task(task_id)
        return task_repo.get(task_id), sse.get_events(task_id)

    snapshot, events = asyncio.run(run())

    assert snapshot is not None
    assert snapshot.status == "success"
    assert snapshot.project_id == "payment-service-prod"
    assert snapshot.error_code == "JAVA_HEAP_OOM"
    assert len(snapshot.runbook_results) == 3
    assert snapshot.root_cause is not None
    assert snapshot.context is not None
    assert snapshot.context["lld_topology"]["dependencies"]
    assert events[-1].type == "task_completed"


def test_workflow_runs_to_completion_with_mock_llm_without_api_key():
    async def run():
        task_repo = TaskRepository()
        sse = SSEManager()
        orchestrator = AgentOrchestrator(
            task_repository=task_repo,
            sse_manager=sse,
            llm_service=None,
        )

        task_id = await orchestrator.create_task(
            "payment-service-prod 最近 Redis timeout 很严重，错误码 JAVA_HEAP_OOM"
        )
        await orchestrator.wait_for_task(task_id)
        return task_repo.get(task_id), sse.get_events(task_id)

    snapshot, events = asyncio.run(run())

    assert snapshot.status == "success"
    assert snapshot.project_id == "payment-service-prod"
    assert snapshot.error_code == "JAVA_HEAP_OOM"
    assert len(snapshot.runbook_results) == 3
    assert snapshot.root_cause["summary"]
    assert events[-1].type == "task_completed"


def test_workflow_failure_publishes_task_failed():
    class BrokenLLMService:
        async def extract_task_info(self, user_input: str) -> ParsedTaskInfo:
            raise RuntimeError("llm unavailable")

    async def run():
        task_repo = TaskRepository()
        sse = SSEManager()
        orchestrator = AgentOrchestrator(
            task_repository=task_repo,
            sse_manager=sse,
            llm_service=BrokenLLMService(),
        )

        task_id = await orchestrator.create_task("bad input")
        await orchestrator.wait_for_task(task_id)
        return task_repo.get(task_id), sse.get_events(task_id)

    snapshot, events = asyncio.run(run())

    assert snapshot is not None
    assert snapshot.status == "failed"
    assert events[-1].type == "task_failed"
    assert "llm unavailable" in events[-1].message
