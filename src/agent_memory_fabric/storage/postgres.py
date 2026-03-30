"""PostgreSQL storage backend for Agent Memory Fabric."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import asyncpg

from agent_memory_fabric.models import MemoryRecord, utc_now
from agent_memory_fabric.policy import (
    allowed_visibility_for_scopes,
    enforce_search_policy,
    enforce_write_policy,
)
from agent_memory_fabric.storage.base import MemoryStore
from agent_memory_fabric.validation import validate_payload


class PostgresMemoryStore(MemoryStore):
    """Async PostgreSQL storage adapter mirroring SQLite interface."""

    def __init__(self, dsn: str, pool_size: int = 10) -> None:
        self.dsn = dsn
        self._pool_size = pool_size
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=self.dsn,
                max_size=self._pool_size,
                min_size=2,
            )
        return self._pool

    async def _init_db(self) -> None:
        """Initialize database tables."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    memory_id TEXT PRIMARY KEY,
                    tenant TEXT NOT NULL,
                    project TEXT NOT NULL,
                    repository TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    visibility TEXT NOT NULL,
                    type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    details TEXT,
                    tags_json JSONB NOT NULL DEFAULT '[]',
                    author TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source_ref TEXT,
                    checksum TEXT,
                    created_at TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL,
                    expires_at TIMESTAMPTZ,
                    schema_version TEXT NOT NULL,
                    metadata_json JSONB NOT NULL DEFAULT '{}'
                )
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    audit_id SERIAL PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    memory_id TEXT,
                    actor TEXT NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )

    async def write_memory(self, payload: dict) -> MemoryRecord:
        """Write a memory record to the database."""
        validate_payload("write-memory.request.schema.json", payload)
        enforce_write_policy(payload)
        record = MemoryRecord.create(**payload)

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO memory_records (
                    memory_id, tenant, project, repository, scope, visibility, type,
                    summary, details, tags_json, author, source, status, source_ref,
                    checksum, created_at, updated_at, expires_at, schema_version, metadata_json
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                """,
                record.memory_id,
                record.tenant,
                record.project,
                record.repository,
                record.scope.value,
                record.visibility.value,
                record.type.value,
                record.summary,
                record.details,
                json.dumps(record.tags),
                record.author,
                record.source,
                record.status.value,
                record.source_ref,
                record.checksum,
                record.created_at,
                record.updated_at,
                record.expires_at,
                record.schema_version,
                json.dumps(record.metadata),
            )
            await self._append_audit_log(
                conn,
                event_type="memory_written",
                memory_id=record.memory_id,
                actor=record.author,
                reason=record.source,
            )
        return record

    async def search_memory(self, payload: dict) -> list[MemoryRecord]:
        """Search memory records."""
        validate_payload("search-memory.request.schema.json", payload)
        enforce_search_policy(payload)
        query = payload["query"]
        limit = payload.get("limit", 10)
        types = payload.get("types") or []
        scopes = payload.get("scope") or []
        allowed_visibilities = allowed_visibility_for_scopes(scopes)

        sql = """
            SELECT * FROM memory_records
            WHERE tenant = $1
              AND project = $2
              AND repository = $3
              AND status = 'active'
              AND (summary LIKE $4 OR COALESCE(details, '') LIKE $5)
        """
        params: list[Any] = [
            payload["tenant"],
            payload["project"],
            payload["repository"],
            f"%{query}%",
            f"%{query}%",
        ]

        if types:
            placeholders = ", ".join(f"${i}" for i in range(len(params) + 1, len(params) + 1 + len(types)))
            sql += f" AND type IN ({placeholders})"
            params.extend(types)

        if scopes:
            placeholders = ", ".join(f"${i}" for i in range(len(params) + 1, len(params) + 1 + len(scopes)))
            sql += f" AND scope IN ({placeholders})"
            params.extend(scopes)

        if allowed_visibilities:
            placeholders = ", ".join(f"${i}" for i in range(len(params) + 1, len(params) + 1 + len(allowed_visibilities)))
            sql += f" AND visibility IN ({placeholders})"
            params.extend(allowed_visibilities)

        sql += " ORDER BY updated_at DESC LIMIT $" + str(len(params) + 1)
        params.append(limit)

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        return [self._row_to_record(row) for row in rows]

    async def get_recent_project_context(self, payload: dict) -> list[MemoryRecord]:
        """Get recent project context records."""
        validate_payload("get-recent-project-context.request.schema.json", payload)
        enforce_search_policy(payload)
        return await self._list_filtered_records(
            payload,
            limit=payload.get("limit", 10),
        )

    async def get_decisions(self, payload: dict) -> list[MemoryRecord]:
        """Get decision records."""
        validate_payload("get-decisions.request.schema.json", payload)
        enforce_search_policy(payload)
        return await self._list_filtered_records(
            payload,
            types=["decision"],
            limit=payload.get("limit", 10),
        )

    async def get_open_questions(self, payload: dict) -> list[MemoryRecord]:
        """Get open question records."""
        validate_payload("get-open-questions.request.schema.json", payload)
        enforce_search_policy(payload)
        return await self._list_filtered_records(
            payload,
            types=["question", "todo"],
            limit=payload.get("limit", 10),
        )

    async def redact_memory(self, payload: dict) -> MemoryRecord:
        """Redact a memory record."""
        validate_payload("redact-memory.request.schema.json", payload)
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM memory_records
                WHERE memory_id = $1
                """,
                payload["memory_id"],
            )
            if row is None:
                raise ValueError(f"Memory not found: {payload['memory_id']}")

            await conn.execute(
                """
                UPDATE memory_records
                SET details = $1, tags_json = $2, status = $3, updated_at = $4, metadata_json = $5
                WHERE memory_id = $6
                """,
                "[REDACTED]",
                json.dumps([]),
                "redacted",
                utc_now(),
                json.dumps(
                    {
                        **json.loads(row["metadata_json"]),
                        "redaction_reason": payload["reason"],
                        "redacted_by": payload["redacted_by"],
                    }
                ),
                payload["memory_id"],
            )
            await self._append_audit_log(
                conn,
                event_type="memory_redacted",
                memory_id=payload["memory_id"],
                actor=payload["redacted_by"],
                reason=payload["reason"],
            )
            updated = await conn.fetchrow(
                """
                SELECT * FROM memory_records
                WHERE memory_id = $1
                """,
                (payload["memory_id"],),
            )
        return self._row_to_record(updated)

    async def upsert_fact(self, payload: dict) -> MemoryRecord:
        """Upsert a fact record."""
        validate_payload("upsert-fact.request.schema.json", payload)
        enforce_write_policy(payload)
        summary = payload.get("summary") or f"Fact: {payload['fact_key']}"
        details = payload["fact_value"]
        metadata = {
            **dict(payload.get("metadata") or {}),
            "fact_key": payload["fact_key"],
            "fact_value": payload["fact_value"],
        }

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM memory_records
                WHERE tenant = $1
                  AND project = $2
                  AND repository = $3
                  AND scope = $4
                  AND type = 'fact'
                """,
                payload["tenant"],
                payload["project"],
                payload["repository"],
                payload["scope"],
            )

            existing = None
            for candidate in rows:
                candidate_metadata = json.loads(candidate["metadata_json"])
                if candidate_metadata.get("fact_key") == payload["fact_key"]:
                    existing = candidate
                    break

            if existing is None:
                record = MemoryRecord.create(
                    tenant=payload["tenant"],
                    project=payload["project"],
                    repository=payload["repository"],
                    scope=payload["scope"],
                    visibility=payload["visibility"],
                    type="fact",
                    summary=summary,
                    author=payload["author"],
                    source=payload["source"],
                    details=details,
                    tags=list(payload.get("tags") or []),
                    source_ref=payload.get("source_ref"),
                    metadata=metadata,
                )
                await conn.execute(
                    """
                    INSERT INTO memory_records (
                        memory_id, tenant, project, repository, scope, visibility, type,
                        summary, details, tags_json, author, source, status, source_ref,
                        checksum, created_at, updated_at, expires_at, schema_version, metadata_json
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                    """,
                    record.memory_id,
                    record.tenant,
                    record.project,
                    record.repository,
                    record.scope.value,
                    record.visibility.value,
                    record.type.value,
                    record.summary,
                    record.details,
                    json.dumps(record.tags),
                    record.author,
                    record.source,
                    record.status.value,
                    record.source_ref,
                    record.checksum,
                    record.created_at,
                    record.updated_at,
                    record.expires_at,
                    record.schema_version,
                    json.dumps(record.metadata),
                )
                await self._append_audit_log(
                    conn,
                    event_type="fact_upserted",
                    memory_id=record.memory_id,
                    actor=record.author,
                    reason=payload["fact_key"],
                )
                return record

            await conn.execute(
                """
                UPDATE memory_records
                SET visibility = $1, summary = $2, details = $3, tags_json = $4, author = $5,
                    source = $6, source_ref = $7, updated_at = $8, metadata_json = $9
                WHERE memory_id = $10
                """,
                payload["visibility"],
                summary,
                details,
                json.dumps(list(payload.get("tags") or [])),
                payload["author"],
                payload["source"],
                payload.get("source_ref"),
                utc_now(),
                json.dumps(metadata),
                existing["memory_id"],
            )
            await self._append_audit_log(
                conn,
                event_type="fact_upserted",
                memory_id=existing["memory_id"],
                actor=payload["author"],
                reason=payload["fact_key"],
            )
            updated = await conn.fetchrow(
                "SELECT * FROM memory_records WHERE memory_id = $1",
                existing["memory_id"],
            )
        return self._row_to_record(updated)

    async def list_memories_by_repo(self, payload: dict) -> list[MemoryRecord]:
        """List memories by repository."""
        validate_payload("list-memories-by-repo.request.schema.json", payload)
        enforce_search_policy(payload)
        return await self._list_filtered_records(
            payload,
            types=payload.get("types"),
            limit=payload.get("limit", 10),
        )

    async def _list_filtered_records(
        self,
        payload: dict,
        *,
        types: list[str] | None = None,
        limit: int,
    ) -> list[MemoryRecord]:
        """List filtered memory records."""
        scopes = payload["scope"]
        allowed_visibilities = allowed_visibility_for_scopes(scopes)
        sql = """
            SELECT * FROM memory_records
            WHERE tenant = $1
              AND project = $2
              AND repository = $3
              AND status = 'active'
        """
        params: list[Any] = [
            payload["tenant"],
            payload["project"],
            payload["repository"],
        ]

        placeholders = ", ".join(f"${i}" for i in range(len(params) + 1, len(params) + 1 + len(scopes)))
        sql += f" AND scope IN ({placeholders})"
        params.extend(scopes)

        visibility_placeholders = ", ".join(f"${i}" for i in range(len(params) + 1, len(params) + 1 + len(allowed_visibilities)))
        sql += f" AND visibility IN ({visibility_placeholders})"
        params.extend(allowed_visibilities)

        if types:
            type_placeholders = ", ".join(f"${i}" for i in range(len(params) + 1, len(params) + 1 + len(types)))
            sql += f" AND type IN ({type_placeholders})"
            params.extend(types)

        sql += " ORDER BY updated_at DESC LIMIT $" + str(len(params) + 1)
        params.append(limit)

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        return [self._row_to_record(row) for row in rows]

    def _row_to_record(self, row: asyncpg.Record) -> MemoryRecord:
        """Convert a database row to a MemoryRecord."""
        return MemoryRecord.from_dict(
            {
                "memory_id": row["memory_id"],
                "tenant": row["tenant"],
                "project": row["project"],
                "repository": row["repository"],
                "scope": row["scope"],
                "visibility": row["visibility"],
                "type": row["type"],
                "summary": row["summary"],
                "details": row["details"],
                "tags": json.loads(row["tags_json"]),
                "author": row["author"],
                "source": row["source"],
                "status": row["status"],
                "source_ref": row["source_ref"],
                "checksum": row["checksum"],
                "created_at": row["created_at"].isoformat(),
                "updated_at": row["updated_at"].isoformat(),
                "expires_at": row["expires_at"].isoformat() if row["expires_at"] else None,
                "schema_version": row["schema_version"],
                "metadata": json.loads(row["metadata_json"]),
            }
        )

    async def _append_audit_log(
        self,
        conn: asyncpg.Connection,
        *,
        event_type: str,
        memory_id: str | None,
        actor: str,
        reason: str | None,
    ) -> None:
        """Append an entry to the audit log."""
        await conn.execute(
            """
            INSERT INTO audit_log (event_type, memory_id, actor, reason, created_at)
            VALUES ($1, $2, $3, $4, $5)
            """,
            event_type,
            memory_id,
            actor,
            reason,
            datetime.now(timezone.utc).isoformat(),
        )

    async def list_audit_events(self) -> list[dict]:
        """List all audit events."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT audit_id, event_type, memory_id, actor, reason, created_at
                FROM audit_log
                ORDER BY audit_id ASC
                """
            )
        return [dict(row) for row in rows]

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool is not None:
            await self._pool.close()
