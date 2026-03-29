from __future__ import annotations

from pathlib import Path

from agent_memory_fabric.storage.sqlite import SQLiteMemoryStore


def sample_write_payload() -> dict:
    return {
        "tenant": "default",
        "project": "amf",
        "repository": "agent-memory-fabric",
        "scope": "repo",
        "visibility": "team",
        "type": "decision",
        "summary": "Prefer Python for the open core runtime",
        "details": "Python is the first implementation language for the open core.",
        "tags": ["python", "runtime"],
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
