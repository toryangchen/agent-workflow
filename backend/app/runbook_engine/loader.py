from __future__ import annotations

from pathlib import Path

import yaml

from app.schemas.runbook_schema import RunbookDefinition


class RunbookLoader:
    def __init__(self, runbooks_dir: Path) -> None:
        self.runbooks_dir = runbooks_dir

    def load_all(self) -> dict[str, RunbookDefinition]:
        runbooks: dict[str, RunbookDefinition] = {}
        for yaml_file in sorted(self.runbooks_dir.glob("*/runbook.yaml")):
            with yaml_file.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
            script_path = yaml_file.parent / "script.py"
            runbook = RunbookDefinition(
                **data,
                script_path=str(script_path),
            )
            runbooks[runbook.id] = runbook
        return runbooks

