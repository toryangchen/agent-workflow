from __future__ import annotations

from pathlib import Path

import yaml


def load_error_code_mapping(mapping_file: Path) -> dict[str, list[str]]:
    with mapping_file.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    return {str(key): list(value or []) for key, value in data.items()}

