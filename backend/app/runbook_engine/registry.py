from __future__ import annotations

from pathlib import Path

from app.runbook_engine.loader import RunbookLoader
from app.runbook_engine.parser import load_error_code_mapping
from app.schemas.runbook_schema import RunbookDefinition


class RunbookRegistry:
    def __init__(self, runbooks_dir: Path, mapping_file: Path) -> None:
        self.runbooks_dir = runbooks_dir
        self.mapping_file = mapping_file
        self._runbooks = RunbookLoader(runbooks_dir).load_all()
        self._mapping = load_error_code_mapping(mapping_file)

    def get_by_error_code(self, error_code: str) -> list[RunbookDefinition]:
        ids = self._mapping.get(error_code, [])
        return [self._runbooks[runbook_id] for runbook_id in ids if runbook_id in self._runbooks]

