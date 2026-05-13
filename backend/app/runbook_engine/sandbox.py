from __future__ import annotations

from pathlib import Path
from typing import Any


def execute_script(script_path: str, context: dict[str, Any]) -> dict[str, Any]:
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
        },
        "context": context,
        "result": result,
    }
    exec(compile(code, script_path, "exec"), globals_dict, globals_dict)
    return result

