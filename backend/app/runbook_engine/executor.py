from __future__ import annotations

import asyncio
import time
from typing import Any

from app.core.config import settings
from app.runbook_engine.http_client import RunbookHttpClient
from app.runbook_engine.sandbox import execute_script
from app.schemas.context_schema import AgentContext
from app.schemas.runbook_schema import RunbookDefinition, RunbookResult


class RunbookExecutor:
    def __init__(self, http_client: RunbookHttpClient | None = None) -> None:
        self.http_client = http_client or RunbookHttpClient(
            allowed_hosts=settings.runbook_http_allowed_hosts,
            default_timeout_seconds=settings.runbook_http_timeout_seconds,
        )

    async def execute_one(
        self,
        runbook: RunbookDefinition,
        context: AgentContext | dict[str, Any],
    ) -> RunbookResult:
        start = time.perf_counter()
        try:
            raw = await asyncio.wait_for(
                asyncio.to_thread(
                    execute_script,
                    runbook.script_path,
                    context.runtime_view() if isinstance(context, AgentContext) else context,
                    self.http_client,
                ),
                timeout=runbook.timeout,
            )
            status = str(raw.get("status", "success"))
            return RunbookResult(
                runbook_id=runbook.id,
                name=runbook.name,
                status=status,
                summary=str(raw.get("summary", "")),
                evidence=list(raw.get("evidence", [])),
                suggestion=str(raw.get("suggestion", "")),
                elapsed_ms=int((time.perf_counter() - start) * 1000),
                raw=raw,
            )
        except Exception as exc:
            return RunbookResult(
                runbook_id=runbook.id,
                name=runbook.name,
                status="failed",
                summary="Runbook 执行失败",
                error=str(exc),
                elapsed_ms=int((time.perf_counter() - start) * 1000),
            )

    async def execute_many(
        self,
        runbooks: list[RunbookDefinition],
        context: AgentContext | dict[str, Any],
    ) -> list[RunbookResult]:
        return await asyncio.gather(
            *(self.execute_one(runbook, context) for runbook in runbooks)
        )
