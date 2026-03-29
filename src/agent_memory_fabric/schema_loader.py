from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=None)
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    schema_path = project_root() / "schemas" / name
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
