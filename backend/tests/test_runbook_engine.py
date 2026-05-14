import asyncio
from pathlib import Path

from app.runbook_engine.executor import RunbookExecutor
from app.runbook_engine.registry import RunbookRegistry
from app.schemas.context_schema import AgentContext


def test_registry_loads_mapping_and_runbooks():
    registry = RunbookRegistry(
        runbooks_dir=Path("runbooks"),
        mapping_file=Path("runbooks/error_code_mapping.yaml"),
    )

    runbooks = registry.get_by_error_code("JAVA_HEAP_OOM")

    assert [runbook.id for runbook in runbooks] == [
        "redis_timeout_check",
        "jvm_heap_oom",
        "log_error_check",
    ]
    assert runbooks[0].requires == ["feisha_logs", "monitor_metrics"]


def test_executor_injects_context_and_collects_result():
    async def run():
        registry = RunbookRegistry(
            runbooks_dir=Path("runbooks"),
            mapping_file=Path("runbooks/error_code_mapping.yaml"),
        )
        runbook = registry.get_by_error_code("REDIS_TIMEOUT")[0]
        executor = RunbookExecutor()

        return await executor.execute_one(
            runbook,
            AgentContext(
                task_id="task-1",
                user_input="payment-service-prod JAVA_HEAP_OOM",
                project_id="payment-service-prod",
                error_code="REDIS_TIMEOUT",
                feisha_logs=[
                    "Redis timeout on payment-service-prod",
                    "normal request",
                    "Redis timeout while borrowing connection",
                ],
                monitor_metrics={"redis_timeout_count": 2},
            ),
        )

    result = asyncio.run(run())

    assert result.runbook_id == "redis_timeout_check"
    assert result.status == "success"
    assert "Redis timeout 2 次" in result.summary
    assert result.evidence


def test_agent_context_is_exposed_to_runtime_scripts():
    async def run():
        registry = RunbookRegistry(
            runbooks_dir=Path("runbooks"),
            mapping_file=Path("runbooks/error_code_mapping.yaml"),
        )
        runbook = registry.get_by_error_code("JAVA_HEAP_OOM")[2]
        executor = RunbookExecutor()
        context = AgentContext(
            task_id="task-1",
            user_input="payment-service-prod JAVA_HEAP_OOM",
            project_id="payment-service-prod",
            error_code="JAVA_HEAP_OOM",
            feisha_logs=[{"level": "ERROR", "message": "JAVA_HEAP_OOM Redis timeout"}],
            lld_topology={"dependencies": ["redis-cluster-prod"]},
        )
        return await executor.execute_one(runbook, context)

    result = asyncio.run(run())

    assert result.runbook_id == "log_error_check"
    assert "redis-cluster-prod" in " ".join(result.evidence)
