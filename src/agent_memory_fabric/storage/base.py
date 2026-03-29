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
