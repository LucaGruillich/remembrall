import json
from pathlib import Path


def load_project_index(vault_path: str) -> list[dict]:
    project_index_path = Path(vault_path) / "System" / "project_index.json"

    if not project_index_path.exists():
        return []

    with project_index_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return []

    return data