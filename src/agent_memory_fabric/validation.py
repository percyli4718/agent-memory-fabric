from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from .schema_loader import load_schema


def validate_payload(schema_name: str, payload: dict[str, Any]) -> None:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    if not errors:
        return

    message = "; ".join(_format_error(err) for err in errors)
    raise ValueError(f"Schema validation failed for {schema_name}: {message}")


def _format_error(error: JsonSchemaValidationError) -> str:
    path = ".".join(str(part) for part in error.path)
    prefix = f"{path}: " if path else ""
    return f"{prefix}{error.message}"
