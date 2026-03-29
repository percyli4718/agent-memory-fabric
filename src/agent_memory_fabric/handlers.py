from __future__ import annotations

from typing import Any

from agent_memory_fabric.schema_loader import load_schema
from agent_memory_fabric.storage.base import MemoryStore


class ToolHandlers:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def search_memory(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("search-memory.request.schema.json")
        results = [record.to_dict() for record in self.store.search_memory(payload)]
        return {"results": results, "count": len(results)}

    def write_memory(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("write-memory.request.schema.json")
        record = self.store.write_memory(payload)
        return {"memory": record.to_dict()}

    def get_recent_project_context(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-recent-project-context.request.schema.json")
        results = [
            record.to_dict() for record in self.store.get_recent_project_context(payload)
        ]
        return {"results": results, "count": len(results)}

    def get_decisions(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-decisions.request.schema.json")
        results = [record.to_dict() for record in self.store.get_decisions(payload)]
        return {"results": results, "count": len(results)}

    def get_open_questions(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("get-open-questions.request.schema.json")
        results = [record.to_dict() for record in self.store.get_open_questions(payload)]
        return {"results": results, "count": len(results)}

    def redact_memory(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ = load_schema("redact-memory.request.schema.json")
        record = self.store.redact_memory(payload)
        return {"memory": record.to_dict()}
