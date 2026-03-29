from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class Scope(StrEnum):
    USER = "user"
    REPO = "repo"
    PROJECT = "project"
    TEAM = "team"
    ORG = "org"


class Visibility(StrEnum):
    PRIVATE = "private"
    TEAM = "team"
    ORG = "org"


class MemoryType(StrEnum):
    DECISION = "decision"
    BUGFIX = "bugfix"
    INCIDENT = "incident"
    NOTE = "note"
    TODO = "todo"
    QUESTION = "question"
    FACT = "fact"
    CONVENTION = "convention"
    SUMMARY = "summary"


class Status(StrEnum):
    ACTIVE = "active"
    REDACTED = "redacted"
    ARCHIVED = "archived"
    DELETED = "deleted"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class MemoryRecord:
    memory_id: str
    tenant: str
    project: str
    repository: str
    scope: Scope
    visibility: Visibility
    type: MemoryType
    summary: str
    author: str
    source: str
    status: Status
    created_at: str
    updated_at: str
    schema_version: str = "v0.1"
    details: str | None = None
    tags: list[str] = field(default_factory=list)
    source_ref: str | None = None
    checksum: str | None = None
    expires_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        tenant: str,
        project: str,
        repository: str,
        scope: str,
        visibility: str,
        type: str,
        summary: str,
        author: str,
        source: str,
        details: str | None = None,
        tags: list[str] | None = None,
        source_ref: str | None = None,
        expires_at: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "MemoryRecord":
        now = utc_now()
        return cls(
            memory_id=f"mem_{uuid4().hex}",
            tenant=tenant,
            project=project,
            repository=repository,
            scope=Scope(scope),
            visibility=Visibility(visibility),
            type=MemoryType(type),
            summary=summary,
            author=author,
            source=source,
            status=Status.ACTIVE,
            created_at=now,
            updated_at=now,
            details=details,
            tags=tags or [],
            source_ref=source_ref,
            expires_at=expires_at,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "tenant": self.tenant,
            "project": self.project,
            "repository": self.repository,
            "scope": self.scope.value,
            "visibility": self.visibility.value,
            "type": self.type.value,
            "summary": self.summary,
            "details": self.details,
            "tags": self.tags,
            "author": self.author,
            "source": self.source,
            "status": self.status.value,
            "source_ref": self.source_ref,
            "checksum": self.checksum,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "schema_version": self.schema_version,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryRecord":
        return cls(
            memory_id=data["memory_id"],
            tenant=data["tenant"],
            project=data["project"],
            repository=data["repository"],
            scope=Scope(data["scope"]),
            visibility=Visibility(data["visibility"]),
            type=MemoryType(data["type"]),
            summary=data["summary"],
            details=data.get("details"),
            tags=list(data.get("tags") or []),
            author=data["author"],
            source=data["source"],
            status=Status(data["status"]),
            source_ref=data.get("source_ref"),
            checksum=data.get("checksum"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            expires_at=data.get("expires_at"),
            schema_version=data["schema_version"],
            metadata=dict(data.get("metadata") or {}),
        )
