from __future__ import annotations

from typing import Any

from app.schemas.runbook_schema import RunbookDefinition


def required_context_keys(runbooks: list[RunbookDefinition]) -> set[str]:
    keys: set[str] = set()
    for runbook in runbooks:
        keys.update(runbook.requires)
    return keys

