from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings
from app.runbook_engine.http_client import RunbookHttpClient


def execute_script(
    script_path: str,
    context: dict[str, Any],
    http_client: RunbookHttpClient | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "success",
        "summary": "",
        "evidence": [],
        "suggestion": "",
    }
    code = Path(script_path).read_text(encoding="utf-8")
    globals_dict = {
        "__builtins__": {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "sum": sum,
            "min": min,
            "max": max,
            "range": range,
            "enumerate": enumerate,
            "list": list,
            "dict": dict,
            "set": set,
            "any": any,
            "all": all,
            "Exception": Exception,
        },
        "context": context,
        "result": result,
        "http": http_client
        or RunbookHttpClient(
            allowed_hosts=settings.runbook_http_allowed_hosts,
            default_timeout_seconds=settings.runbook_http_timeout_seconds,
        ),
    }
    exec(compile(code, script_path, "exec"), globals_dict, globals_dict)
    return result
