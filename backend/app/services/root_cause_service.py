from __future__ import annotations

from typing import Any

from app.services.llm_service import LLMService


class RootCauseService:
    def __init__(self, llm_service: LLMService) -> None:
        self.llm_service = llm_service

    async def analyze(
        self,
        project_id: str,
        error_code: str,
        context: dict[str, Any],
        runbook_results: list[Any],
    ) -> dict[str, Any]:
        result = await self.llm_service.generate_root_cause(
            project_id=project_id,
            error_code=error_code,
            context=context,
            runbook_results=runbook_results,
        )
        return result.model_dump()
