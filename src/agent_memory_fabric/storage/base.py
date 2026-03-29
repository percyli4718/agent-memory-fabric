from __future__ import annotations

from abc import ABC, abstractmethod

from agent_memory_fabric.models import MemoryRecord


class MemoryStore(ABC):
    @abstractmethod
    def write_memory(self, payload: dict) -> MemoryRecord:
        raise NotImplementedError

    @abstractmethod
    def search_memory(self, payload: dict) -> list[MemoryRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_recent_project_context(self, payload: dict) -> list[MemoryRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_decisions(self, payload: dict) -> list[MemoryRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_open_questions(self, payload: dict) -> list[MemoryRecord]:
        raise NotImplementedError

    @abstractmethod
    def redact_memory(self, payload: dict) -> MemoryRecord:
        raise NotImplementedError

    @abstractmethod
    def upsert_fact(self, payload: dict) -> MemoryRecord:
        raise NotImplementedError

    @abstractmethod
    def list_memories_by_repo(self, payload: dict) -> list[MemoryRecord]:
        raise NotImplementedError
