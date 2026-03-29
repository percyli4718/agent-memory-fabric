from __future__ import annotations

from pathlib import Path

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
        assert "Missing required fields" in str(exc)
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
