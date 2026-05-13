from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.exceptions import LLMConfigurationError
from app.schemas.llm_schema import ParsedTaskInfo, RootCauseAnalysis


class LLMService:
    def __init__(self, force_mock: bool | None = None) -> None:
        self.force_mock = force_mock
        self.llm: ChatOpenAI | None = None

    def _should_mock(self) -> bool:
        if self.force_mock is not None:
            return self.force_mock
        return settings.app_env == "development" and (
            not settings.llm_api_key or not settings.llm_base_url or not settings.llm_model
        )

    def _get_llm(self) -> ChatOpenAI:
        if not settings.llm_api_key or not settings.llm_base_url or not settings.llm_model:
            raise LLMConfigurationError(
                "LLM_API_KEY、LLM_BASE_URL、LLM_MODEL 必须配置完整"
            )
        if self.llm is None:
            self.llm = ChatOpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
                model=settings.llm_model,
            )
        return self.llm

    async def extract_task_info(self, user_input: str) -> ParsedTaskInfo:
        if self._should_mock():
            return self._mock_extract_task_info(user_input)
        structured = self._get_llm().with_structured_output(ParsedTaskInfo)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "你是故障诊断平台的输入解析器。"
                        "从用户中文输入中提取 project_id 和标准化 error_code。"
                        "如果出现明确错误码，保持大写下划线格式。"
                    )
                ),
                HumanMessage(content=user_input),
            ]
        )
        return ParsedTaskInfo.model_validate(result)

    async def generate_root_cause(
        self,
        project_id: str,
        error_code: str,
        runbook_results: list[Any],
        context: dict[str, Any] | None = None,
        common_data: dict[str, Any] | None = None,
    ) -> RootCauseAnalysis:
        context_data = context or common_data or {}
        if self._should_mock():
            return self._mock_root_cause(project_id, error_code, context_data, runbook_results)
        structured = self._get_llm().with_structured_output(RootCauseAnalysis)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "你是资深 SRE，负责生成中文根因分析。"
                        "必须结合 Runbook 结果和上下文，给出简洁、可执行的结论。"
                    )
                ),
                HumanMessage(
                    content=(
                        f"project_id={project_id}\n"
                        f"error_code={error_code}\n"
                        f"context={context_data}\n"
                        f"runbook_results={[r.model_dump() if hasattr(r, 'model_dump') else r for r in runbook_results]}"
                    )
                ),
            ]
        )
        return RootCauseAnalysis.model_validate(result)

    def _mock_extract_task_info(self, user_input: str) -> ParsedTaskInfo:
        error_match = re.search(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b", user_input)
        project_match = re.search(r"\b[a-z][a-z0-9-]+-(?:prod|staging|test|dev)\b", user_input)
        return ParsedTaskInfo(
            project_id=project_match.group(0) if project_match else "payment-service-prod",
            error_code=error_match.group(0) if error_match else "JAVA_HEAP_OOM",
        )

    def _mock_root_cause(
        self,
        project_id: str,
        error_code: str,
        context: dict[str, Any],
        runbook_results: list[Any],
    ) -> RootCauseAnalysis:
        summaries = [
            r.summary if hasattr(r, "summary") else str(r.get("summary", ""))
            for r in runbook_results
        ]
        return RootCauseAnalysis(
            summary=(
                f"{project_id} 当前故障与 {error_code} 相关。综合 Runbook 结果看，"
                "Redis timeout、连接池接近上限以及 JVM 堆内存高水位同时出现，"
                "疑似 Redis 连接释放异常或最近发布引入请求堆积，进而放大 JVM 内存压力。"
            ),
            evidence=[
                "；".join(item for item in summaries if item) or "Runbook 已完成执行",
                f"LLD 依赖：{', '.join(context.get('lld_topology', {}).get('dependencies', []))}",
                f"Redis timeout 指标：{context.get('monitor_metrics', {}).get('redis_timeout_count', '-')}",
            ],
            suggestions=[
                "优先检查 Redis 连接池借还逻辑和连接池上限配置",
                "关联最近发布变更，必要时先回滚可疑版本",
                "补充 heap dump 和慢请求采样，确认是否存在连接泄漏或请求堆积",
            ],
        )
