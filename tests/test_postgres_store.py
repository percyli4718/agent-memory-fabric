from __future__ import annotations

import os
from typing import Any

import pytest
import pytest_asyncio

from agent_memory_fabric.handlers import ToolHandlers
from agent_memory_fabric.schema_loader import load_schema
from agent_memory_fabric.storage.postgres import PostgresMemoryStore


def get_test_dsn() -> str:
    """Get PostgreSQL connection string from environment or use default."""
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://test:test@localhost:5432/test_amf"
    )


class AsyncToolHandlers:
    """Async version of ToolHandlers for PostgreSQL testing."""

    def __init__(self, store: PostgresMemoryStore) -> None:
        self.store = store

    async def search_memory(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("search-memory.request.schema.json")
        results = [record.to_dict() for record in await self.store.search_memory(payload)]
        return {"results": results, "count": len(results)}

    async def write_memory(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("write-memory.request.schema.json")
        record = await self.store.write_memory(payload)
        return {"memory": record.to_dict()}

    async def get_recent_project_context(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-recent-project-context.request.schema.json")
        results = [
            record.to_dict() for record in await self.store.get_recent_project_context(payload)
        ]
        return {"results": results, "count": len(results)}

    async def get_decisions(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-decisions.request.schema.json")
        results = [record.to_dict() for record in await self.store.get_decisions(payload)]
        return {"results": results, "count": len(results)}

    async def get_open_questions(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-open-questions.request.schema.json")
        results = [record.to_dict() for record in await self.store.get_open_questions(payload)]
        return {"results": results, "count": len(results)}

    async def redact_memory(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("redact-memory.request.schema.json")
        record = await self.store.redact_memory(payload)
        return {"memory": record.to_dict()}

    async def upsert_fact(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("upsert-fact.request.schema.json")
        record = await self.store.upsert_fact(payload)
        return {"memory": record.to_dict()}

    async def list_memories_by_repo(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("list-memories-by-repo.request.schema.json")
        results = [record.to_dict() for record in await self.store.list_memories_by_repo(payload)]
        return {"results": results, "count": len(results)}


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


@pytest.fixture(scope="function")
def postgres_dsn() -> str:
    """Return the PostgreSQL connection string."""
    return get_test_dsn()


@pytest_asyncio.fixture(scope="function")
async def postgres_store(postgres_dsn: str) -> PostgresMemoryStore:
    """Create a PostgresMemoryStore instance for testing."""
    store = PostgresMemoryStore(postgres_dsn)
    await store._init_db()
    yield store
    await store.close()


@pytest.mark.asyncio
async def test_write_and_search_memory(postgres_store: PostgresMemoryStore) -> None:
    record = await postgres_store.write_memory(sample_write_payload())
    assert record.memory_id.startswith("mem_")

    results = await postgres_store.search_memory(
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


@pytest.mark.asyncio
async def test_rejects_missing_required_fields(postgres_store: PostgresMemoryStore) -> None:
    try:
        await postgres_store.write_memory({"tenant": "default"})
    except ValueError as exc:
        assert "Schema validation failed" in str(exc)
    else:
        raise AssertionError("Expected validation error")


@pytest.mark.asyncio
async def test_rejects_invalid_visibility_for_scope(postgres_store: PostgresMemoryStore) -> None:
    try:
        await postgres_store.write_memory(sample_write_payload(scope="user", visibility="team"))
    except ValueError as exc:
        assert "not allowed" in str(exc)
    else:
        raise AssertionError("Expected policy validation error")


@pytest.mark.asyncio
async def test_rejects_unsupported_retrieval_scope(postgres_store: PostgresMemoryStore) -> None:
    try:
        await postgres_store.search_memory(
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


@pytest.mark.asyncio
async def test_get_recent_project_context_returns_latest_first(postgres_store: PostgresMemoryStore) -> None:
    await postgres_store.write_memory(
        sample_write_payload(
            type="note",
            summary="Earlier repository note",
            details="This was written first.",
        )
    )
    later = await postgres_store.write_memory(
        sample_write_payload(
            type="decision",
            summary="Later repository decision",
            details="This was written second.",
        )
    )

    results = await postgres_store.get_recent_project_context(
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


@pytest.mark.asyncio
async def test_get_decisions_filters_decision_records(postgres_store: PostgresMemoryStore) -> None:
    await postgres_store.write_memory(sample_write_payload(type="note", summary="A note"))
    await postgres_store.write_memory(sample_write_payload(type="decision", summary="A decision"))

    results = await postgres_store.get_decisions(
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


@pytest.mark.asyncio
async def test_get_open_questions_filters_question_and_todo_records(postgres_store: PostgresMemoryStore) -> None:
    await postgres_store.write_memory(sample_write_payload(type="question", summary="Open question"))
    await postgres_store.write_memory(sample_write_payload(type="todo", summary="Open todo"))
    await postgres_store.write_memory(sample_write_payload(type="decision", summary="Closed decision"))

    results = await postgres_store.get_open_questions(
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


@pytest.mark.asyncio
async def test_redact_memory_updates_record_and_appends_audit_event(postgres_store: PostgresMemoryStore) -> None:
    record = await postgres_store.write_memory(
        sample_write_payload(
            type="note",
            summary="Sensitive note",
            details="Contains material that should be redacted.",
        )
    )

    redacted = await postgres_store.redact_memory(
        {
            "memory_id": record.memory_id,
            "redacted_by": "security-review",
            "reason": "Contains sensitive data",
        }
    )

    assert redacted.status.value == "redacted"
    assert redacted.details == "[REDACTED]"
    assert redacted.metadata["redacted_by"] == "security-review"

    events = await postgres_store.list_audit_events()
    assert len(events) == 2
    assert events[-1]["event_type"] == "memory_redacted"


@pytest.mark.asyncio
async def test_tool_handlers_expose_mcp_facing_results(postgres_store: PostgresMemoryStore) -> None:
    handlers = AsyncToolHandlers(postgres_store)

    created = await handlers.write_memory(sample_write_payload(summary="Handler write"))
    assert created["memory"]["summary"] == "Handler write"

    search = await handlers.search_memory(
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

    redacted = await handlers.redact_memory(
        {
            "memory_id": created["memory"]["memory_id"],
            "redacted_by": "handler-test",
            "reason": "test",
        }
    )
    assert redacted["memory"]["status"] == "redacted"


@pytest.mark.asyncio
async def test_upsert_fact_creates_and_updates_single_fact_record(postgres_store: PostgresMemoryStore) -> None:
    first = await postgres_store.upsert_fact(
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
    second = await postgres_store.upsert_fact(
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


@pytest.mark.asyncio
async def test_list_memories_by_repo_returns_filtered_records(postgres_store: PostgresMemoryStore) -> None:
    await postgres_store.write_memory(sample_write_payload(type="note", summary="Repo note"))
    await postgres_store.write_memory(sample_write_payload(type="decision", summary="Repo decision"))

    results = await postgres_store.list_memories_by_repo(
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


@pytest.mark.asyncio
async def test_handler_supports_upsert_fact_and_list_by_repo(postgres_store: PostgresMemoryStore) -> None:
    handlers = AsyncToolHandlers(postgres_store)

    fact = await handlers.upsert_fact(
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

    listed = await handlers.list_memories_by_repo(
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
