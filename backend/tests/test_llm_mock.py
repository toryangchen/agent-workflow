import asyncio

from app.services.llm_service import LLMService


def test_llm_service_development_mock_extracts_project_and_error_code():
    async def run():
        service = LLMService(force_mock=True)
        return await service.extract_task_info(
            "payment-service-prod 最近 Redis timeout 很严重，错误码 JAVA_HEAP_OOM"
        )

    parsed = asyncio.run(run())

    assert parsed.project_id == "payment-service-prod"
    assert parsed.error_code == "JAVA_HEAP_OOM"


def test_llm_service_development_mock_generates_root_cause():
    async def run():
        service = LLMService(force_mock=True)
        return await service.generate_root_cause(
            project_id="payment-service-prod",
            error_code="JAVA_HEAP_OOM",
            context={},
            runbook_results=[],
        )

    result = asyncio.run(run())

    assert "payment-service-prod" in result.summary
    assert result.evidence
    assert result.suggestions
