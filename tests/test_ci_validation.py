"""CI validation tests for schema validation and package structure."""

from __future__ import annotations

import json
from pathlib import Path


def test_all_json_schemas_are_valid() -> None:
    """Validate that all JSON schema files are well-formed JSON."""
    schemas_dir = Path(__file__).resolve().parent.parent / "schemas"
    schema_files = list(schemas_dir.glob("*.schema.json"))

    assert len(schema_files) > 0, "No schema files found in schemas directory"

    for schema_file in schema_files:
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema = json.load(f)
            assert "$schema" in schema, f"{schema_file.name} missing $schema"
            assert "title" in schema, f"{schema_file.name} missing title"
            assert "type" in schema, f"{schema_file.name} missing type"
        except json.JSONDecodeError as exc:
            raise AssertionError(f"Invalid JSON in {schema_file.name}: {exc}")


def test_memory_record_schema_validates_sample_record() -> None:
    """Test that the memory record schema validates a sample record."""
    from jsonschema import Draft202012Validator, FormatChecker

    schemas_dir = Path(__file__).resolve().parent.parent / "schemas"
    schema_file = schemas_dir / "memory-record.schema.json"

    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    sample_record = {
        "memory_id": "mem_001",
        "tenant": "default",
        "project": "amf",
        "repository": "agent-memory-fabric",
        "scope": "repo",
        "visibility": "team",
        "type": "decision",
        "summary": "Test decision",
        "details": "Test details",
        "author": "test",
        "source": "unit-test",
        "status": "active",
        "created_at": "2026-03-29T00:00:00Z",
        "updated_at": "2026-03-29T00:00:00Z",
        "schema_version": "v1",
    }

    errors = list(validator.iter_errors(sample_record))
    assert len(errors) == 0, f"Schema validation failed: {[e.message for e in errors]}"


def test_invalid_record_fails_validation() -> None:
    """Test that invalid records fail schema validation."""
    from jsonschema import Draft202012Validator, FormatChecker

    schemas_dir = Path(__file__).resolve().parent.parent / "schemas"
    schema_file = schemas_dir / "memory-record.schema.json"

    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    # Invalid: missing required 'updated_at' field and invalid scope value
    invalid_record = {
        "memory_id": "mem_001",
        "tenant": "default",
        "project": "amf",
        "repository": "agent-memory-fabric",
        "scope": "invalid_scope",  # Not in enum
        "visibility": "team",
        "type": "decision",
        "summary": "Test decision",
        "author": "test",
        "source": "unit-test",
        "status": "active",
        "created_at": "2026-03-29T00:00:00Z",
        "updated_at": "2026-03-29T00:00:00Z",
        "schema_version": "v1",
    }

    errors = list(validator.iter_errors(invalid_record))
    assert len(errors) > 0, "Expected validation errors for invalid record"
