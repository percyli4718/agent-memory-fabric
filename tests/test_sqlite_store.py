from __future__ import annotations

from pathlib import Path

from agent_memory_fabric.handlers import ToolHandlers
from agent_memory_fabric.storage.sqlite import SQLiteMemoryStore


def sample_write_payload(
    *,
    scope: str = "repo",
    visibility: str = "team",
    type: str = "decision",
    summary: str = "Prefer Python for the open core runtime",
    details: str = "Python is the first implementation language for the open core.",
    tags: list[str] | None = None,
) -> dict:
    return {
        "tenant": "default",
        "project": "amf",
        "repository": "agent-memory-fabric",
        "scope": scope,
        "visibility": visibility,
        "type": type,
        "summary": summary,
        "details": details,
        "tags": tags or ["python", "runtime"],
        "author": "test-suite",
        "source": "unit-test",
    }


def test_write_and_search_memory(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    record = store.write_memory(sample_write_payload())
    assert record.memory_id.startswith("mem_")

    results = store.search_memory(
        {
            "query": "Python",
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": ["repo"],
            "types": ["decision"],
            "limit": 10,
        }
    )

    assert len(results) == 1
    assert results[0].summary == "Prefer Python for the open core runtime"


def test_rejects_missing_required_fields(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    try:
        store.write_memory({"tenant": "default"})
    except ValueError as exc:
        assert "Schema validation failed" in str(exc)
    else:
        raise AssertionError("Expected validation error")


def test_rejects_invalid_visibility_for_scope(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    try:
        store.write_memory(sample_write_payload(scope="user", visibility="team"))
    except ValueError as exc:
        assert "not allowed" in str(exc)
    else:
        raise AssertionError("Expected policy validation error")


def test_rejects_unsupported_retrieval_scope(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    try:
        store.search_memory(
            {
                "query": "Python",
                "tenant": "default",
                "project": "amf",
                "repository": "agent-memory-fabric",
                "scope": ["org"],
            }
        )
    except ValueError as exc:
        assert "Unsupported scopes" in str(exc)
    else:
        raise AssertionError("Expected retrieval policy validation error")


def test_get_recent_project_context_returns_latest_first(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    store.write_memory(
        sample_write_payload(
            type="note",
            summary="Earlier repository note",
            details="This was written first.",
        )
    )
    later = store.write_memory(
        sample_write_payload(
            type="decision",
            summary="Later repository decision",
            details="This was written second.",
        )
    )

    results = store.get_recent_project_context(
        {
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": ["repo"],
            "limit": 10,
        }
    )

    assert len(results) == 2
    assert results[0].memory_id == later.memory_id


def test_get_decisions_filters_decision_records(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    store.write_memory(sample_write_payload(type="note", summary="A note"))
    store.write_memory(sample_write_payload(type="decision", summary="A decision"))

    results = store.get_decisions(
        {
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": ["repo"],
            "limit": 10,
        }
    )

    assert len(results) == 1
    assert results[0].type.value == "decision"


def test_get_open_questions_filters_question_and_todo_records(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    store.write_memory(sample_write_payload(type="question", summary="Open question"))
    store.write_memory(sample_write_payload(type="todo", summary="Open todo"))
    store.write_memory(sample_write_payload(type="decision", summary="Closed decision"))

    results = store.get_open_questions(
        {
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": ["repo"],
            "limit": 10,
        }
    )

    assert len(results) == 2
    assert {record.type.value for record in results} == {"question", "todo"}


def test_redact_memory_updates_record_and_appends_audit_event(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    record = store.write_memory(
        sample_write_payload(
            type="note",
            summary="Sensitive note",
            details="Contains material that should be redacted.",
        )
    )

    redacted = store.redact_memory(
        {
            "memory_id": record.memory_id,
            "redacted_by": "security-review",
            "reason": "Contains sensitive data",
        }
    )

    assert redacted.status.value == "redacted"
    assert redacted.details == "[REDACTED]"
    assert redacted.metadata["redacted_by"] == "security-review"

    events = store.list_audit_events()
    assert len(events) == 2
    assert events[-1]["event_type"] == "memory_redacted"


def test_tool_handlers_expose_mcp_facing_results(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))
    handlers = ToolHandlers(store)

    created = handlers.write_memory(sample_write_payload(summary="Handler write"))
    assert created["memory"]["summary"] == "Handler write"

    search = handlers.search_memory(
        {
            "query": "Handler",
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": ["repo"],
            "limit": 10,
        }
    )
    assert search["count"] == 1

    redacted = handlers.redact_memory(
        {
            "memory_id": created["memory"]["memory_id"],
            "redacted_by": "handler-test",
            "reason": "test",
        }
    )
    assert redacted["memory"]["status"] == "redacted"


def test_upsert_fact_creates_and_updates_single_fact_record(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))

    first = store.upsert_fact(
        {
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": "repo",
            "visibility": "team",
            "fact_key": "service_owner",
            "fact_value": "platform-team",
            "author": "test-suite",
            "source": "unit-test",
        }
    )
    second = store.upsert_fact(
        {
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": "repo",
            "visibility": "team",
            "fact_key": "service_owner",
            "fact_value": "core-platform",
            "author": "test-suite",
            "source": "unit-test",
        }
    )

    assert first.memory_id == second.memory_id
    assert second.metadata["fact_value"] == "core-platform"
    assert second.type.value == "fact"


def test_list_memories_by_repo_returns_filtered_records(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    store = SQLiteMemoryStore(str(db_path))
    store.write_memory(sample_write_payload(type="note", summary="Repo note"))
    store.write_memory(sample_write_payload(type="decision", summary="Repo decision"))

    results = store.list_memories_by_repo(
        {
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": ["repo"],
            "types": ["decision"],
            "limit": 10,
        }
    )

    assert len(results) == 1
    assert results[0].summary == "Repo decision"


def test_handler_supports_upsert_fact_and_list_by_repo(tmp_path: Path) -> None:
    db_path = tmp_path / "amf.db"
    handlers = ToolHandlers(SQLiteMemoryStore(str(db_path)))

    fact = handlers.upsert_fact(
        {
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": "repo",
            "visibility": "team",
            "fact_key": "runbook",
            "fact_value": "/data/runbooks/amf.md",
            "author": "handler-test",
            "source": "unit-test",
        }
    )
    assert fact["memory"]["type"] == "fact"

    listed = handlers.list_memories_by_repo(
        {
            "tenant": "default",
            "project": "amf",
            "repository": "agent-memory-fabric",
            "scope": ["repo"],
            "types": ["fact"],
            "limit": 10,
        }
    )
    assert listed["count"] == 1
    assert listed["results"][0]["metadata"]["fact_key"] == "runbook"
