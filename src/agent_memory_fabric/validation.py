from __future__ import annotations

from typing import Any

from .schema_loader import load_schema


def validate_payload(schema_name: str, payload: dict[str, Any]) -> None:
    schema = load_schema(schema_name)
    required = schema.get("required", [])
    missing = [key for key in required if key not in payload]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Missing required fields for {schema_name}: {joined}")

    properties = schema.get("properties", {})
    if not schema.get("additionalProperties", True):
        unexpected = [key for key in payload if key not in properties]
        if unexpected:
            joined = ", ".join(unexpected)
            raise ValueError(f"Unexpected fields for {schema_name}: {joined}")
