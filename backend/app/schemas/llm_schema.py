from __future__ import annotations

from pydantic import BaseModel, Field


class ParsedTaskInfo(BaseModel):
    project_id: str = Field(description="业务项目或服务标识")
    error_code: str = Field(description="标准化错误码，例如 JAVA_HEAP_OOM")


class RootCauseAnalysis(BaseModel):
    summary: str = Field(description="中文根因分析总结")
    evidence: list[str] = Field(default_factory=list, description="关键证据")
    suggestions: list[str] = Field(default_factory=list, description="处理建议")

