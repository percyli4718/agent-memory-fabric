from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from agent_memory_fabric.models import MemoryRecord, utc_now
from agent_memory_fabric.policy import (
    allowed_visibility_for_scopes,
    enforce_search_policy,
    enforce_write_policy,
)
from agent_memory_fabric.storage.base import MemoryStore
from agent_memory_fabric.validation import validate_payload


class SQLiteMemoryStore(MemoryStore):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_parent()
        self._init_db()

    def _ensure_parent(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
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
                    tags_json TEXT NOT NULL,
                    author TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source_ref TEXT,
                    checksum TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT,
                    schema_version TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    memory_id TEXT,
                    actor TEXT NOT NULL,
                    reason TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

    def write_memory(self, payload: dict) -> MemoryRecord:
        validate_payload("write-memory.request.schema.json", payload)
        enforce_write_policy(payload)
        record = MemoryRecord.create(**payload)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memory_records (
                    memory_id, tenant, project, repository, scope, visibility, type,
                    summary, details, tags_json, author, source, status, source_ref,
                    checksum, created_at, updated_at, expires_at, schema_version, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
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
                ),
            )
            self._append_audit_log(
                conn,
                event_type="memory_written",
                memory_id=record.memory_id,
                actor=record.author,
                reason=record.source,
            )
        return record

    def search_memory(self, payload: dict) -> list[MemoryRecord]:
        validate_payload("search-memory.request.schema.json", payload)
        enforce_search_policy(payload)
        query = payload["query"]
        limit = payload.get("limit", 10)
        types = payload.get("types") or []
        scopes = payload.get("scope") or []
        allowed_visibilities = allowed_visibility_for_scopes(scopes)

        sql = [
            """
            SELECT * FROM memory_records
            WHERE tenant = ?
              AND project = ?
              AND repository = ?
              AND status = 'active'
              AND (summary LIKE ? OR COALESCE(details, '') LIKE ?)
            """
        ]
        params: list[object] = [
            payload["tenant"],
            payload["project"],
            payload["repository"],
            f"%{query}%",
            f"%{query}%",
        ]

        if types:
            placeholders = ", ".join("?" for _ in types)
            sql.append(f"AND type IN ({placeholders})")
            params.extend(types)

        if scopes:
            placeholders = ", ".join("?" for _ in scopes)
            sql.append(f"AND scope IN ({placeholders})")
            params.extend(scopes)

        if allowed_visibilities:
            placeholders = ", ".join("?" for _ in allowed_visibilities)
            sql.append(f"AND visibility IN ({placeholders})")
            params.extend(allowed_visibilities)

        sql.append("ORDER BY updated_at DESC LIMIT ?")
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute("\n".join(sql), params).fetchall()
        return [self._row_to_record(row) for row in rows]

    def get_recent_project_context(self, payload: dict) -> list[MemoryRecord]:
        validate_payload("get-recent-project-context.request.schema.json", payload)
        enforce_search_policy(payload)
        return self._list_filtered_records(
            payload,
            limit=payload.get("limit", 10),
        )

    def get_decisions(self, payload: dict) -> list[MemoryRecord]:
        validate_payload("get-decisions.request.schema.json", payload)
        enforce_search_policy(payload)
        return self._list_filtered_records(
            payload,
            types=["decision"],
            limit=payload.get("limit", 10),
        )

    def get_open_questions(self, payload: dict) -> list[MemoryRecord]:
        validate_payload("get-open-questions.request.schema.json", payload)
        enforce_search_policy(payload)
        return self._list_filtered_records(
            payload,
            types=["question", "todo"],
            limit=payload.get("limit", 10),
        )

    def redact_memory(self, payload: dict) -> MemoryRecord:
        validate_payload("redact-memory.request.schema.json", payload)
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM memory_records
                WHERE memory_id = ?
                """,
                (payload["memory_id"],),
            ).fetchone()
            if row is None:
                raise ValueError(f"Memory not found: {payload['memory_id']}")

            conn.execute(
                """
                UPDATE memory_records
                SET details = ?, tags_json = ?, status = ?, updated_at = ?, metadata_json = ?
                WHERE memory_id = ?
                """,
                (
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
                ),
            )
            self._append_audit_log(
                conn,
                event_type="memory_redacted",
                memory_id=payload["memory_id"],
                actor=payload["redacted_by"],
                reason=payload["reason"],
            )
            updated = conn.execute(
                """
                SELECT * FROM memory_records
                WHERE memory_id = ?
                """,
                (payload["memory_id"],),
            ).fetchone()
        return self._row_to_record(updated)

    def _list_filtered_records(
        self,
        payload: dict,
        *,
        types: list[str] | None = None,
        limit: int,
    ) -> list[MemoryRecord]:
        scopes = payload["scope"]
        allowed_visibilities = allowed_visibility_for_scopes(scopes)
        sql = [
            """
            SELECT * FROM memory_records
            WHERE tenant = ?
              AND project = ?
              AND repository = ?
              AND status = 'active'
            """
        ]
        params: list[object] = [
            payload["tenant"],
            payload["project"],
            payload["repository"],
        ]

        placeholders = ", ".join("?" for _ in scopes)
        sql.append(f"AND scope IN ({placeholders})")
        params.extend(scopes)

        visibility_placeholders = ", ".join("?" for _ in allowed_visibilities)
        sql.append(f"AND visibility IN ({visibility_placeholders})")
        params.extend(allowed_visibilities)

        if types:
            type_placeholders = ", ".join("?" for _ in types)
            sql.append(f"AND type IN ({type_placeholders})")
            params.extend(types)

        sql.append("ORDER BY updated_at DESC LIMIT ?")
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute("\n".join(sql), params).fetchall()
        return [self._row_to_record(row) for row in rows]

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
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
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "expires_at": row["expires_at"],
                "schema_version": row["schema_version"],
                "metadata": json.loads(row["metadata_json"]),
            }
        )

    def _append_audit_log(
        self,
        conn: sqlite3.Connection,
        *,
        event_type: str,
        memory_id: str | None,
        actor: str,
        reason: str | None,
    ) -> None:
        from datetime import datetime, timezone

        conn.execute(
            """
            INSERT INTO audit_log (event_type, memory_id, actor, reason, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event_type,
                memory_id,
                actor,
                reason,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    def list_audit_events(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT audit_id, event_type, memory_id, actor, reason, created_at
                FROM audit_log
                ORDER BY audit_id ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]
